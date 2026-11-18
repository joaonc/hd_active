import configparser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

from .utils import FilePath

DEFAULT_CONFIG_FILE_NAME = 'hd_active.ini'


def _to_list(value: str) -> list[str]:
    items = (item.strip(' "\'') for item in value.split(','))
    return [item for item in items if item]


@dataclass
class HdActiveConfig:
    """
    Config options for HD Active, stored in an INI file.
    """

    SECTION_NAME = 'HD Active'
    OPTION_RUN = 'run_on_start'
    OPTION_WAIT = 'wait_between_access'
    OPTION_DRIVE_PATHS = 'drives'

    drive_paths: list[str] = field(default_factory=list)
    wait: float = 60
    run: bool = False

    def __post_init__(self):
        if self.wait <= 0:
            raise ValueError(f'`{self.OPTION_WAIT}` must be greater than 0, got {self.wait}.')

    def __str__(self):
        return f'drive paths: {", ".join(self.drive_paths)}\nwait: {self.wait}s'

    @classmethod
    def _parser(cls) -> configparser.ConfigParser:
        return configparser.ConfigParser(converters={'list': _to_list})

    @classmethod
    def load(cls, file_name: FilePath) -> Self:
        """
        Read the config from a file. Options not in the file get the default values.

        :raises FileNotFoundError: The file doesn't exist.
        :raises ValueError: An option has an invalid value.
        :raises configparser.Error: The file is not a valid INI file.
        """
        parser = cls._parser()
        if not parser.read(file_name):
            raise FileNotFoundError(file_name)
        if not parser.has_section(cls.SECTION_NAME):
            return cls()

        section = parser[cls.SECTION_NAME]
        defaults = cls()
        return cls(
            drive_paths=section.getlist(cls.OPTION_DRIVE_PATHS, defaults.drive_paths),
            wait=section.getfloat(cls.OPTION_WAIT, defaults.wait),
            run=section.getboolean(cls.OPTION_RUN, defaults.run),
        )

    def save(self, file_name: FilePath):
        """
        Write the config to a file, creating it if needed.

        Anything else in an existing file is preserved.
        """
        parser = self._parser()
        parser.read(file_name)
        if not parser.has_section(self.SECTION_NAME):
            parser.add_section(self.SECTION_NAME)
        section = parser[self.SECTION_NAME]
        section[self.OPTION_RUN] = str(self.run)
        section[self.OPTION_WAIT] = str(self.wait)
        section[self.OPTION_DRIVE_PATHS] = ', '.join(str(p) for p in self.drive_paths)

        path = Path(file_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w') as f:
            parser.write(f)
