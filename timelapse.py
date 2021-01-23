import _thread
import logging
import time
import picamera

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(threadName)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z')

    _thread.start_new_thread(do_timelapse, ())

    while 1:
        pass

def do_timelapse():
    with picamera.PiCamera() as camera:
        logging.info('Warming up camera')
        camera.start_preview()
        time.sleep(5)

        for filename in camera.capture_continuous('camera/img{timestamp:%Y-%m-%d-%H-%M-%S}.jpg'):
            logging.debug('Captured image %s', filename)
            time.sleep(5)
        
        camera.stop_preview()

if __name__ == '__main__':
    main()