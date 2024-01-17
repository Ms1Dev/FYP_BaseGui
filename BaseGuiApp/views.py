from django.shortcuts import render
from RPi_Hardware import oled

def Index(request):
    oled.print_text("Testttt", 1)
    return render(request, 'index.html')