import adafruit_ssd1306  
import board  
import digitalio  
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

PIN = board.D10
led = digitalio.DigitalInOut(PIN)
led.direction = digitalio.Direction.OUTPUT

WIDTH = 128
HEIGHT = 64
ROWS = 4
ROW_HEIGHT = HEIGHT / ROWS

def screen_on():
    led.value = True

def screen_off():
    led.value = False

def print_text(text, row = 0):
    oled=adafruit_ssd1306.SSD1306_I2C(WIDTH,HEIGHT,board.I2C()) 
    oled.fill(0)  
    oled.show()  
    font=ImageFont.load_default()  
    image=Image.new('1',(WIDTH,HEIGHT))  
    draw=ImageDraw.Draw(image)  
    draw.text((0, row * ROW_HEIGHT), text, font=font, fill=255)  
    oled.image(image)  
    oled.show()  


