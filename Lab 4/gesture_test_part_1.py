# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import board
from adafruit_apds9960.apds9960 import APDS9960
import os


i2c = board.I2C()

apds = APDS9960(i2c)
apds.enable_proximity = True
apds.enable_gesture = True

def speak_text_festival(text):
    command = f'echo "{text}" | festival --tts'
    os.system(command)

# Uncomment and set the rotation if depending on how your sensor is mounted.
# apds.rotation = 270 # 270 for CLUE

print("voice test")

while True:
    gesture = apds.gesture()

    if gesture == 0x01:
        print("up")
        speak_text_festival("up")
    elif gesture == 0x02:
        print("down")
        speak_text_festival("down")
    elif gesture == 0x03:
        print("left")
        speak_text_festival("left")
    elif gesture == 0x04:
        print("right")
        os.system("aplay b_minor_note.wav &")