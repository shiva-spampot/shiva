import datetime
import ssl
from aiosmtpd.controller import Controller
import asyncio
from aiosmtpd.smtp import SMTP
from shiva_authenticator import Authenticator
from shiva_handler import ShivaHandler
from utils import get_logger
from config import get_config


logger = get_logger()


class ShivaSMTPD(SMTP):
    pass


class ShivaController(Controller):
    def factory(self):
        _config = get_config()
        server_hostname = _config["shiva"].get("server_hostname")
        dt_str = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%a, %d %b %Y %H:%M:%S -0"
        )
        ident_str = f"{_config['shiva']['ident']} {dt_str}"
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(
            certfile="./certs/certificate.pem", keyfile="./certs/private_key.pem"
        )
        kwargs = {
            "ident": ident_str,
            "authenticator": Authenticator(),
            "auth_required": True,
            "auth_require_tls": True,
            "tls_context": context,
        }
        if server_hostname:
            kwargs["hostname"] = server_hostname
        return ShivaSMTPD(self.handler, **kwargs)


if __name__ == "__main__":
    _config = get_config()

    _hostname = _config["shiva"]["hostname"]
    _port = _config["shiva"]["port"]
    controller = ShivaController(
        handler=ShivaHandler(),
        hostname=_hostname,
        port=_port,
    )
    controller.start()
    try:
        logger.info(
            f"SMTP server running on {_hostname}:{_port}. Press Ctrl+C to stop."
        )
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop()
