import time
import subprocess
import os
import digitalio
import board
from PIL import Image, ImageDraw, ImageOps
import adafruit_rgb_display.st7789 as st7789
from time import strftime, sleep
import random

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.D5)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 16000000
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

def tile_gif_frame(base_image, frame_image, num_images):
    base_width, base_height = base_image.size

    # for the tiling case, we have a 9 hr period
    rows = num_images // 3 + 1
    cols = 3
    pasted_images = 0

    tile_width = base_width // 3
    tile_height = base_height // 3
    tile = frame_image.resize((tile_width, tile_height))

    for x in range(0, base_width, tile_width):
        for y in range(0, base_height, tile_height):
            if pasted_images >= num_images:
                return
            base_image.paste(tile, (x, y))
            pasted_images += 1

class Frame:
    def __init__(self, duration=0):
        self.duration = duration
        self.image = None

# inspired by https://learn.adafruit.com/pitft-linux-python-animated-gif-player/python-code
class AnimatedGif:
    def __init__(self, display, gif_path, num_images=1, bg_color=(0, 0, 0)):
        self.display = display
        self.gif_path = gif_path
        self.num_images = num_images
        self.bg_color = bg_color
        self.frames = []
        self.load_frames()
    
    def load_frames(self):
        gif = Image.open(self.gif_path)
        self.loop = gif.info.get("loop", 1)
        self.frames.clear()
        for i in range(gif.n_frames):
            gif.seek(i)
            frame = gif.convert("RGB")
            duration = 100
            self.frames.append((frame, duration))
    
    def play(self):
        while True:
            for frame, duration in self.frames:
                if self.num_images > 1:
                    tile_gif_frame(image, frame, self.num_images)
                else:
                    frame = frame.resize((width, height))
                    image.paste(frame, (0, 0))
                self.display.image(image, rotation)
                time.sleep(duration / 1000)
            if self.loop == 1:
                break
            if self.loop > 0:
                self.loop -= 1

def place_image_randomly(base_img, overlay_img, area, scale=1.0):
    base_img = base_img.convert("RGBA")
    overlay_img = overlay_img.convert("RGBA")

    w, h = overlay_img.size
    overlay_img = overlay_img.resize((int(w*scale), int(h*scale)), Image.ANTIALIAS)

    x0, y0, x1, y1 = area
    max_x = max(x0, x1 - overlay_img.width)
    max_y = max(y0, y1 - overlay_img.height)

    pos_x = random.randint(x0, max_x)
    pos_y = random.randint(y0, max_y)

    base_img.paste(overlay_img, (pos_x, pos_y), overlay_img)  

    return base_img

def take_bite(img, background_color=(0,0,0)):
    img = img.convert("RGB")  
    w, h = img.size

    radius = random.randint(int(w*0.05), int(w*0.125))
    cx = random.randint(radius, w - radius)
    cy = random.randint(radius, h - radius)

    draw = ImageDraw.Draw(img)
    draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=background_color)

    return img


class EatablePizza:
    def __init__(self, display, pizza_path, bg_color=(0,0,0)):
        self.display = display
        self.bg_color = bg_color
        self.pizza = Image.open(pizza_path).convert("RGB")
        self.pizza = self.pizza.resize((width, height))

    def display_pizza(self):
        self.display.image(self.pizza, rotation)

    def bite(self):
        self.pizza = take_bite(self.pizza, self.bg_color)
        self.display_pizza()


buttonA = digitalio.DigitalInOut(board.D23)   
buttonA.switch_to_input(pull=digitalio.Pull.UP)

# placeholder init
pizza_player = EatablePizza(disp, "pizza-eat-1.png")  
bite_refresh_time = 5

while True:
    hour = datetime.now().hour
    
    # morning -> dough rising -> preparation for the day (resting the dough)
    if 0 < hour <= 9:
        gif_path = "pizza_rise.gif"
        tiled_gif = AnimatedGif(disp, gif_path, hour)
        tiled_gif.play()  # non-blocking

    # workday -> baking -> generative process
    elif 10 <= hour <= 18:
        gif_path = "pizza_bake.gif"
        tiled_gif = AnimatedGif(disp, gif_path, 1)
        tiled_gif.play()  # non-blocking

    # evening -> eating pizza -> interactive with bites
    elif 19 <= hour <= 21:
        pizza_number = hour - 18
        pizza_path = f"pizza-eat-{pizza_number}.png"  # fallback
        pizza_player = EatablePizza(disp, pizza_path)
        pizza_player.display_pizza()

        last_bite_time = time.monotonic()
        while time.monotonic() - last_bite_time < bite_refresh_time:
            a_pressed = (buttonA.value == False)  
            if a_pressed:
                pizza_player.bite()
                print(f"Bite taken at hour {hour}")
                last_bite_time = time.monotonic()  
                time.sleep(0.05)
            else:
                time.sleep(0.02)

        pizza_player.display_pizza()
        print(f"Pizza refreshed for hour {hour}")

    # night -> cleaning -> resting for next day
    else:
        night_image = Image.open('pizza-wash.png').convert("RGB")
        night_image = night_image.resize((width, height))
        disp.image(night_image, rotation)
        a_pressed = (buttonA.value == False)  
        if a_pressed:
            print("Playing night animation")
            tiled_gif = AnimatedGif(disp, 'pizza-wash.gif', 1)
            tiled_gif.play() 
    time.sleep(0.05)

