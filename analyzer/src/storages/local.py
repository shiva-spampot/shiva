import os
from typing import Any
from storages.base import BaseStorage


class LocalStorage(BaseStorage):

    def __init__(self, directory_path):
        self.directory_path = directory_path

    def save(self, filename: str, data: Any):
        """Saves data to a local directory."""
        full_path = os.path.join(self.directory_path, filename)
        os.makedirs(
            os.path.dirname(full_path), exist_ok=True
        )  # Ensure the directory exists

        if isinstance(data, str):
            write_mode = "w"
        else:
            write_mode = "wb"

        with open(full_path, write_mode) as file:
            file.write(data)

        return full_path
