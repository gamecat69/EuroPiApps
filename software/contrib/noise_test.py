from europi import *
from time import sleep
from machine import Pin, ADC, PWM, freq
from europi_script import EuroPiScript


class NoiseTest(EuroPiScript):
    def __init__(self):
        # Overclock the Pico for improved performance.
        machine.freq(250_000_000)
        self.testMode=''
        self.numDecPlaces = 6
        self.numSamples = 4096

    def startScreen(self):
        # Display start text
        oled.fill(0)
        oled.text('knob test: b1', 0, 0, 1)
        oled.text('ain test : b2', 0, 12, 1)
        oled.show()
        while True:
            if b1.value() == 1:
                self.testMode = 'knobs'
                break
            elif b2.value() == 1:
                self.testMode = 'ain'
                break
        self.startTest()

    def wait_for_b1(self, value):
        while b1.value() != value:
            sleep(0.05)

    def startTest(self):
        if self.testMode == 'knobs':
            
            # Knob 1 Test
            oled.fill(0)
            oled.text('k1 full ccw(min)', 0, 0, 1)
            oled.text('Press b1', 0, 12, 1)
            oled.show()
            self.wait_for_b1(1)
            self.wait_for_b1(0)
            lowVal = round(k1.percent(samples=self.numSamples), self.numDecPlaces)

            self.wait_for_b1(1)
            self.wait_for_b1(0)

            oled.fill(0)
            oled.text('k1 full cw(max)', 0, 0, 1)
            oled.text('Press b1', 0, 12, 1)
            oled.show()
            self.wait_for_b1(1)
            self.wait_for_b1(0)
            highVal = round(k1.percent(samples=self.numSamples), self.numDecPlaces)

            oled.fill(0)
            oled.text('low:' + str(lowVal), 0, 0, 1)
            oled.text('high:' + str(highVal), 0, 9, 1)
            oled.text('Press b1', 0, 18, 1)
            oled.show()
            self.wait_for_b1(1)
            self.wait_for_b1(0)

            # Knob 2 Test
            oled.fill(0)
            oled.text('k2 full ccw(min)', 0, 0, 1)
            oled.text('Press b1', 0, 9, 1)
            oled.show()
            self.wait_for_b1(1)
            self.wait_for_b1(0)
            lowVal = round(k2.percent(samples=self.numSamples), self.numDecPlaces)

            oled.fill(0)
            oled.text('k2 full cw(max)', 0, 0, 1)
            oled.text('Press b1', 0, 9, 1)
            oled.show()
            self.wait_for_b1(1)
            self.wait_for_b1(0)
            highVal = round(k2.percent(samples=self.numSamples), self.numDecPlaces)

            oled.fill(0)
            oled.text('low:' + str(lowVal), 0, 0, 1)
            oled.text('high:' + str(highVal), 0, 9, 1)
            oled.text('Press b1', 0, 18, 1)
            oled.show()
            self.wait_for_b1(1)
            self.wait_for_b1(0)

        elif self.testMode == 'ain':
            oled.fill(0)
            oled.text('Unplug all', 0, 0, 1)
            oled.text('Press b1', 0, 12, 1)
            oled.show()
            self.wait_for_b1(1)
            self.wait_for_b1(0)
            lowVal = round(ain.percent(samples=self.numSamples), self.numDecPlaces)
            oled.fill(0)
            oled.text('low:' + str(lowVal), 0, 0, 1)
            oled.text('Press b1', 0, 9, 1)
            oled.show()
            self.wait_for_b1(1)
            self.wait_for_b1(0)

        self.testMode=''
        self.startScreen()

    def main(self):

        usb = Pin(24, Pin.IN)
        
        if usb.value() == 1:
            oled.fill(0)
            oled.text('Rack power on?', 0, 0, 1)
            oled.text('Yes? Press b1', 0, 12, 1)
            oled.show()
            self.wait_for_b1(1)
            self.wait_for_b1(0)

        self.startScreen()

if __name__ == '__main__':
    m = NoiseTest()
    m.main()
