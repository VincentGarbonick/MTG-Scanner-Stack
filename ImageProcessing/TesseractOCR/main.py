import pytesseract
from PIL import Image

"""
This will be the main file for handling image processing on the Jetson Nano.
Images will be acquired from a separate program that will be in control of motor and camera.
This program will save captured pictures to the 'ImageTemp' directory.
Images in this directory will then be processed as a FIFO queue. 
Processed images will be added to the database. 

"""



if __name__ == "__main__":

