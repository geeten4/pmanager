import sys


class Logging:
    """handles all logging in app, only edits the messages"""

    @staticmethod
    def input(msg: str) -> str:
        """normal input from user"""
        out = input(msg + '\n')
        if out == 'exit':
            # always check if user wants to exit
            sys.exit('User exit\n')
        return out

    @staticmethod
    def yes_no(msg: str) -> bool:
        """boolean from user"""
        message = msg + '\n yes/no\n'
        yeses = ['yes', 'YES', 'Yes', 'y', 'Y']
        nos = ['no', 'NO', 'No', 'n', 'N']

        out = input(message)
        while out not in yeses and out not in nos:
            Logging.print('Incorrect input. Expect "yes" or "no".')
            out = input(message)

        return out in yeses

    @staticmethod
    def print(msg: str) -> None:
        """classic print"""
        print('\n' + msg)