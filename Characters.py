
from collections import deque

KEYBOARD_DIGITS = "0123456789"
KEYBOARD_LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
KEYBOARD_SYMBOLS = " `~!@#$%^&*()-_=+[{]}\\|\\;:'\",<.>/?"
KEYBOARD_CHARS = KEYBOARD_DIGITS + KEYBOARD_LETTERS + KEYBOARD_SYMBOLS

SPECIALS_BASH = ["$", "`", "*", "\"", "\\"]

HEX_DIGITS = "0123456789abcdef"

def to_hex_str(value):
    result = deque([])
    while value > 0:
        result.appendleft(value%16)
        value //= 16
    return "".join(HEX_DIGITS[item] for item in result)

def gen_printable_unicode(src_gen=None, hex_length=4):
    assert hex_length in [4, 8]
    prefixChar = {4:"u", 8:"U"}[hex_length]
    if src_gen is None:
        src_gen = range(0, 16**hex_length)
    for value in src_gen:
        baseStr = to_hex_str(value).rjust(hex_length, HEX_DIGITS[0])
        try:
            char = eval("\"\\" + prefixChar + baseStr + "\"")
        except UnicodeError as ue:
            print("unicode error caused by prefix {} and baseStr {}.".format(prefixChar, baseStr))
            raise ue
        assert len(char) == 1
        if char.isprintable():
            yield char