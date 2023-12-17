import abc
from pathlib import Path
from typing import Any, Optional

import yaml


class BaseStorage:
    def __init__(self):
        pass

    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Save state to persistent storage"""

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Load state locally from persistent storage"""


class YamlFileStorage(BaseStorage):
    """
        Class for working with storage in a yaml file
    """

    def __init__(self, file_path: Optional[str] = None):
        super().__init__()
        self.file_path = file_path

    def save_state(self, state: dict) -> None:
        with open(self.file_path, 'w', encoding='utf-8') as config_file:
            yaml.safe_dump(state, config_file)

    def retrieve_state(self) -> dict:
        if Path(self.file_path).is_file():
            with open(self.file_path, 'r', encoding='utf-8') as config_file:
                current_state = yaml.safe_load(config_file)
            return current_state or {}
        return {}


class State:
    """
        A class for storing state when working with data.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.current_state = self.storage.retrieve_state()

    def set_state(self, key: str, value: Any) -> None:
        """Set state for a specific key"""
        self.current_state.update({key: value})
        self.storage.save_state(self.current_state)

    def get_state(self, key: str) -> Any:
        """Get state for a specific key"""
        return self.current_state.get(key)
