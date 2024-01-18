import adafruit_ssd1306  
import board  
import digitalio  
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import threading

WIDTH = 128
HEIGHT = 64
ROWS = 4
ROW_HEIGHT = HEIGHT / ROWS

PIN = board.D10
led = digitalio.DigitalInOut(PIN)
led.direction = digitalio.Direction.OUTPUT
led.value = True
oled=adafruit_ssd1306.SSD1306_I2C(WIDTH,HEIGHT,board.I2C()) 
oled.fill(0)  
oled.show()  
font=ImageFont.load_default()  
image=Image.new('1',(WIDTH,HEIGHT))  
draw=ImageDraw.Draw(image)  
printLock = threading.Lock()

def print_text(text, row = 0, outline = 0):
    with printLock:
        startOfRow = row * ROW_HEIGHT + row
        draw.rectangle((0, startOfRow, WIDTH -1, startOfRow + ROW_HEIGHT), fill=0, outline=outline)
        draw.text((2, startOfRow +2), text, font=font, fill=255)  
        oled.image(image)  
        oled.show()  
