import _thread
import datetime
import glob
import logging
import os
import subprocess
import time
import picamera
from fractions import Fraction
from threading import Lock

_config = None
_data_lock = Lock()
_status = {
    'isRendering': False,
    'isRunning': False,
    'stop': False
}

def init(config):
    global _config
    _config = config

def get_last_img():
    outputdir = _config['TIMELAPSE_IMG'].get('outputdir')
    list_of_files = glob.glob(outputdir + '/*')
    if len(list_of_files) == 0:
        return None
    return max(list_of_files, key=os.path.getctime)

def is_running():
    return _status['isRunning']

def render(renderingFinishedCallback = None):
    if _status['isRunning']:
        return False

    with _data_lock:
        _status['isRendering'] = True

    _thread.start_new_thread(_do_render, (renderingFinishedCallback,))
    return True

def start():
    if not _can_start_timelapse():
        return False

    _thread.start_new_thread(_do_timelapse, (_status,))
    return True

def stop():
    with _data_lock:
        _status['stop'] = True

def _can_start_timelapse():
    return not _status['isRendering'] and not _status['isRunning']

def _configure_camera(camera: picamera.PiCamera):
    camera.shutter_speed = int(_config['CAMERA'].get('shutterSpeed'))

    warmup = _config['CAMERA'].getfloat('warmup')
    logging.debug('Warming camera up for %s seconds', warmup)
    time.sleep(warmup)

    camera.awb_mode = _config['CAMERA'].get('awb')
    camera.exposure_mode = _config['CAMERA'].get('exposure')

    logging.debug('Camera config:')
    logging.debug('- awb: %s', camera.awb_mode)
    logging.debug('- exposure: %s', camera.exposure_mode)
    logging.debug('- shutter speed: %s', camera.shutter_speed)

def _do_render(renderingFinishedCallback = None):
    try:
        cmd = _config['TIMELAPSE_VIDEO'].get('cmd')
        inputGlob = _config['TIMELAPSE_VIDEO'].get('inputGlob')
        outputFile = _config['TIMELAPSE_VIDEO'].get('outputdir') + '/' + _config['TIMELAPSE_VIDEO'].get('fileformat').format(timestamp=datetime.datetime.now())
        
        logging.info('Starting timelapse rendering with glob %s to %s', inputGlob, outputFile)
        with subprocess.Popen([cmd, inputGlob, outputFile]):
            logging.debug('Waiting for %s', cmd)
        
        logging.info('Finished timelapse rendering')

        if renderingFinishedCallback != None:
            renderingFinishedCallback(True, outputFile)
    except:
        logging.exception('Exception in timelapse rendering')
        if renderingFinishedCallback != None:
            renderingFinishedCallback(False, None)
    finally:
        with _data_lock:
            _status['isRendering'] = False

def _do_timelapse(status):
    with _data_lock:
        _status['isRunning'] = True
        _status['stop'] = False

    fileformat = _config['TIMELAPSE_IMG'].get('fileformat')
    interval = _config['TIMELAPSE_IMG'].getfloat('interval')
    outputdir = _config['TIMELAPSE_IMG'].get('outputdir')
    
    with _init_camera() as camera:
        _configure_camera(camera)

        logging.info('Starting timelapse with interval of %s seconds', interval)
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

def _init_camera() -> picamera.PiCamera:
    fractionValue = _config['CAMERA'].get('fraction')
    fraction = None if fractionValue == '' else Fraction(fractionValue)
    sensorMode = int(_config['CAMERA'].get('sensorMode'))

    logging.debug('Camera init:')
    logging.debug('- Framerate: %s', fractionValue)
    logging.debug('- Sensor mode: %s', sensorMode)

    return picamera.PiCamera(framerate=fraction,sensor_mode=sensorMode)

