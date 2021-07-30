import sys


class Logging:

    @staticmethod
    def input(msg: str) -> str:
        out = input(msg + '\n')
        if out == 'exit':
            sys.exit('User exit\n')
        return out

    @staticmethod
    def yes_no(msg: str) -> bool:
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
        print('\n' + msg)