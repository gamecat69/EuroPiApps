from europi import *
from time import ticks_diff, ticks_ms, sleep
from random import randint, uniform
from europi_script import EuroPiScript
import machine

'''
Probapoly
author: Nik Ansell (github.com/gamecat69)

A polyrhythmic sequencer with probability

digital_in: Clock input
analog_in: Different mode, adjusted by setting self.ainMode as follows:
- Mode 1: Analogue input voltage adjusts the upper poly value
- Mode 2: Analogue input voltage adjusts the upper poly value
- Mode 3: Analogue input voltage adjusts the probabilities of outputs 2,3,5,6 sending gates
- Mode 4: Analogue input toggles double time feature


button_1: Short press (<500ms): Reduce pattern length (When manualPatternLengthFeature is True). Long Press (>500ms): Toggle doubletime feature
button_2: Short press (<500ms): Reduce pattern length (When manualPatternLengthFeature is True). Long Press (>500ms): Toggle Manual pattern length feature

knob_1: Select upper polyrhythm value
knob_2: Select lower polyrhythm value

output_1: Gate upper polyrhythm
output_2: Gate upper polyrhythm (50% probability)
output_3: Gate upper polyrhythm (25% probability)
output_4: Gate lower polyrhythm
output_5: Gate lower polyrhythm (50% probability)
output_6: Gate lower polyrhythm (50% probability)

'''

