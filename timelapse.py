import _thread
import glob
import logging
import os
import time
import picamera
from threading import Lock

_config = None
_data_lock = Lock()
_status = {
    'isRunning': False,
    'stop': False
}

def init(config):
    global _config
    _config = config

def get_last_img():
    outputdir = _config['TIMELAPSE'].get('outputdir')
    list_of_files = glob.glob(outputdir + '/*')
    if len(list_of_files) == 0:
        return None
    return max(list_of_files, key=os.path.getctime)

def is_running():
    return _status['isRunning']

def start():
    _thread.start_new_thread(_do_timelapse, (_status,))

def stop():
    with _data_lock:
        _status['stop'] = True

def _do_timelapse(status):
    with _data_lock:
        _status['isRunning'] = True
        _status['stop'] = False

    fileformat = _config['TIMELAPSE'].get('fileformat')
    interval = _config['TIMELAPSE'].getfloat('interval')
    outputdir = _config['TIMELAPSE'].get('outputdir')

    with picamera.PiCamera() as camera:
        logging.info('Starting timelapse with interval %s', interval)
        camera.start_preview()
        time.sleep(interval)

        for filename in camera.capture_continuous(outputdir + '/' + fileformat):
            logging.debug('Captured image %s', filename)
            time.sleep(interval)

            if status['stop']:
                break
        
        logging.info('Stopping timelapse')
        camera.stop_preview()
    
    with _data_lock:
        _status['isRunning'] = False
        _status['stop'] = False
