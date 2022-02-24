from jetcam.csi_camera import *
from PIL import Image
import time, hashlib, sys

def camera_callback(change):
    """
    TODO:
    Use messaging interface to synchronize image capture and motor advancement

    Motor code sends message to capture image once card/motor is in position
    in camera_callback, if message that system is ready for picture, capture and save image to disk
    Send message back to motor program after finished with operations
    When motor code receives this message, it continues and advances to next card
    
    """
    new_image = change["new"]
    
    hash = hashlib.md5(bytes(new_image))
    print(hash.hexdigest())

    new_image = Image.fromarray(new_image)
    new_image.save(f"test{hash.hexdigest()}.jpeg")
    sys.exit(0)

if __name__ == "__main__":

    # Custom args for our camera to try and optimize image quality for our environment
    # Note: This uses fork of jetcam library
    GStreamerArgs = f"""
    nvarguscamerasrc sensor-id=0 ! 
    video/x-raw(memory:NVMM), width=3264, height=2464, 
    format=(string)NV12, framerate=(fraction)2/1, exposuretimerange="200000 400000", 
    ee-mode=2, ee-strength=1, tnr-strength=1, tnr-mode=2 ! nvvidconv flip-method=1 ! 
    nvvidconv ! video/x-raw, width=(int)3264, height=(int)2464, 
    format=(string)GRAY8 ! videoconvert ! appsink"""

    cam = CSICamera(custom_args = GStreamerArgs)
    cam.running = True
    cam.observe(camera_callback)
    time.sleep(10)
    sys.exit(0)


    
    
    

