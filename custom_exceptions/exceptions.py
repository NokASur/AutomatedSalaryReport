class SSHException(Exception):
    def __init__(self, error_message):
        super().__init__(f'SSH Exception: {error_message}')


class SFTPException(Exception):
    def __init__(self, error_message):
        super().__init__(f'SFTP Exception: {error_message}')


class OSException(Exception):
    def __init__(self, error_message):
        super().__init__(f'OSE Exception: {error_message}')
