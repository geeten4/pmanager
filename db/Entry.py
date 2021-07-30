from interface.Logging import Logging
from typing import Dict
import aes.aes as aes

class Entry:
    url: str  = ''
    user_name: str  = ''
    notes: str  = ''
    password_decrypted: str = ''
    password_encrypted: str = ''
    title: str = ''

    def encrypt(self, key: str) -> None:
        if self.password_decrypted == '':
            Logging.print(f'[Entry {self.title}] Missing password_decrypted')
            return
        self.password_encrypted = aes.encrypt(self.password_decrypted, key)

    def decrypt(self, key: str) -> None:
        if self.password_encrypted == '':
            Logging.print(f'[Entry {self.title}] Missing password_encrypted')
            return
        self.password_decrypted = aes.decrypt(self.password_encrypted, key)

    def to_dict(self) -> Dict[str, str]:
        """returns self as a dictionary without password_decrypted"""

        attributes = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a)) and getattr(self, a) != '' and a != 'password_decrypted']
        attribute_values = [getattr(self, a) for a in attributes]

        return dict([(attribute, attribute_value) for attribute, attribute_value in zip(attributes, attribute_values)])

    def __str__(self) -> str:
        return f'__ Entry {self.title} __\nPassword: {self.password_decrypted}\nUser name: {self.user_name}\nURL: {self.url}\nNotes: {self.notes}'