import _thread
import configparser
import logging
import logging.config
import time
import picamera
import telegrambot
import timelapse
import microbit
from threading import Lock

config = configparser.ConfigParser()

def main():
    timelapse.init(config)
    telegrambot.init(config)

    microbit.init(config)
    microbit.start()

    telegrambot.start_polling()

    # try:
    #     while 1:
    #         pass
    # except KeyboardInterrupt:
    #     logging.info('Received keyboard interrupt, waiting 10 seconds')
    #     time.sleep(10)

def read_config():
    logging.config.fileConfig('config/logging.ini')

    logging.info('Reading configuration')
    config.read('config/config.ini')

if __name__ == '__main__':
    read_config()
    main()
