
import time
import board
import busio
import os
import qwiic_proximity
import adafruit_mpr121


def distance_to_volume(distance_cm):
    MAX_DISTANCE_CM = 60.96
    MAX_VOLUME = 70           

    if distance_cm >= MAX_DISTANCE_CM:
        percent = 0
    elif distance_cm <= 0:
        percent = MAX_VOLUME
    else:
        percent = int(MAX_VOLUME * (1 - (distance_cm / MAX_DISTANCE_CM)))

    # Set system Master volume
    os.system(f"amixer set 'Master' {percent}%")
    return percent



def runExample():
    i2c = busio.I2C(board.SCL, board.SDA)
    oProx = qwiic_proximity.QwiicProximity()
    mpr121 = adafruit_mpr121.MPR121(i2c)

    if oProx.connected == False:
        print("The Qwiic Proximity device isn't connected to the system. Please check your connection", file=sys.stderr)
        return

    oProx.begin()

    while True:
        for i in range(12):
            if mpr121[i].value: 
                print(f"Twizzler {i} touched!")
                if i == 0:
                    os.system("aplay note1.wav &")
                    break
                elif i == 1:
                    os.system("aplay note2.wav &")
                    break
                elif i == 2:
                    os.system("aplay note3.wav &")
                    break
                elif i == 3: 
                    os.system("aplay note4.wav &")
                    break
        proxValue = oProx.get_proximity()
        volPercent = distance_to_volume(proxValue)
        print("Proximity Value: %d" % proxValue)
        print("Volume set to: %d%%" % volPercent)

        time.sleep(0.15)  # Small delay to keep from spamming output messages.

if __name__ == '__main__':
	try:
		runExample()
	except (KeyboardInterrupt, SystemExit) as exErr:
		print("\nEnding Example 1")
		sys.exit(0)