from interface.Logging import Logging
import secrets
from typing import List, Optional
from db.Entry import Entry
from hashlib import sha256
import json

# save hash of master password to validate before unlocking

class Database:

    """
        manages user databases
        each database contains List[Entry] which stores all important information
    """

    # holds all entries in the database
    entries: List[Entry] = []
    # second half of master key sha256 hash used as validation when unlocking db
    master_pass_sha256: str
    # location of database file
    db_file_location: str
    # database name
    name: str

    @staticmethod
    def from_file(db_file_location: str):
        """loads database given file location"""

        database = Database()
        database.db_file_location = db_file_location
        # use file name as database name
        database.name = db_file_location.split('/')[-1].rstrip('.json')
        database.load()
        return database

    @staticmethod
    def generate_password() -> str:
        """generates random 32 long hex string"""

        return secrets.token_hex(16)

    def del_entry(self, entry_title: str) -> None:
        """deletes an entry from self.entries and saves the database"""
        self.entries = [entry for entry in self.entries if entry.title != entry_title]
        self.save()

    def add_entry(self, entry: Entry) -> None:
        """adds an entry to self.entries and saves the database"""
        self.entries.append(entry)
        self.save()
    
    def save(self) -> None:
        """
            saves database to original file
            if no such file exists, creates new one
            save master_password and all entries
            entries handle themselves what to save 
        """
        with open(self.db_file_location, 'w') as db_file:
            json.dump({
                'master_password': {
                    'sha256': self.master_pass_sha256,
                },
                'entries': [entry.to_dict() for entry in self.entries],
            }, db_file)

    def load(self) -> None:
        """
            loads database from file given file location string
            self.db_file_location must be set
        """

        # load the file
        db = json.load(open(self.db_file_location))

        # load sha hash of master password
        self.master_pass_sha256 = db['master_password']['sha256']

        # load all entries
        entries_json = db['entries']
        entries: List[Entry] = []

        # from all json entries create Entry instances and add them to self.entries
        for entry_json in entries_json:
            entry = Entry()

            for attribute in entry_json:
                # set all attributes stored in entry_json
                setattr(entry, attribute, entry_json[attribute])
            
            entries.append(entry)
        
        self.entries = entries

    def unlock(self, master_password: str) -> None:
        """unlocks loaded database given a master password"""

        # master password should already be checked for validity
        # here just return None if incorrect
        if not self.password_correct(master_password):
            Logging.print('Password incorrect, exiting.')
            return

        # first half of master password serves as key for all entries
        master_password_hash = sha256(master_password.encode('utf-8')).hexdigest()[:32]

        # decrypt each entry given master password
        for entry in self.entries:
            entry.decrypt(master_password_hash)

    def password_correct(self, password: str) -> bool:
        """return True if second part of sha256 of password matches saved hash in database"""

        # second half of master password hash serves for validating
        password_hash = sha256(password.encode('utf-8')).hexdigest()[32:]
        return self.master_pass_sha256 == password_hash

    def entry_titles(self) -> List[str]:
        """returns List[str] of all entry titles"""
        return [entry.title for entry in self.entries]

    def entry_by_title(self, entry_title: str) -> Optional[Entry]:
        """
            returns an entry by given title
            entries must have unique titles
            return None if no such entry title found
        """
        entries = [entry for entry in self.entries if entry.title == entry_title]
        if entries == []:
            Logging.print('No such entry found.')
            return
        return entries[0] 

    def __str__(self) -> str:
        """database string printed in the app"""
        return f'*** DATABASE {self.name} ***\n\n ' + '\n\n'.join([str(entry) for entry in self.entries])
        