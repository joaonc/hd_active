import configparser
from typing import List, Union


class HdActiveConfig:
    """
    Config options for HD Active in a INI file format.
    """

    SECTION_NAME = 'HD Active'
    OPTION_RUN = 'run_on_start'
    OPTION_WAIT = 'wait_between_access'
    OPTION_DRIVE_PATHS = 'drives'

    def __init__(self, file_name: str):
        self.file_name = file_name

        # Default values
        self.run: bool = False
        self.wait: Union[int, float] = 60
        self.drive_paths: List[str] = []

        self.config = configparser.ConfigParser(
            converters={'list': lambda x: [i.strip(' "\'') for i in x.split(',')]}
        )
        self.read()

    def __str__(self):
        return f'drive paths: {", ".join(self.drive_paths)}' \
               f'\nwait: {self.wait}s'

    def read(self):
        files_read = self.config.read(self.file_name)
        if not files_read:
            raise FileNotFoundError(self.file_name)
        try:
            section = self.config[self.SECTION_NAME]
            self.run = section.getboolean(self.OPTION_RUN, self.run)
            self.wait = section.getfloat(self.OPTION_WAIT, self.wait)
            self.drive_paths = section.getlist(self.OPTION_DRIVE_PATHS, self.drive_paths)
        except KeyError:
            # Section didn't exist, vars will continue with previous values.
            pass

    def write(self):
        section = self.config[self.SECTION_NAME]
        section[self.OPTION_RUN] = str(self.run)
        section[self.OPTION_WAIT] = str(self.wait)
        section[self.OPTION_DRIVE_PATHS] = ', '.join(
            str(drive_path) for drive_path in self.drive_paths
        )

        with open(self.file_name) as configfile:
            self.config.write(configfile)
