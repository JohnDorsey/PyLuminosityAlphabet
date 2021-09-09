
from collections import deque
import difflib
import itertools
import unicodedata


try:
    import emoji
except ImportError as ie:
    print("emoji module is not installed. Some safeguards against poorly-behaved characters won't be available. Try:\n    pip install emoji")


KEYBOARD_DIGITS = "0123456789"
KEYBOARD_LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
KEYBOARD_SYMBOLS = " `~!@#$%^&*()-_=+[{]}\\|\\;:'\",<.>/?"
KEYBOARD_CHARS = KEYBOARD_DIGITS + KEYBOARD_LETTERS + KEYBOARD_SYMBOLS



SPECIAL_CHARS_DICT = {"BASH":["$", "`", "*", "\"", "\\"]}

SNEAKY_ORDS_DICT = {"GNOME_XTERM": [789, 829, 1557, 1612, 3785, 825, 781, 1619]}



HEX_DIGITS = "0123456789abcdef"



def gen_chunks_as_lists(thing, chunk_length):
    i = 0
    while i*chunk_length < len(thing):
        yield thing[i*chunk_length:(i+1)*chunk_length]
        i += 1

def gen_take_upto(src_gen, count):
    for i, item in enumerate(src_gen):
        if i == count:
            return
        yield item
        
def gen_consume_deque(src_deque):
    while True:
        try:
            newItem = src_deque.popleft()
        except IndexError:
            return
        yield newItem
    assert False

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
    specialCharSet = {char for sublist in SPECIAL_CHARS_DICT.values() for char in sublist}
    sneakyOrdSet = {num for sublist in SNEAKY_ORDS_DICT.values() for num in sublist}
    for char in gen_printable_unicode(**kwargs):
        if unicodedata.category(char) in {"Cc", "Cf"}:
            continue
        if emoji.emoji_count(char) > 0:
            continue
        if char in specialCharSet:
            continue
        if ord(char) in sneakyOrdSet:
            continue
        yield char
        
        
            

def annotate_characters(src_gen):
    print("this method returns a dictionary. Make sure it is stored somewhere.")
    result = dict()
    for i, char in enumerate(src_gen):
        userInput = input("index {}: value {}:".format(i, ord(char)) + char + char + char + char + char + ">")
        result[char] = userInput
    return result
            
            
def identify_safe_chars(src_list, goods=None, bads=None, width=32, height=24, doublespace=False, reps=1):
    assert isinstance(goods, set)
    assert isinstance(bads, set)
    #if goods is None:
    #    goods = set()
    #if bads is None:
    #    bads = set()
    recycleDeque = deque([])
    result = {"goods":goods, "bads":bads, "recycle":recycleDeque}
    #chunkGen = gen_chunks_as_lists(src_list)
    srcListItemGen = (char for char in src_list)
    
    def recycleFrom(data):
        for item in data:
            assert type(item) == str
            assert len(item) == 1
            recycleDeque.append(item)
    
    while True:
        srcCharGen = itertools.chain(srcListItemGen, gen_consume_deque(recycleDeque))
        currentBlock = [(i, "".join(gen_take_upto(srcCharGen, width))) for i in range(height)]
        
        lengthGuageStr = "    :"+("#"*width*reps)
        print(lengthGuageStr)
        for row in currentBlock:
            if row[1] == "":
                continue
            print(str(row[0]).rjust(4," ") + "(" + "".join(char*reps for char in row[1]) + ")")
            if doublespace:
                print("")
        print(lengthGuageStr)
        
        backToTop = False
        userInput = input("space-delimited row indices or \"<width|height|doublespace|reps>=<an int>\" or \"q\">")
        if userInput.startswith("width="):
            width = int(userInput[6:])
            backToTop = True
        if userInput.startswith("height="):
            height = int(userInput[7:])
            backToTop = True
        if userInput.startswith("doublespace="):
            doublespace = int(userInput[12:])
            backToTop = True
        if userInput.startswith("reps="):
            reps = int(userInput[5:])
            backToTop = True
        if backToTop:
            for row in currentBlock:
                recycleFrom(row[1])
            continue
        if userInput == "q":
            return result
        if userInput == "":
            userComplaints = []
        else:
            userComplaints = []
            for word in userInput.split(" "):
                if ".." in word:
                    rangeStartStr, rangeEndStr = word.split("..")
                    rangeStart, rangeEnd = int(rangeStartStr), int(rangeEndStr)
                    for badIndex in range(rangeStart, rangeEnd+1):
                        userComplaints.append(badIndex)
                else:
                    userComplaints.append(int(word))
        
        for rowIndex, rowText in currentBlock:
            if rowIndex in userComplaints:
                if width == 1:
                    assert len(rowText) == 1
                    bads.add(rowText)
                else:
                    recycleFrom(rowText)
            else:
                for char in rowText:
                    goods.add(char)
    print("ending abnormally.")
    return result
            

    
    
    
    
    
    
    