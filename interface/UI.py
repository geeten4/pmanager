from db.Entry import Entry
from hashlib import sha256
import os
from typing import Any, Dict, List, Optional
from db.Database import Database
from db.General import General
from interface.Logging import Logging


class UI:

    database: Database
    general: General
    user_storage_location = 'db/user_storage'
    database_location = 'db'
    database_names: List[str]
    commands: Dict[str, Dict[str, Any]]

    def __init__(self) -> None:
        self.commands = self.get_commands()
        self.database_names = self.get_database_names()

        # load general info
        self.general = General()
        self.general.load(self.database_location)

    # starts whole application
    def process(self, args: Optional[List[str]]) -> None:
        Logging.print("Password Manager")
        Logging.print("type 'exit' to exit the application any time.")
        Logging.print("use 'main.py help' to list the availible commands.")
        if args is None or args == []:
            self.start(loaded_db=False)
            return

        command = args.pop(0)
        if command not in self.commands.keys():
            Logging.print(f'Unrecognized command: {command}. \nAvailible commands\n: {self.commands_str()}')
            return

        self.commands[command]['method']()

    # MAIN METHODS

    def start(self, loaded_db: bool) -> None:

        if not loaded_db:
            # load database
            if self.general.last_db_used != '':
                # if is last db used save
                self.database = self.get_database(self.general.last_db_used)
            else:
                # is not saved, get new one
                database_name = self.get_database_name()
                if database_name is None:
                    return

                self.database = self.get_database(database_name)

            Logging.print(f'\nSelecting database: {self.database.name}\n')

            # load password
            password = self.get_master_password()

            # unlock and Logging.print database
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
        database_name = self.get_database_name()
        if database_name is None:
            return

        self.general.change_last_db_used(database_name)
        self.start(False)

    def create_database(self) -> None:
        database_name = Logging.input('Please enter the name of the new database.')
        while database_name in self.database_names:
            database_name = Logging.input(f'Database {database_name} already exists. Please use a different name. Existing databases:\n{", ".join(self.database_names)}')

        # get master password
        master_password = Logging.input('Choose master password.')

        # save to file
        database = Database()
        database.master_pass_sha256 = sha256(master_password.encode('utf-8')).hexdigest()[32:]
        database.db_file_location = f'{self.user_storage_location}/{database_name}.json'
        database.save()
        
        # save last db used
        self.general.change_last_db_used(database_name)

        Logging.print(f'Succesfuly created database {database_name}.')

    def delete_database(self) -> None:
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

        if not Logging.yes_no(f'Are you sure you want to delete database "{database_name}" ?'):
            return
        
        os.remove(f'{self.user_storage_location}/{database_name}.json')

        Logging.print(f'Succesfuly removed database "{database_name}".')

    def create_entry(self) -> None:
        master_key = self.start_entry()

        # get entry title
        entry_title = self.new_entry_title(self.database.entry_titles())

        # ask for properties
        entry = Entry()
        entry.title = entry_title
        entry_properties = self.entry_property_log_messages().items()
        for entry_property_name, entry_property_msg  in entry_properties:
            entry_property_value = Logging.input(entry_property_msg)
            setattr(entry, entry_property_name, entry_property_value)
        
        # generate password
        password = Database.generate_password()
        Logging.print(f'Generated password: {password}')
        setattr(entry, 'password_decrypted', password)

        # encrypt password
        entry.encrypt(master_key)

        # add entry to database
        self.database.add_entry(entry)

        Logging.print(f'Succesfuly added entry: "{entry_title}"')

        # start application
        self.start(True)

    def delete_entry(self) -> None:
        self.start_entry()

        entry_titles = self.database.entry_titles()

        if entry_titles == []:
            Logging.print('No entries found. Use "add-entry" to add an entry.')
            return

        entry_title = Logging.input(f'Which entry do you wish to delete?\n{", ".join(entry_titles)}')
        while entry_title not in entry_titles:
            entry_title = Logging.input(f'No such known entry. Please select one of the following:\n{entry_titles}')

        if not Logging.yes_no(f'Are you sure you want to delete entry "{entry_title}" ?'):
            return

        # delete from database
        self.database.del_entry(entry_title)

        Logging.print(f'Succesfuly deleted entry {entry_title}')

    def change_entry(self) -> None:
        self.start_entry()

        entry_titles = self.database.entry_titles()

        if entry_titles == []:
            Logging.print('No entries found. Use "add-entry" to add an entry.')
            return

        entry_title = Logging.input(f'Which entry do you wish to edit?\n{", ".join(entry_titles)}')
        while entry_title not in entry_titles:
            entry_title = Logging.input(f'No such known entry. Please select one of the following:\n{entry_titles}')

        entry = self.database.entry_by_title(entry_title)

        entry_properties = self.entry_property_log_messages().items()
        for entry_property_name, entry_property_msg  in entry_properties:
            if entry_property_name in ['password_encrypted', 'password_decrypted']:
                continue
            entry_property_value = Logging.input(entry_property_msg)
            if entry_property_value != '':
                setattr(entry, entry_property_name, entry_property_value)

        self.database.save()

        Logging.print(f'Succesfuly edited entry {entry_title}')

    def help(self) -> None:
        Logging.print('Availible commands: \n' + self.commands_str())

    # UTILITY METHODS

    def start_entry(self) -> Optional[str]:
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
        # return Dict[entry_property: logMessage]
        return {
            'user_name': 'Optional: User name',
            'url': 'Optional: URL',
            'notes': 'Optional: Notes',
        }

    def get_database_name(self) -> Optional[str]:
        if self.database_names == []:
            Logging.print(f'No database found. Use the command "create-db" to create a new database')
            return

        database_name = Logging.input(f'\nSelect a database. \n {", ".join(self.database_names)}')
        while database_name not in self.database_names:
            database_name = Logging.input(f'\nDatabase {database_name} not found. Please select one. \n {", ".join(self.database_names)}')

        return database_name

    def get_entry_title(self) -> str:
        pass

    def new_entry_title(self, entry_titles_in_use: List[str]) -> str:
        entry_title = Logging.input('Entry title:')
        while entry_title in entry_titles_in_use:
            entry_title = Logging.input(
                f"Entry title '{entry_title}' is already saved. \nEntry titles in use: {', '.join(entry_titles_in_use)}\nUse 'del-entry' to delete an entry.")
        return entry_title

    def get_database(self, database_name: str) -> Database:
        return Database.from_file(f'{self.user_storage_location}/{database_name}.json')

    def get_master_password(self) -> str:
        password = Logging.input('Please enter password:')
        while not self.database.password_correct(password):
            password = Logging.input('Incorrect password, please reenter:')

        return password

    def get_master_key(self) -> str:
        master_password = self.get_master_password()
        return sha256(master_password.encode('utf-8')).hexdigest()[:32]

    def get_database_names(self) -> List[str]:
        databases = os.listdir('db/user_storage')
        return [database.rstrip('.json') for database in databases]

    def get_commands(self) -> Dict[str, Dict[str, Any]]:
        return {
            'change-db': {
                'description': 'Change database',
                'method': self.change_database,
            },
            'create-db': {
                'description': 'Create a new database',
                'method': self.create_database,
            },
            'del-db': {
                'description': 'Delete a existing database',
                'method': self.delete_database,
            },
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
        commands = self.get_commands()
        return "\n".join([f'{key} - {commands[key]["description"]}' for key in commands.keys() if key != 'help'])