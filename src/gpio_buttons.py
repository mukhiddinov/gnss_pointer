import time
import RPi.GPIO as GPIO

class ButtonPins:
    def __init__(self, pointer_pin: int, cancel_pin: int, logger):
        self.pointer_pin = pointer_pin
        self.cancel_pin = cancel_pin
        self.log = logger

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pointer_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.cancel_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def cleanup(self):
        GPIO.cleanup()

    @staticmethod
    def _wait_release(pin: int):
        while GPIO.input(pin) == GPIO.LOW:
            time.sleep(0.03)

    def poll(self):
        """
        Return: "pointer" / "cancel" / None
        """
        if GPIO.input(self.pointer_pin) == GPIO.LOW:
            self._wait_release(self.pointer_pin)
            return "pointer"
        if GPIO.input(self.cancel_pin) == GPIO.LOW:
            self._wait_release(self.cancel_pin)
            return "cancel"
        return None
