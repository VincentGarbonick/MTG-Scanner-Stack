import Jetson.GPIO as GPIO
from jetcam.csi_camera import *
from PIL import Image
import time, hashlib, sys

# Motor 1 Pins
PIN_1 = 29 #in 1a (BLUE)
PIN_2 = 31 #in 2a (GREEN)

# Motor 2 Pins
PIN_3 = 33 #in 1b (YELLOW)
PIN_4 = 35 #in 2b (WHITE)

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

# Set up and initialize all motor pins and set the motors to stop
def initializePins():

    print("Initializing GPIO")

    # Don't show warnings about GPIO pins
    GPIO.setwarnings(False)

    # Initialize all necessary pins as outputs
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PIN_1, GPIO.OUT)
    GPIO.setup(PIN_2, GPIO.OUT)
    GPIO.setup(PIN_3, GPIO.OUT)
    GPIO.setup(PIN_4, GPIO.OUT)

    # Stop both motors (just in case)
    stopMotor([PIN_1, PIN_2], True)
    stopMotor([PIN_3, PIN_4], False)

# Start the motor by passing it the first and second pin as a list and a boolean value for direction
def startMotor(pins, forward):

    if forward:
        GPIO.output(pins[0], GPIO.HIGH)
        GPIO.output(pins[1], GPIO.LOW)

    else:
        GPIO.output(pins[0], GPIO.LOW)
        GPIO.output(pins[1], GPIO.HIGH) 

# Stop the motor by passing it the first and second pin as a list and a boolean value for brake type
def stopMotor(pins, hardBrake):

    if hardBrake:
        GPIO.output(pins[0], GPIO.HIGH)
        GPIO.output(pins[1], GPIO.HIGH)

    else:
        GPIO.output(pins[0], GPIO.LOW)
        GPIO.output(pins[1], GPIO.LOW)

# Cleanup camera and GPIO for safe program exit
def cleanup(camera):
    
    stopMotor([PIN_1, PIN_2], True)
    stopMotor([PIN_3, PIN_4], False)

    print("\n\n Initiating Cleanup Sequence\n")
    camera._cleanup()

    print("\nCleaning up GPIO")
    GPIO.cleanup()
    print("GPIO Cleanup: Done Success\nGPIO released")

    print("\nExiting Gracefully")
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

    print("Initializing Camera")
    cam = CSICamera(custom_args = GStreamerArgs)
    cam.running = True
    cam.observe(cameraCallback)

    initializePins()
    motor1 = [PIN_1, PIN_2]
    motor2 = [PIN_3, PIN_4]

    print(f"Threadstop: {threadStop == True}")

    try:

        while True:
            if threadStop == True:
                cleanup(cam)
            
            # Feed one card onto image capture rails
            print("\nFeeding Card")
            startMotor(motor1, True)
            time.sleep(3)
            stopMotor(motor1, True)
            time.sleep(1)
            startMotor(motor1, False)
            time.sleep(1.7)
            stopMotor(motor1, True)

            # Set the camera to ready and take an image
            cameraReady = True
            while cameraReady:
                if threadStop == True:
                    cleanup(cam)
                time.sleep(0.1)

            # Give the camera a moment to get a clear image
            time.sleep(1)

            # Run image rail clearing motor
            # Note that motor2 needs to run backward since it is geared
            startMotor(motor2, False)
            time.sleep(1)
            stopMotor(motor2, False)

    # In the case of keyboard interrupt, cleanup the camera and GPIO and exit gracefully
    except KeyboardInterrupt:
        cleanup(cam)

    
if __name__ == "__main__":
    main(False)
  
### END OF FILE ###
