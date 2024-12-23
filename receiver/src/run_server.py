#!/usr/bin/venv python3
import asyncio
from aiosmtpd.controller import Controller
import logging

from server import ShivaHandler, Authenticator


def run():
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d [+] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

    handler = ShivaHandler()
    controller = Controller(
        handler,
        hostname="0.0.0.0",
        port=2525,
        authenticator=Authenticator(),
        auth_required=True,
        auth_require_tls=False,
    )
    controller.start()

    try:
        print("SMTP server running on 0.0.0.0:2525. Press Ctrl+C to stop.")
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop()


if __name__ == "__main__":
    run()
