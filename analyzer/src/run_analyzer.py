#!/usr/bin/env python3

import glob
import os.path
from time import sleep
import json

import config
import analyzer


def get_file_keys(queue_dir):
    if not os.path.exists(queue_dir):
        print("Queue directory does not exists. Creating it.")
        os.mkdir(queue_dir)

    for eml_file in glob.iglob(f"{queue_dir}/*.eml"):
        file_key = eml_file[:-4]
        if os.path.exists(eml_file) and os.path.exists(f"{file_key}.meta"):
            yield os.path.basename(file_key)


def run():
    print("Starting SHIVA Analyzer now.")
    shiva_analyzer = analyzer.SHIVAAnalyzer(config)

    while True:
        for file_key in get_file_keys(config.QUEUE_DIR):
            result = shiva_analyzer.parse(file_key)
            print(json.dumps(result, indent=4))
            # TODO: index this result

        print("Processed all files (if any) collected till now. Sleeping now for 30 seconds.")
        sleep(30)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass
