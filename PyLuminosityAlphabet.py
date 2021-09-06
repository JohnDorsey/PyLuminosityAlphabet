
import pathlib
from collections import namedtuple

import pygame
pygame.init()

KEYBOARD_DIGITS = "0123456789"
KEYBOARD_LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
KEYBOARD_SYMBOLS = " `~!@#$%^&*()-_=+[{]}\\|\\;:'\",<.>/?"
KEYBOARD_CHARS = KEYBOARD_DIGITS + KEYBOARD_LETTERS + KEYBOARD_SYMBOLS

SPECIALS_BASH = "$`*\"\\"

DEFAULT_FONT_PATH_STR = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"



TextElement = namedtuple("TextElement",["font_name","font_size","antialias","text","image","image_width","image_height","luminosity"])

def get_color_luminosity_f(color):
    assert len(color) >= 3
    if not len(color) == 3:
        assert color[3] in [0, 255], "custom alpha not supported"
    color = color[:3]
    return float(sum(color))/(3.0*256.0)
    
def get_surface_luminosity_f(surface):
    colorGen = (surface.get_at((x,y)) for y in range(surface.get_height()) for x in range(surface.get_width()))
    return sum(get_color_luminosity_f(color) for color in colorGen)
    
def path_from_str(path_str):
    font_path = pathlib.Path(font_path_text)
    return font_path
    
def make_font(path_str, size):
    return pygame.font.Font(path_from_str(path_str), size)
    

class FontProfile:
    def __init__(self, name, size, antialias):
        self._name, self._size = name, size
        self.font = make_font(name, size)
        self._antialias = antialias
        
    def get_char_picture(self, char):
        result = self.font.render(char, self._antialias, (255,255,255), (0,0,0))
        return result
    
    """
    def make_char_picture(self, char):
        self.char_pictures[char] = self.get_char_picture(char)
        
    def make_char_pictures(self, include=KEYBOARD_CHARS, exclude=""):
        self.char_pictures = dict()
        for char in include:
            if char in exclude:
                continue
            self.make_char_picture(char)
    """
    """
    def _gen_char_pictures(self, include=KEYBOARD_CHARS, exclude="")
        for char in include:
            if char in exclude:
                continue
            yield char, self.get_char_picture(
            """
            
    def get_alphabet_elements(self, include=KEYBOARD_CHARS, exclude=SPECIALS_BASH, force_monospace=False):
        result = []
        for char in include:
            if char in exclude:
                continue
            picture = self.get_char_picture(char)
            newProfileItem = TextElement(self._name, self._size, self._antialias, char, picture, picture.get_width(), picture.get_height(), get_surface_luminosity_f(picture))
            result.append(newProfileItem)
        #filter for monospace rulebreakers:
        if force_monospace:
            median_width = sorted(elem.image_width for elem in result)[len(result)//2]
            result = [item for item in result if item.image_width == median_width]
        result = sorted(result, key=(lambda item: item.luminosity))
        return result
        
    def get_alphabet_chars(self, **kwargs):
        return [elem.text for elem in self.get_alphabet_elements(**kwargs)]
        
    def get_alphabet_str(self, **kwargs):
        return "".join(self.get_alphabet_chars(**kwargs))
    
        
def main():
    while True:
        font_path_str = input("font path>")
        if font_path_str == "":
            font_path_str = DEFAULT_FONT_PATH_STR
            
        fontSize = input("fontSize>")
        if fontSize == "":
            fontSize = 10
        else:
            fontSize = int(fontSize)
            
        fontProfile = FontProfile(font_path_str, fontSize, True)
        print(fontProfile.get_alphabet_str())
        

#main()