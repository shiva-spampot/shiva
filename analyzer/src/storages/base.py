from abc import ABC, abstractmethod
from typing import Any


class BaseStorage(ABC):

    @abstractmethod
    def save(self, filename:str, data: Any) -> str:
        """Method to save data to the storage."""
        pass
