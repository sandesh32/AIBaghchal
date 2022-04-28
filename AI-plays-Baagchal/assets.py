import os
import  sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Assets(object):
    def __init__(self):
        self.blank_image_path = "images/blanks/blank_64x64.png"
        self.tiger_image_path = "images/tigers/tiger_64x64.png"
        self.goat_image_path = "images/goats/goat_64x64.png"
        self.configuration_path = "settings.conf"

        # self.blank_image_path = resource_path("blank_64x64.png")
        # self.tiger_image_path = resource_path("tiger_64x64.png")
        # self.goat_image_path = resource_path("goat_64x64.png")
        # self.configuration_path = resource_path("settings.conf")