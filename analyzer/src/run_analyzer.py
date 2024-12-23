import glob
import os.path
from time import sleep
import json
import config
import analyzer
from db.session import SessionLocal


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
    while True:
        db = SessionLocal()
        count = 0
        shiva_analyzer = analyzer.SHIVAAnalyzer(db, config)
        for file_key in get_file_keys(config.QUEUE_DIR):
            count += 1
            shiva_analyzer.run(file_key)
            remove_file(file_key)

        if not count:
            sleep(30)


def remove_file(file_name: str):
    file_path = os.path.join(config.QUEUE_DIR, f"{file_name}.eml")
    os.remove(file_path)

    file_path = os.path.join(config.QUEUE_DIR, f"{file_name}.meta")
    os.remove(file_path)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass
