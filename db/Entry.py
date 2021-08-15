from interface.Logging import Logging
from typing import Dict
import aes.aes as aes

class Entry:
    """
        main storing class
        each instance holds information about single title/password instance
    """

    # title whic uniquely identifies the Entry
    title: str = ''

    # passwords
    # only passowrd_encrypted stored in database files
    # password_decrypted loads later
    password_decrypted: str = ''
    password_encrypted: str = ''

    # additional optional information
    url: str  = ''
    user_name: str  = ''
    notes: str  = ''

    def encrypt(self, key: str) -> None:
        """encrypts self.password_decrypted given master key, saves to self.password_encrypted"""
        
        # password_decrypted should not be missing, exit app if so
        if self.password_decrypted == '':
            Logging.print(f'[Entry {self.title}] Missing password_decrypted')
            return

        # encrypt to self.password_encrypted
        self.password_encrypted = aes.encrypt(self.password_decrypted, key)

    def decrypt(self, key: str) -> None:
        """decrypts stored password from self.password_encrypted, saves to self.password_decrypted"""
        
        # password_encrypted should not be missing
        if self.password_encrypted == '':
            Logging.print(f'[Entry {self.title}] Missing password_encrypted')
            return

        self.password_decrypted = aes.decrypt(self.password_encrypted, key)

    def to_dict(self) -> Dict[str, str]:
        """returns self as a dictionary without password_decrypted"""

        # get all attributes to be printed out
        attributes = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a)) and getattr(self, a) != '' and a != 'password_decrypted']
        attribute_values = [getattr(self, a) for a in attributes]

        return dict([(attribute, attribute_value) for attribute, attribute_value in zip(attributes, attribute_values)])

    def __str__(self) -> str:
        """printed string in main app"""
        return f'__ Entry {self.title} __\nPassword: {self.password_decrypted}\nUser name: {self.user_name}\nURL: {self.url}\nNotes: {self.notes}'