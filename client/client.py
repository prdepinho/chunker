
import socket
import time
import configparser
import traceback
import logging
import logging.config
import sys
import os

if __name__ == "__main__":
    config_file = "client.ini"

    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print("how to use: \n%s <filename>" % sys.argv[0])
        sys.exit()

    try:
        logging.config.fileConfig("logging.ini")
        logger = logging.getLogger("client")

        config = configparser.ConfigParser()
        loaded = len(config.read(config_file)) > 0
        host      =     os.environ.get('CLIENT_HOST') or config.get('client', 'host', fallback=None)
        port      = int(os.environ.get('CLIENT_PORT') or config.get('client', 'port', fallback=0))
        if not host: raise ValueError('client host not defined')
        if not port: raise ValueError('client port not defined')
        logger.info('client - %s:%d' % (host, port))

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))

            with open(filename, 'rb') as file:
                message = file.read()
                logger.info("opened %s" % filename)

            sock.sendall(message)
            logger.info("sent file")

    except ValueError as e:
        logger.error('configuration error: %s' % str(e))
    except FileNotFoundError as e:
        logger.error('error: file not found: %s' % filename)
    except Exception as e:
        logger.error(traceback.format_exc())
