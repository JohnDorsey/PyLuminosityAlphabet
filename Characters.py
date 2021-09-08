
from collections import deque
import difflib

try:
    import emoji
except ImportError as ie:
    print("emoji module is not installed. Some safeguards against poorly-behaved characters won't be available. Try:\n    pip install emoji")


KEYBOARD_DIGITS = "0123456789"
KEYBOARD_LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
KEYBOARD_SYMBOLS = " `~!@#$%^&*()-_=+[{]}\\|\\;:'\",<.>/?"
KEYBOARD_CHARS = KEYBOARD_DIGITS + KEYBOARD_LETTERS + KEYBOARD_SYMBOLS

SPECIALS_BASH = ["$", "`", "*", "\"", "\\"]

HEX_DIGITS = "0123456789abcdef"




def gen_take_upto(src_gen, count):
    for i, item in enumerate(src_gen):
        if i == count:
            return
        yield item

def join_upto(src_gen, count, delimiter=""):
    assert count >= 0
    return delimiter.join(gen_take_upto(src_gen, count))

def diff_compact(str_a, str_b, include_unchanged=False, include_indices=False):
    diffResult = difflib.ndiff(str_a, str_b)
    result = dict()
    for index, item in enumerate(diffResult):
        assert len(item) == 3
        key = item[0]
        if key == " " and not include_unchanged:
            continue
        if key not in result:
            result[key] = []
        result[key].append((index, item[2]) if include_indices else item[2])
    return result


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
            
def gen_wellbehaved_unicode(**kwargs):
    for char in gen_printable_unicode(**kwargs):
        if emoji.emoji_count(char) > 0:
            continue
        yield char
        
        
            

def annotate_characters(src_gen):
    print("this method returns a dictionary. Make sure it is stored somewhere.")
    result = dict()
    for i, char in enumerate(src_gen):
        userInput = input("index {}: value {}:".format(i, ord(char)) + char + char + char + char + char + ">")
        result[char] = userInput
    return result
            
    