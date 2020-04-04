from picamera import PiCamera
from time import sleep


#CHANGE PATH
SOURCE_IMAGE_PATH = "/home/vardhan/Chandu-Vardhan/Face_Recognition/faces/source42.jpg"


camera = PiCamera()
#camera.start_preview()
#sleep(5)
camera.capture(SOURCE_IMAGE_PATH)
#camera.stop_preview()