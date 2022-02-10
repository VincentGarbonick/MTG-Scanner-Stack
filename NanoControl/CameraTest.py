from jetcam.csi_camera import *
from PIL import Image




if __name__ == "__main__":
    cam = CSICamera(width=1920, height=1080, capture_width=3280, capture_height=2464, capture_fps=4 )
    test = cam.read()
    

    print(cam.value)
    print(cam.value)
    asdf = Image.fromarray(cam.value)
    asdf.show()