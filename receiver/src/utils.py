import os
from hashlib import sha256

import ssdeep

import config


def init_receiver():
    """
    This function is supposed to run before server start for setting up/confirming various
    required things.
    :return:
    """
    # Creating queue and other directories if they don't exist.
    os.makedirs(config.QUEUE_DIR, exist_ok=True)


def calculate_hashes(content: bytes) -> tuple:
    return sha256(content).hexdigest(), ssdeep.hash(content)


def compare_ssdeep_hashes(unique_hashes, new_hash):
    print("Comparing SSDEEP hash with existing hashes.")
    for unique_hash in unique_hashes:
        print(ssdeep.compare(unique_hash, new_hash))
        if ssdeep.compare(unique_hash, new_hash) >= config.THRESHOLD:
            return True
