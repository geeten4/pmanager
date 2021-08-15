import json

class General:
    """stores general info about the whole app"""

    # last database which was used
    # application defaults to this
    last_db_used: str
    # location of file storing all general information
    location: str
    # name of the file
    file_name = 'general.json'

    def load(self, location: str) -> None:
        """loads information from file given the file location"""
        general = json.load(open(f'{location}/{self.file_name}'))
        # save to last used database
        self.last_db_used = general['last_db_used']
        self.location = location

    def change_last_db_used(self, last_db_name: str) -> None:
        """changes last_db_used and saves"""
        self.last_db_used = f'{last_db_name}'
        self.save()

    def save(self) -> None:
        """saves current content to file"""
        with open(f'{self.location}/{self.file_name}', 'w') as general_file:
            json.dump({
                'last_db_used': self.last_db_used if hasattr(self, 'last_db_used') else ''
            }, general_file)