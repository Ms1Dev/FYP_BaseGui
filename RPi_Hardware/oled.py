import adafruit_ssd1306  
import board  
import digitalio  
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import threading

WIDTH = 128
HEIGHT = 64
ROWS = 5
ROW_HEIGHT = HEIGHT / ROWS -1

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


class Row:
    def __init__(self, text, filled = False, outline = False) -> None:
        self.text = text
        self.filled = filled
        self.outline = outline

    def print(self, index):
        with printLock:
            startOfRow = index * ROW_HEIGHT + index
            textColour = 255
            fill = 0
            outline = 0
            if self.filled:
                fill = 255
                textColour = 0
            if self.outline:
                outline = 255 - fill
            draw.rectangle((0, startOfRow, WIDTH -1, startOfRow + ROW_HEIGHT), fill=fill, outline=outline)
            draw.text((2, startOfRow), self.text, font=font, fill=textColour)  
            oled.image(image)  
            oled.show()  


rows : Row = []


def print_rectangle(row):
    with printLock:
        startOfRow = row * ROW_HEIGHT + row
        draw.rectangle((0, startOfRow, WIDTH -1, startOfRow + ROW_HEIGHT -1), fill=0)
        oled.image(image)  
        oled.show()  


def refresh():
    row_count = len(rows)
    for i in range(0, ROWS):
        if i < row_count:
            rows[i].print(i)
        else:
            print_rectangle(i)

