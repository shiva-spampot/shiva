import importlib
from config import config


STORAGE_ALIASES = {
    "s3": "storages.s3.S3Storage",
    "local": "storages.local.LocalStorage",
}


def get_storage_backend():
    storage_type = config.get("storage", "storage_type")

    metadata = dict(config["storage"])
    metadata.pop("storage_type")

    if storage_type not in STORAGE_ALIASES:
        raise ValueError(f"Unsupported storage type: {storage_type}")

    module_name, class_name = STORAGE_ALIASES[storage_type].rsplit(".", 1)
    module = importlib.import_module(module_name)
    storage_class = getattr(module, class_name)

    return storage_class(**metadata)
