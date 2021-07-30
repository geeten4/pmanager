from interface.Logging import Logging
import random
from typing import List
from db.Entry import Entry
from hashlib import sha256
import json

# save hash of master password to validate before unlocking

class Database:

    entries: List[Entry] = []
    # second half of master key sha256 hash used as validation when unlocking db
    master_pass_sha256: str
    db_file_location: str
    name: str

    @staticmethod
    def from_file(db_file_location: str):
        database = Database()
        database.db_file_location = db_file_location
        database.name = db_file_location.split('/')[-1].rstrip('.json')
        database.load()
        return database

    @staticmethod
    def generate_password() -> str:
        return '%030x' % random.randrange(16**32)

    def del_entry(self, entry_title: str):
        self.entries = [entry for entry in self.entries if entry.title != entry_title]
        self.save()

    def add_entry(self, entry: Entry):
        self.entries.append(entry)
        self.save()
    
    def save(self):
        with open(self.db_file_location, 'w') as db_file:
            json.dump({
                'master_password': {
                    'sha256': self.master_pass_sha256,
                },
                'entries': [entry.to_dict() for entry in self.entries],
            }, db_file)

    def load(self) -> None:

        db = json.load(open(self.db_file_location))

        # load sha hash of master password
        self.master_pass_sha256 = db['master_password']['sha256']

        # load all entries
        entries_json = db['entries']
        entries: List[Entry] = []

        for entry_json in entries_json:
            entry = Entry()

            for attribute in entry_json:
                setattr(entry, attribute, entry_json[attribute])
            
            entries.append(entry)
        
        self.entries = entries

    def unlock(self, master_password: str) -> None:

        # first half of master password serves as key for all entries
        master_password_hash = sha256(master_password.encode('utf-8')).hexdigest()[:32]

        for entry in self.entries:
            entry.decrypt(master_password_hash)

    def password_correct(self, password: str) -> bool:
        # second half of master password hash serves for validating
        password_hash = sha256(password.encode('utf-8')).hexdigest()[32:]
        return self.master_pass_sha256 == password_hash

    def entry_titles(self) -> List[str]:
        return [entry.title for entry in self.entries]

    def entry_by_title(self, entry_title: str) -> Entry:
        entries = [entry for entry in self.entries if entry.title == entry_title]
        if entries == []:
            Logging.print('No such entry found.')
            return
        return entries[0] 

    def __str__(self) -> str:
        return f'*** DATABASE {self.name} ***\n\n ' + '\n\n'.join([str(entry) for entry in self.entries])
        