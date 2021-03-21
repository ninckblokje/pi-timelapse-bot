import _thread
import configparser
import logging
import logging.config
import microbit
import picamera
import telegrambot
import time
import timelapse
from threading import Lock

config = configparser.ConfigParser()

def main():
    timelapse.init(config)
    telegrambot.init(config)

    microbit.init(config)
    microbit.start()

    telegrambot.start_polling()

    microbit.stop()
    logging.info('Stopping, waiting 5 seconds')
    time.sleep(5)

def read_config():
    logging.config.fileConfig('config/logging.ini')

    logging.info('Reading configuration')
    config.read('config/config.ini')

if __name__ == '__main__':
    read_config()
    main()
