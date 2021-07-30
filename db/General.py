import json

class General:
    last_db_used: str
    location: str
    file_name = 'general.json'

    def load(self, location: str) -> None:
        general = json.load(open(f'{location}/{self.file_name}'))
        self.last_db_used = general['last_db_used']
        self.location = location

    def change_last_db_used(self, last_db_name: str) -> None:
        self.last_db_used = f'{last_db_name}'
        self.save()

    def save(self) -> None:
        with open(f'{self.location}/{self.file_name}', 'w') as general_file:
            json.dump({
                'last_db_used': self.last_db_used if hasattr(self, 'last_db_used') else ''
            }, general_file)