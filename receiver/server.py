import os.path
from smtpd import SMTPServer

import config
import utils
import json


# TODO: Implement SMTP AUTH using https://github.com/bcoe/secure-smtpd
class SHIVAServer(SMTPServer):
    unique_ssdeep_hashes = set()
    unique_sha1_hashes = set()

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        """ Get more detailed documentation in smtpd.SMTPServer class
        :param peer: tuple: peer contains (ipaddr, port) of the client to our smtp port.
        :param mailfrom: str: mailfrom is the raw address the client claims the message is coming from.
        :param rcpttos: list: rcpttos is a list of raw recipient addresses.
        :param data: bytes: data is a string containing the entire full text of the message.
        :return: This function should return None for a normal `250 Ok' response;
        otherwise, it should return the desired response string in RFC 821
        format.
        """
        # Not doing anything with kwargs for now.
        self._process_spam_message(peer, mailfrom, rcpttos, data)

    def _process_spam_message(self, peer, mailfrom, rcpttos, data):
        print("Received spam, parsing now.")

        sha1_hash, ssdeep_hash = utils.calculate_hashes(data)
        print(f"SHA1 Hash: {sha1_hash}")
        print(f"SSDEEP Hash: {ssdeep_hash}")

        if self._is_spam_duplicate(len(data), sha1_hash, ssdeep_hash):
            print("Duplicate spam found, will not process.")
        else:
            self.unique_ssdeep_hashes.add(ssdeep_hash)
            self.unique_sha1_hashes.add(sha1_hash)

            spam_meta_details = {
                "ssdeep": ssdeep_hash,
                "sha1": sha1_hash
            }
            client_info = self._parse_client_info(peer)
            if client_info:
                spam_meta_details.update(client_info)

            spam_meta_details["sender"] = mailfrom
            spam_meta_details["recipients"] = rcpttos
            spam_meta_details["sensor_name"] = config.SENSOR_NAME

            print(spam_meta_details)

            self._write_files(sha1_hash, spam_meta_details, data)

    def _is_spam_duplicate(self, data_size, sha1_hash, ssdeep_hash):
        if sha1_hash in self.unique_sha1_hashes:
            return True

        # SSDEEP needs data to be larger than 4KB for generating meaningful hashes.
        if data_size > 4096 and \
                utils.compare_ssdeep_hashes(self.unique_ssdeep_hashes, ssdeep_hash):
            return True

    @staticmethod
    def _parse_client_info(peer: tuple):
        try:
            host, port = peer
            return {"client_addr": host, "client_port": port}
        except Exception as e:
            print(f"Failed to parsed peer info: {e}")

    @staticmethod
    def _write_files(unique_hash, meta_details: dict, data: bytes):
        meta_file = os.path.join(config.QUEUE_DIR, f"{unique_hash}.meta")
        eml_file = os.path.join(config.QUEUE_DIR, f"{unique_hash}.eml")

        print("Writing metadata file.")
        with open(meta_file, "w") as fp:
            json.dump(meta_details, fp, indent=4)

        print("Writing raw eml file.")
        with open(eml_file, "wb") as fp:
            fp.write(data)
