import os
from glob import iglob

from integrations import virustotal
import email_parser


class SHIVAAnalyzer(object):
    def __init__(self, config):
        self._config = config
        self.archive_dir = self._get_archive_path()
        self._parser = email_parser.EmailParser(self._config.QUEUE_DIR)
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

    def parse(self, file_key: str) -> dict:
        print(f"Currently parsing {file_key}")
        parsed_info = self._parser.parse(file_key)
        attachments = parsed_info.get("attachments")
        if attachments:
            if self._vt_client:
                for attachment in attachments:
                    print(f"Checking {attachment['file_sha256']} hash on VT.")
                    vt_result = self._vt_client.lookup_file_reputation(attachment['file_sha256'])
                    if vt_result:
                        attachment["virustotal"] = vt_result
        return parsed_info
