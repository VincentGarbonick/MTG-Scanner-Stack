import nanocamera, math, time
import Jetson.GPIO as GPIO

# GLOBAL CONSTANTS
STEP_PIN = 15

# Call to send a step pulse on STEP_PIN for a specified duration at a given frequency to run a stepper motor
def run_motor(duration = 1, freq = 2000):
    
    step_iterations = freq * math.floor(duration / 2)
    period = 1 / freq

    print("Running motor at", freq, "Hz for approximately", duration, "seconds.")

    start_time = time.time()
    for i in range(0, step_iterations):
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(period)
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(period)

    GPIO.output(STEP_PIN, GPIO.LOW)
    end_time = time.time()

    print("Runtime =", end_time - start_time, "\n")


if __name__ == "__main__":

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(STEP_PIN, GPIO.OUT)


    for j in range(1000, 4000, 500):
        run_motor(5, j)
        time.sleep(0.5)

    print("Done")
    GPIO.output(STEP_PIN, GPIO.LOW) 
    GPIO.cleanup()
    
    """
    camera = nanocamera.Camera()
    print(camera.isReady())
    """