import os

from integrations import virustotal


class SHIVAAnalyzer(object):
    def __init__(self, config):
        self._config = config
        self.archive_dir = self._get_archive_path()
        self._vt_client = virustotal.VTLookup(config.VT_API_KEY)

    def _get_archive_path(self):
        archive_dir = self._config.ARCHIVE_DIR
        if archive_dir:
            if not os.path.exists(self.archive_dir):
                try:
                    os.mkdir(self.archive_dir)
                except Exception as e:
                    print(f"Failed to create archive dir: {e}")
                    archive_dir = ""
        return archive_dir

    def parse(self, file_key):
        parsed_info = {}

        # ## Parsing logic comes here ## #
        print(f"Currently parsing: {file_key}")

        return parsed_info
