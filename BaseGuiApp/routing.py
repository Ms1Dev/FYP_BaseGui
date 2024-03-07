from django.urls import path

from BaseGuiApp.consumers import GuiConsumer

urlpatterns = [
    path("ws/gui/", GuiConsumer.as_asgi(), name="gui"),
]