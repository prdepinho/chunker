
import socket
import threading
import configparser
import traceback
import logging
import logging.config
from datetime import datetime
import os

def write_to_file(buffer, file_name, client_sock, count, logger):
    now = datetime.now()
    name = "%s_%d_%d_%d%.2d%.2d%.2d%.2d%.2d" % (
            file_name, client_sock.fileno(), count,
            now.year, now.month, now.day, now.hour, now.minute, now.second
            )
    with open(name, "wb") as file:
        file.write(bytes(buffer))
        logger.info('written to file %s (%d bytes)' % (name, len(buffer)))


def server_worker(client_sock, client_addr, logger, file_size, file_name):
    try:
        buffer = []
        count = 0
        while True:
            data = client_sock.recv(2048)
            if not data:
                if len(buffer) > 0:
                    write_to_file(buffer, file_name, client_sock, count, logger)
                break

            left = file_size - len(buffer)
            if left > len(data):
                buffer += data
            else:
                buffer += data[:left]
                write_to_file(buffer, file_name, client_sock, count, logger)
                count += 1
                buffer = data[left:]


    except TimeoutError:
        logger.info("timeout %s" % str(client_addr))
    except Exception as e:
        logger.error(traceback.format_exc())
    finally:
        client_sock.close()


if __name__ == "__main__":
    config_file = "server.ini"

    try:
        logging.config.fileConfig("logging.ini")
        logger = logging.getLogger("server")

        config = configparser.ConfigParser()
        config.read(config_file)
        host      =     os.environ.get('SERVER_HOST')      or config.get('server', 'host', fallback=None)
        port      = int(os.environ.get('SERVER_PORT')      or config.get('server', 'port', fallback=0))
        timeout   = int(os.environ.get('SERVER_TIMEOUT')   or config.get('server', 'timeout', fallback=0))
        file_size = int(os.environ.get('SERVER_FILE_SIZE') or config.get('server', 'file_size', fallback=0))
        file_name =     os.environ.get('SERVER_FILE_NAME') or config.get('server', 'file_name', fallback=None)
        if not host: raise ValueError('server host not defined')
        if not port: raise ValueError('server port not defined')
        if not timeout: raise ValueError('server timeout not defined')
        if not file_size: raise ValueError('server file_size not defined')
        if not file_name: raise ValueError('server file_name not defined')
        logger.info('server - %s:%d' % (host, port))
        logger.info('timeout: %ds, file_size: %d bytes, file_name: "%s"' % (timeout, file_size, file_name))

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((host, port))
            sock.listen(1)
            logger.info('listening')

            while True:
                client_sock, client_addr = sock.accept()
                client_sock.settimeout(timeout)
                logger.info('connected to: %s' % str(client_addr))

                thread = threading.Thread(
                        target=server_worker,
                        args=(client_sock, client_addr, logger, file_size, file_name))
                thread.start()

    except ValueError as e:
        logger.error('configuration error: %s' % str(e))
    except FileNotFoundError as e:
        logger.error('error: file not found: %s' % filename)
    except Exception as e:
        logger.error(traceback.format_exc())

