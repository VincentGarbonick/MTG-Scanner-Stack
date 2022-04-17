import Jetson.GPIO as GPIO
from jetcam.csi_camera import *
from PIL import Image
import time, hashlib, sys

PIN_1 = 29 #in 1a 
PIN_2 = 31 #in 2a 
PIN_3 = 33 #in 1b 
PIN_4 = 35 #in 2b 

cameraReady = False

def cameraCallback(change):
    global cameraReady
    newImage = change["new"]
    hash = hashlib.md5(bytes(newImage))
    #print(hash.hexdigest())

    newImage = Image.fromarray(newImage)
    if cameraReady:
        newImage.save(f"/home/dt17/git/MTG-Scanner-Stack/ImageProcessing/TesseractOCR/ImageTemp/{hash.hexdigest()}.jpeg")
        print(f"Image {hash.hexdigest()} saved")
        cameraReady = False

def initializePins():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PIN_1, GPIO.OUT)
    GPIO.setup(PIN_2, GPIO.OUT)
    GPIO.setup(PIN_3, GPIO.OUT)
    GPIO.setup(PIN_4, GPIO.OUT)

def cleanup(camera):
    GPIO.output(PIN_1, GPIO.HIGH)
    GPIO.output(PIN_2, GPIO.HIGH) #braking 
    GPIO.output(PIN_3, GPIO.LOW) # motor two low braking 
    GPIO.output(PIN_4, GPIO.LOW)
    print("Cleaning up camera thread")
    camera._cleanup()
    GPIO.cleanup()
    sys.exit(0)


def main(threadStop):
    global cameraReady

    # Custom args for our camera to try and optimize image quality for our environment
    # Note: This uses fork of jetcam library
    GStreamerArgs = f"""
    nvarguscamerasrc sensor-id=0 ! 
    video/x-raw(memory:NVMM), width=3264, height=2464, 
    format=(string)NV12, framerate=(fraction)4/1, exposuretimerange="200000 400000", 
    ee-mode=2, ee-strength=1, tnr-strength=1, tnr-mode=2 ! nvvidconv flip-method=1 ! 
    nvvidconv ! video/x-raw, width=(int)3264, height=(int)2464, 
    format=(string)GRAY8 ! videoconvert ! appsink"""

    initializePins()
    cam = CSICamera(custom_args = GStreamerArgs)
    cam.running = True
    cam.observe(cameraCallback)


    print(f"Threadstop: {threadStop == True}")
    try:
        while True:
            if threadStop == True:
                cleanup(cam)
                print()
            print("l00p")
            GPIO.output(PIN_1, GPIO.HIGH)
            GPIO.output(PIN_2, GPIO.LOW) #feed forwarrd 
            time.sleep(3)
            GPIO.output(PIN_1, GPIO.HIGH)
            GPIO.output(PIN_2, GPIO.HIGH) #braking 
            time.sleep(1)
            GPIO.output(PIN_1, GPIO.LOW)
            GPIO.output(PIN_2, GPIO.HIGH) # reversing to home 
            time.sleep(1.7)
            GPIO.output(PIN_1, GPIO.HIGH)
            GPIO.output(PIN_2, GPIO.HIGH) #braking 

            cameraReady = True
            while cameraReady:
                if threadStop == True:
                    cleanup(cam)
                time.sleep(0.1)


            time.sleep(1)
            GPIO.output(PIN_1, GPIO.HIGH)
            GPIO.output(PIN_2, GPIO.HIGH) # braking again

            GPIO.output(PIN_3, GPIO.LOW) 
            GPIO.output(PIN_4, GPIO.HIGH) # motor two going forward
            time.sleep(1)
            GPIO.output(PIN_3, GPIO.LOW) # motor two low braking 
            GPIO.output(PIN_4, GPIO.LOW)
    except KeyboardInterrupt:
        cleanup(cam)

    

if __name__ == "__main__":
    main(False)
  
        