class Probapoly(EuroPiScript):
    def __init__(self):
        
        # Needed if using europi_script
        super().__init__()

        # Variables
        self.step = 1
        self.clockStep = 0
        self.resetTimeout = 2000
        self.maxPolyVal = 32
        self.upper = 1
        self.lower = 3
        self.ainValue = 0
        self.upperBernoulliProb = 50
        self.lowerBernoulliProb = 50
        self.upperProb1 = 50
        self.upperProb2 = 25
        self.lowerProb1 = 50
        self.lowerProb2 = 25
        self.doubleTime = False
        self.doubleTimeManualOverride = False
        self.UPPER_BUTTON_PRESS_TIME_LIMIT = 3000 # Used as a workaround to stop phantom button presses (Issue 132)
        self.SHORT_BUTTON_PRESS_TIME_THRESHOLD = 500
        self.gateVoltage = 10
        self.ainModes = ['U', 'L', 'P', 'D']

        self.loadState()

        @din.handler
        def clockRising():
            for cv in cvs:
                cv.off()
            self.handleClock()
            self.clockStep +=1
            self.step += 1

            # Reached end of pattern, or a shorter pattern is now needed (based on upper and lower values), reset step to 0
            if self.step > self.patternLength:
                self.step = 1

        @din.handler_falling
        def clockFalling():
            for cv in cvs:
                cv.off()
            if self.doubleTimeManualOverride or self.doubleTime:
                self.handleClock()
                self.clockStep +=1
                self.step += 1

                # Reached end of pattern, or a shorter pattern is now needed, reset step to 1
                if self.step > self.patternLength:
                    self.step = 1

        @b1.handler_falling
        def b1Pressed():
            if ticks_diff(ticks_ms(), b1.last_pressed()) > self.SHORT_BUTTON_PRESS_TIME_THRESHOLD and ticks_diff(ticks_ms(), b1.last_pressed()) < self.UPPER_BUTTON_PRESS_TIME_LIMIT:
                
                if self.ainMode < len(self.ainModes):
                    self.ainMode += 1
                else:
                    self.ainMode = 1
                    self.doubleTime = False

                if self.ainMode == 4:
                    # toggle double-time feature
                    self.doubleTime = True
                else:
                    self.doubleTime = False

            else:
            # Short press, decrease manual pattern length if self.manualPatternLengthFeature is True
                if self.manualPatternLengthFeature:
                    self.manualPatternLength -= 1
                    self.patternLength = self.manualPatternLength
            
            self.saveState()

        @b2.handler_falling
        def b2Pressed():
            if ticks_diff(ticks_ms(), b2.last_pressed()) > self.SHORT_BUTTON_PRESS_TIME_THRESHOLD and ticks_diff(ticks_ms(), b2.last_pressed()) < self.UPPER_BUTTON_PRESS_TIME_LIMIT:
                # Toggle manualPatternLengthFeature
                self.manualPatternLengthFeature = not self.manualPatternLengthFeature
                if self.manualPatternLengthFeature:
                    self.patternLength = self.manualPatternLength
            else:
            # Short press, increase manual pattern length if self.manualPatternLengthFeature is True
                if self.manualPatternLengthFeature:
                    self.manualPatternLength += 1
                    self.patternLength = self.manualPatternLength
            self.saveState()

    ''' Save working vars to a save state file'''
    def saveState(self):
        self.state = {
            "ainMode": self.ainMode,
            "manualPatternLengthFeature": self.manualPatternLengthFeature,
            "manualPatternLength": self.manualPatternLength
        }
        self.save_state_json(self.state)


    ''' Load a previously saved state, or initialize working vars, then save'''
    def loadState(self):
        self.state = self.load_state_json()
        self.ainMode = self.state.get("ainMode", 1)
        self.manualPatternLengthFeature = self.state.get("manualPatternLengthFeature", False)
        self.manualPatternLength = self.state.get("manualPatternLength", 32)
        if self.manualPatternLength:
            self.patternLength = self.manualPatternLength
        else:
            self.patternLength = self.lcm(self.upper, self.lower)
        self.saveState()

    def handleClock(self):
        
        # Play upper gate
        if self.step % self.upper == 0:    
            cv1.voltage(self.gateVoltage)

        # Output trigger with fixed and unrelated probabilities
            if randint(0,99) < self.upperProb1:
                cv2.voltage(self.gateVoltage)

            if randint(0,99) < self.upperProb2:
                cv3.voltage(self.gateVoltage)

        # Play lower gate
        if self.step % self.lower == 0:
            cv4.voltage(self.gateVoltage)

            # Output trigger with fixed and unrelated probabilities
            if randint(0,99) < self.lowerProb1:
                cv5.voltage(self.gateVoltage)

            if randint(0,99) < self.lowerProb2:
                cv6.voltage(self.gateVoltage)

    # Generate pattern length by finding the lowest common multiple (LCM) and greatest common divisor (GCD)
    # https://www.programiz.com/python-programming/examples/lcm
    def lcm(self, x, y):
        return (x*y)//self.computeGcd(x,y)

    def computeGcd(self, x, y):
        while(y):
            x, y = y, x % y
        return x

    def getUpper(self):
        # Mode 1, use the analogue input voltage to set the upper ratio value
        if self.ainValue > 0.9 and self.ainMode == 1:
            self.upper = int((self.maxPolyVal / 100) * self.ainValue) + 1
        else:
            self.upper = k1.read_position(self.maxPolyVal) + 1

    def getLower(self):
        # Mode 2, use the analogue input voltage to set the lower ratio value
        if self.ainValue > 0.9 and self.ainMode == 2:
            self.lower = int((self.maxPolyVal / 100) * self.ainValue) + 1
        else:
            self.lower = k2.read_position(self.maxPolyVal) + 1

    def getAinValue(self):
        self.ainValue = 100 * ain.percent()

    def updateScreen(self):
        # Clear the screen
        oled.fill(0)

        rectLeftX = 20
        rectRightX = 44
        rectLength = 20
 
        # Calculate where the steps should be using left justification
        if self.step <= 9:
            stepLeftX = 86
        elif self.step > 9 and self.step <= 99:
            stepLeftX = 78
        else:
            stepLeftX = 70

        # current step
        oled.text(str(self.step) + '|' + str(self.patternLength), stepLeftX, 0, 1)

        # Upper + lower values
        oled.text(str(self.upper), 0, 6, 1)
        oled.rect(0 , 17, 16, 1, 1)
        oled.text(str(self.lower), 0, 22, 1)

        # probabilities
        oled.rect(rectLeftX, 6, rectLength, 8, 1)
        oled.fill_rect(rectLeftX, 6, self.upperProb1//5, 8, 1)
        oled.rect(rectRightX, 6, rectLength, 8, 1)
        oled.fill_rect(rectRightX, 6, self.upperProb2//5, 8, 1)
        oled.rect(rectLeftX, 22, rectLength, 8, 1)
        oled.fill_rect(rectLeftX, 22, self.lowerProb1//5, 8, 1)
        oled.rect(rectRightX, 22, rectLength, 8, 1)
        oled.fill_rect(rectRightX, 22, self.lowerProb2//5, 8, 1)

        oled.text(str(self.ainModes[self.ainMode-1]), 90, 22, 1)

        if self.doubleTimeManualOverride or self.doubleTime:
            oled.text('!!', 100, 22, 1)
        if self.manualPatternLengthFeature:
            oled.text('M', 119, 22, 1)
        oled.show()

    def main(self):
        while True:
            self.getLower() 
            self.getUpper()
            self.getAinValue()
            self.updateScreen()

            # Ain CV toggles doubleTime feature
            if self.ainMode == 4:
                if self.ainValue > 50:
                    self.doubleTime = True
                else:
                    self.doubleTime = False
            # Ain CV controls probability
            if self.ainMode == 3:
                if self.ainValue >= 0.9:
                    self.upperProb1 = int(self.ainValue * 2)
                    self.upperProb2 = int(self.ainValue * 1)
                    self.lowerProb1 = int(self.ainValue * 2)
                    self.lowerProb2 = int(self.ainValue * 1)
                else:
                    self.upperProb1 = 0
                    self.upperProb2 = 0
                    self.lowerProb1 = 0
                    self.lowerProb2 = 0
            else:
                self.upperProb1 = 50
                self.upperProb2 = 25
                self.lowerProb1 = 50
                self.lowerProb2 = 25

            if not self.manualPatternLengthFeature:
                self.patternLength = self.lcm(self.upper, self.lower)

            # If I have been running, then stopped for longer than reset_timeout, reset the steps and clock_step to 0
            if self.clockStep != 0 and ticks_diff(ticks_ms(), din.last_triggered()) > self.resetTimeout:
                self.step = 1
                self.clockStep = 0

if __name__ == '__main__':
    dm = Probapoly()
    dm.main()


