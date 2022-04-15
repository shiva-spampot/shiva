#!/usr/bin/env python3

import asyncore

from server import SHIVAServer
import config
import utils


def run():
    print("Starting the SMTP server now.")
    utils.init_receiver()

    # Instantiating a new object automatically also starts listening on provided host and port
    SHIVAServer(localaddr=(config.SHIVA_HOST, config.SHIVA_PORT), remoteaddr=None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    run()
