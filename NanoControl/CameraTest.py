from jetcam.csi_camera import *
from PIL import Image
import time, hashlib, sys
import Jetson.GPIO as GPIO

cameraReady = False

ENABLE_PIN = 11
DIR_PIN = 15

def camera_callback(change):
    global cameraReady
    new_image = change["new"]
    
    hash = hashlib.md5(bytes(new_image))
    #print(hash.hexdigest())

    new_image = Image.fromarray(new_image)
    if cameraReady:
        new_image.save(f"test{hash.hexdigest()}.jpeg")
        print(f"Image {hash.hexdigest()} saved")
        cameraReady = False


def init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(ENABLE_PIN, GPIO.OUT)
    GPIO.setup(DIR_PIN, GPIO.OUT)

    GPIO.output(ENABLE_PIN, GPIO.LOW)
    GPIO.output(DIR_PIN, GPIO.LOW)



if __name__ == "__main__":
    init()

    # Custom args for our camera to try and optimize image quality for our environment
    # Note: This uses fork of jetcam library
    GStreamerArgs = f"""
    nvarguscamerasrc sensor-id=0 ! 
    video/x-raw(memory:NVMM), width=3264, height=2464, 
    format=(string)NV12, framerate=(fraction)8/1, exposuretimerange="200000 400000", 
    ee-mode=2, ee-strength=1, tnr-strength=1, tnr-mode=2 ! nvvidconv flip-method=1 ! 
    nvvidconv ! video/x-raw, width=(int)3264, height=(int)2464, 
    format=(string)GRAY8 ! videoconvert ! appsink"""

    cam = CSICamera(custom_args = GStreamerArgs)
    cam.running = True
    cam.observe(camera_callback)
    
    try:
        while True:
            # Run forward for 1 second
            GPIO.output(DIR_PIN, GPIO.HIGH)
            GPIO.output(ENABLE_PIN, GPIO.HIGH)
            time.sleep(1)
            
            # Pause for 0.25 seconds
            GPIO.output(ENABLE_PIN, GPIO.LOW)
            time.sleep(0.25)

            # Pause for at least 0.6 seconds up to picture taken and cameraReady returns to False
            cameraReady = True
            while cameraReady:
                time.sleep(0.1)

            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Cleaning up GPIO")
        GPIO.cleanup()
    



    
    
    

