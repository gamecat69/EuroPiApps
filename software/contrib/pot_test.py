from europi import *
import machine
from europi_script import EuroPiScript

class PotTest(EuroPiScript):
    def __init__(self):
        pass

    def main(self):
        while True:
            # get pot values

            self.k1percent = round(k1.percent() * 100,1)
            self.k1readposition = k1.read_position(100)

            self.k2percent = round(k2.percent() * 100,1)
            self.k2readposition = k2.read_position(100)

            # display on screen
            oled.fill(0)
            oled.text('k1: ' + str(self.k1percent) + '% | ' + str(self.k1readposition), 0, 0, 1)
            oled.text('k2: ' + str(self.k2percent) + '% | ' + str(self.k2readposition), 0, 12, 1)
            oled.show()

if __name__ == '__main__':
    m = PotTest()
    m.main()