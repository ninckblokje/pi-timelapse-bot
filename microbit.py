import _thread
import timelapse
import time
import logging
from bluezero import microbit

_config = None
_ubit = None

def init(config):
    global _config
    _config = config

def start():
    global _ubit

    enabled = _config['MICROBIT'].get('enabled')
    if enabled == "False":
        logging.info("micro:bit disabled")
        return

    adapter = _config['MICROBIT'].get('adapter')
    device = _config['MICROBIT'].get('device')
    logging.info('Connecting to micro:bit %s using adapter %s', device, adapter)

    _ubit = microbit.Microbit(adapter_addr=adapter,
                         device_addr=device)
    _ubit.connect()

    _thread.start_new_thread(_wait_for_button)

def stop():
    logging.info("Disconnecting from micro:bit")
    _ubit.disconnect()

def _wait_for_button():
    while True:
        if _ubit.button_a > 0 and _ubit.button_b == 0:
            _ubit.pixels = [0b00000, 0b01000, 0b11111, 0b01000, 0b00000]
            timelapse.start()
        elif _ubit.button_a == 0 and _ubit.button_b > 0:
            _ubit.pixels = [0b00000, 0b00010, 0b11111, 0b00010, 0b00000]
            timelapse.stop()
