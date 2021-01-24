import _thread
import configparser
import logging
import logging.config
import time
import picamera
from threading import Lock

_app_status = {
    'stopTimelapse': False
}
config = configparser.ConfigParser()
data_lock = Lock()

def main():
    _thread.start_new_thread(do_timelapse, (_app_status,))

    try:
        while 1:
            pass
    except KeyboardInterrupt:
        logging.info('Received keyboard interrupt, waiting 10 seconds')
        with data_lock:
            app_status['stopTimelapse'] = True
        time.sleep(10)

def do_timelapse(appStatus):
    fileformat = config['TIMELAPSE'].get('fileformat')
    interval = config['TIMELAPSE'].getfloat('interval')

    with picamera.PiCamera() as camera:
        logging.info('Starting timelapse with interval %s', interval)
        camera.start_preview()
        time.sleep(interval)

        for filename in camera.capture_continuous(fileformat):
            logging.debug('Captured image %s', filename)
            time.sleep(interval)

            if appStatus['stopTimelapse']:
                break
        
        logging.info('Stopping timelapse')
        camera.stop_preview()

def read_config():
    logging.config.fileConfig('config/logging.ini')

    logging.info('Reading configuration')
    config.read('config/config.ini')

if __name__ == '__main__':
    read_config()
    main()
