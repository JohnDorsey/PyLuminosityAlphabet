
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

def gen_printable_unicode_16(src_gen=None):
    if src_gen is None:
        src_gen = range(0, 16**4)
    for value in src_gen:
        baseStr = to_hex_str(value).rjust(4, HEX_DIGITS[0])
        char = eval("\"\\u" + baseStr + "\"")
        assert len(char) == 1
        if char.isprintable():
            yield char