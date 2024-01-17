from django.urls import re_path

from BaseGuiApp.consumers import GuiConsumer

urlpatterns = [
    re_path(r"ws/gui/$", GuiConsumer.as_asgi(), name="gui"),
]