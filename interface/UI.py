from db.Entry import Entry
from hashlib import sha256
import os
from typing import Any, Dict, List, Optional
from db.Database import Database
from db.General import General
from interface.Logging import Logging


class UI:
    """
        main User Interface handling all communication with user
        also handles loaded database object
    """

    # database instance storing and handling all current database information
    database: Database

    # general instance storing general info about the app
    general: General

    # path/to user storage where all databases are stored
    user_storage_location = 'db/user_storage'

    # general.json here
    database_location = 'db'

    # list of all database names
    database_names: List[str]

    # list of all availible commands
    # each command corresponds to a method in UI
    # command-name: {
    #   description: short description of command
    #   method: method in UI corresponding to command
    # }
    commands: Dict[str, Dict[str, Any]]

    def __init__(self) -> None:
        self.commands = self.get_commands()
        self.database_names = self.get_database_names()

        # load general info
        self.general = General()
        self.general.load(self.database_location)

    def process(self, args: Optional[List[str]]) -> None:
        """
            starts whole application
            given no arguments, switches to self.start
            else finds correspoding method and executes
        """

        # application start text
        Logging.print("Password Manager")
        Logging.print("type 'exit' to exit the application any time.")
        Logging.print("use 'main.py help' to list the availible commands.")
        
        # if no args given, switch to self.start
        if args is None or args == []:
            self.start(loaded_db=False)
            return

        # always len(command) == 1
        # end application if no such command found
        command = args.pop(0)
        if command not in self.commands.keys() or len(args) > 0:
            Logging.print(f'Unrecognized command: {command}. \nAvailible commands\n: {self.commands_str()}')
            return

        # execute corresponding method
        self.commands[command]['method']()


    # MAIN METHODS FOR COMMANDS

    def start(self, loaded_db: bool) -> None:
        """
            default start to application
            starts if no command given
        """

        # sometimes self.database already loaded and ready to use
        # load database only if necessary
        if not loaded_db:
            # get name of database
            # last used database stored in self.general
            if self.general.last_db_used != '':
                # use that if stored
                self.database = self.get_database(self.general.last_db_used)
            else:
                # is not saved, get new name of database
                database_name = self.get_database_name()
                if database_name is None:
                    return

                self.database = self.get_database(database_name)

            Logging.print(f'\nSelecting database: {self.database.name}\n')

            # load password
            password = self.get_master_password()

            # unlock database
            self.database.unlock(password)

        # save db as last used
        self.general.change_last_db_used(self.database.name)
        
        # print database
        database_str = str(self.database)
        if database_str == '':
            Logging.print('No entries found. Use "add-entry" to add a new entry.')
            return
        Logging.print('\n' + database_str)

    def change_database(self) -> None:
        """
            switches database to use
            app default loads last used database
            command: 'change-db'
        """

        # get database name
        database_name = self.get_database_name()
        if database_name is None:
            return

        # save it to last used database
        self.general.change_last_db_used(database_name)
        # start app without loaded database
        self.start(False)

    def create_database(self) -> None:
        """
            creates new database and saves to new file
            command: 'create-db'
        """

        # get unique database name
        database_name = Logging.input('Please enter the name of the new database.')
        while database_name in self.database_names:
            database_name = Logging.input(f'Database {database_name} already exists. Please use a different name. Existing databases:\n{", ".join(self.database_names)}')

        # get new master password
        master_password = Logging.input('Choose master password.')
        
        database = Database()
        # second half of sha256(master_password) serves as validity check
        database.master_pass_sha256 = sha256(master_password.encode('utf-8')).hexdigest()[32:]
        database.db_file_location = f'{self.user_storage_location}/{database_name}.json'
        # save to file
        database.save()
        
        # save last db used
        self.general.change_last_db_used(database_name)

        Logging.print(f'Succesfuly created database {database_name}.')

    def delete_database(self) -> None:
        """
            deletes an existing database, given correct password
            command: 'del-db'
        """
        
        # get database name
        database_name = self.get_database_name()
        if database_name is None:
            return

        # load database
        self.database = self.get_database(database_name)

        # get master key
        master_key = self.get_master_key()

        # unlock database
        self.database.unlock(master_key)

        # ask again to assure user
        if not Logging.yes_no(f'Are you sure you want to delete database "{database_name}" ?'):
            return

        # remove the file
        os.remove(f'{self.user_storage_location}/{database_name}.json')

        Logging.print(f'Succesfuly removed database "{database_name}".')

    def create_entry(self) -> None:
        """
            creates new entry and adds to database
            command: 'add-entry'
        """
        
        # get master key
        master_key = self.start_entry()

        # get entry title
        entry_title = self.new_entry_title(self.database.entry_titles())

        # ask for properties
        entry = Entry()
        entry.title = entry_title
        # entry properties to ask for stored in Entry class
        entry_properties = self.entry_property_log_messages().items()
        for entry_property_name, entry_property_msg  in entry_properties:
            # get property value
            entry_property_value = Logging.input(entry_property_msg)
            # store to Entry instance
            setattr(entry, entry_property_name, entry_property_value)
        
        # generate new password
        password = Database.generate_password()
        Logging.print(f'Generated password: {password}')
        setattr(entry, 'password_decrypted', password)

        # encrypt password
        entry.encrypt(master_key)

        # add entry to database
        self.database.add_entry(entry)

        Logging.print(f'Succesfuly added entry: "{entry_title}"')

        # start application with already loaded database
        self.start(True)

    def delete_entry(self) -> None:
        """
            deletes an entry from given database
            command: 'del-entry'
        """
        
        # loads and unlocks database
        self.start_entry()

        # select which entry to delete
        
        # get all entry titles
        entry_titles = self.database.entry_titles()

        if entry_titles == []:
            # if no entries in database
            Logging.print('No entries found. Use "add-entry" to add an entry.')
            return

        # ask which entry to use
        entry_title = Logging.input(f'Which entry do you wish to delete?\n{", ".join(entry_titles)}')
        while entry_title not in entry_titles:
            # if no matching entry title
            entry_title = Logging.input(f'No such known entry. Please select one of the following:\n{entry_titles}')

        # reassure user
        if not Logging.yes_no(f'Are you sure you want to delete entry "{entry_title}" ?'):
            return

        # delete from database
        self.database.del_entry(entry_title)

        Logging.print(f'Succesfuly deleted entry {entry_title}')

    def change_entry(self) -> None:
        """
            edits an entry in database
            command: 'edit-entry'
        """

        # loads and unlocks database
        self.start_entry()

        # get entry which user wants to edit

        # all entry ttiles
        entry_titles = self.database.entry_titles()

        if entry_titles == []:
            # if no entries in database
            Logging.print('No entries found. Use "add-entry" to add an entry.')
            return

        # select entry title from entry_titles to edit
        entry_title = Logging.input(f'Which entry do you wish to edit?\n{", ".join(entry_titles)}')
        while entry_title not in entry_titles:
            # if no such entry title found
            entry_title = Logging.input(f'No such known entry. Please select one of the following:\n{entry_titles}')

        # get entry from self.database by title (entries have unique titles)
        entry = self.database.entry_by_title(entry_title)

        # print all entry properties, except password_decrypted and password_encrypted
        entry_properties = self.entry_property_log_messages().items()
        for entry_property_name, entry_property_msg  in entry_properties:
            if entry_property_name in ['password_encrypted', 'password_decrypted']:
                continue

            # get new value for entry
            entry_property_value = Logging.input(entry_property_msg)
            if entry_property_value != '':
                # change entry value only if given string is not empty
                setattr(entry, entry_property_name, entry_property_value)

        # save database
        self.database.save()

        Logging.print(f'Succesfuly edited entry {entry_title}')

    def help(self) -> None:
        """
            lists all availible commands
            command: 'help'
        """

        Logging.print('Availible commands: \n' + self.commands_str())

    # UTILITY METHODS

    def start_entry(self) -> Optional[str]:
        """
            shortcut for entry methods
            loads and unlocks database to verify user
            some code same in create_entry, delete_entry, change_entry
            returns master_key, though it is not always needed
        """
        
        # get database name
        database_name = self.get_database_name()
        if database_name is None:
            return

        # load database
        self.database = self.get_database(database_name)

        # get master key
        master_key = self.get_master_key()

        # unlock database
        self.database.unlock(master_key)

        return master_key

    def entry_property_log_messages(self) -> Dict[str, str]:
        """
            returns log messages for entry properties
        """
        # return Dict[entry_property: logMessage]
        return {
            'user_name': 'Optional: User name',
            'url': 'Optional: URL',
            'notes': 'Optional: Notes',
        }

    def get_database_name(self) -> Optional[str]:
        """gets database name from user which is to be used"""

        if self.database_names == []:
            # if no database stored
            Logging.print(f'No database found. Use the command "create-db" to create a new database')
            return

        # get database name from user
        database_name = Logging.input(f'\nSelect a database. \n {", ".join(self.database_names)}')
        while database_name not in self.database_names:
            # if no such database name found
            database_name = Logging.input(f'\nDatabase {database_name} not found. Please select one. \n {", ".join(self.database_names)}')

        return database_name

    def new_entry_title(self, entry_titles_in_use: List[str]) -> str:
        """gets new unique entry title from user """

        # get entry title
        entry_title = Logging.input('Entry title:')
        while entry_title in entry_titles_in_use:
            # if already such title in use
            entry_title = Logging.input(
                f"Entry title '{entry_title}' is already saved. \nEntry titles in use: {', '.join(entry_titles_in_use)}\nUse 'del-entry' to delete an entry.")

        return entry_title

    def get_database(self, database_name: str) -> Database:
        """return Database instance given /path/to file"""
        return Database.from_file(f'{self.user_storage_location}/{database_name}.json')

    def get_master_password(self) -> str:
        """gets master password from user"""

        # get password
        password = Logging.input('Please enter password:')
        while not self.database.password_correct(password):
            # if password is not matching stored hash in database
            password = Logging.input('Incorrect password, please reenter:')

        return password

    def get_master_key(self) -> str:
        """
            returns master key from master password
            first half of sha256 hash of master password used as key
        """

        # get password from user
        master_password = self.get_master_password()
        # return sha hex of password
        return sha256(master_password.encode('utf-8')).hexdigest()[:32]

    def get_database_names(self) -> List[str]:
        """returns all availible databases in user_storage"""
        
        # get database names
        databases = os.listdir(self.user_storage_location)
        # return them without .json suffix
        return [database.rstrip('.json') for database in databases]

    def get_commands(self) -> Dict[str, Dict[str, Any]]:
        """returns dict containing all information about availible commands in app"""
        
        return {
            # changes database to use
            'change-db': {
                'description': 'Change database',
                'method': self.change_database,
            },
            # creates new database
            'create-db': {
                'description': 'Create a new database',
                'method': self.create_database,
            },
            # deletes an existing database
            'del-db': {
                'description': 'Delete a existing database',
                'method': self.delete_database,
            },
            # edits an entry in a given database
            'edit-entry': {
                'description': 'Edit a existing entry in a database',
                'method': self.change_entry,
            },
            'add-entry': {
                'description': 'Create a new entry in a database',
                'method': self.create_entry,
            },
            'del-entry': {
                'description': 'Delete an entry in a database',
                'method': self.delete_entry,
            },
            'help': {
                'description': 'Show all availible commands',
                'method': self.help,
            }
        }

    def commands_str(self) -> str:
        """returns string of 'command-name' - 'description' """
        commands = self.get_commands()
        return "\n".join([f'{key} - {commands[key]["description"]}' for key in commands.keys() if key != 'help'])