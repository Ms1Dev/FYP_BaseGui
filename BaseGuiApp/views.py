from django.shortcuts import render
from BaseGuiApp.hardware import oled


def Index(request):
    oled.print_text("Testttt", 1)
    return render(request, 'index.html')