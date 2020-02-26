import cv2
import concurrent.futures
from config.app_conf import AppConf
from utils.logger import Logger
from video.v3io_image import V3ioImage
import logging
import socket
import requests


INIT_FILE_PATH = "config/init.ini"
NUMBER_OF_FRAMES = -1
CAMERA_NAME = socket.gethostname()

logger = Logger(level=logging.DEBUG)
app_conf = AppConf(logger, INIT_FILE_PATH)
cap = cv2.VideoCapture(0)
count = NUMBER_OF_FRAMES
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    while count > 0 or NUMBER_OF_FRAMES == -1:
        try:
            # Capture frame-by-frame
            ret, frame = cap.read()
            if ret:
                cv2.imshow('frame', frame)
                vi = V3ioImage(logger, frame, CAMERA_NAME)
                img_json = vi.image_json
                future = {executor.submit(logger.info(requests.request("POST", app_conf.nuclio_url, json=img_json)))}
            else:
                logger.error("read cap failed")
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            count = count-1
        except Exception as e:
            logger.error(e)
    # When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

