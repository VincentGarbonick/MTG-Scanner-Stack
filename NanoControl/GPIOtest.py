import nanocamera
import Jetson.GPIO as GPIO


import time


if __name__ == "__main__":

    """
    camera = nanocamera.Camera()
    print(camera.isReady())
    """
    GPIO.setmode(GPIO.BOARD)


    GPIO.setup(7, GPIO.OUT)
    for i in range(0, 500):
        GPIO.output(7, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(7, GPIO.HIGH)
        time.sleep(0.01)

    print("Done")
    GPIO.cleanup()