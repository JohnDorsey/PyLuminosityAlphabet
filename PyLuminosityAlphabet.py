"""

PyLuminosityAlphabet.py by John Dorsey.

"""




import pathlib
from collections import namedtuple

import pygame
pygame.init()

import Characters



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
    font_path = pathlib.Path(path_str)
    return font_path
    
def make_font(path_str, size):
    return pygame.font.Font(path_from_str(path_str), size)
    
    
def iter_include_exclude(include, exclude):
    for item in include:
        if item in exclude:
            continue
        yield item
        
        
def filtered_for_uniform_density(src_gen, key_fun, segment_count):
    ResultEntry = namedtuple("ResultEntry", ["rawKey", "value"])
    def uniformityScore(key0, key1, key2):
        assert key0 <= key1 <= key2
        dists = [key1-key0, key2-key1]
        if 0 in dists:
            return 0
        return min(dists)/max(dists)
    result = [None for i in range(segment_count)]
    for i,item in enumerate(src_gen):
        itemRawKey = key_fun(item)
        assert 0 <= itemRawKey < 1, "bad key_fun output for {} at src_gen index {}.".format(item,i)
        itemSegIndex = int(round(itemRawKey * segment_count))
        assert 0 <= itemSegIndex < segment_count
        newEntry = ResultEntry(itemRawKey, item)
        oldEntry = result[itemSegIndex] 
        if oldEntry is not None:
            leftRawKey = result[itemSegIndex-1].rawKey if (itemSegIndex-1 >= 0 and result[itemSegIndex-1] is not None) else 0.0
            rightRawKey = result[itemSegIndex+1].rawKey if (itemSegIndex+1 < segment_count and result[itemSegIndex+1] is not None) else 1.0
            oldUniformity = uniformityScore(leftRawKey, oldEntry.rawKey, rightRawKey)
            newUniformity = uniformityScore(leftRawKey, newEntry.rawKey, rightRawKey)
            if newUniformity > oldUniformity:
                result[itemSegIndex] = newEntry
        else:
            result[itemSegIndex] = newEntry
    return [item.value for item in result if item is not None]
    
    

class FontProfile:
    def __init__(self, name, size, antialias, force_monospace, **other_kwargs):
        if name is None:
            name = DEFAULT_FONT_PATH_STR
        self._name, self._size = name, size
        self.font = make_font(name, size)
        self._antialias, self._force_monospace = antialias, force_monospace
        
        self._monospace_width = None
        if self._force_monospace:
            self.prepare_monospace_filtration(**other_kwargs)
            
        
    def __repr__(self):
        return "FontProfile(name={}, size={}, antialias={}, force_monospace={})".format(self._name, self._size, self._antialias, self._force_monospace)
        
        
    def prepare_monospace_filtration(self, test_chars=Characters.KEYBOARD_CHARS):
        #charPictureSizes = [(element.image_width, element.image_height) for element in self.gen_elements(include=test_chars)]
        test_elem_gen = self.gen_elements(include=test_chars, ignore_force_monospace=True)
        element_list = self.filtered_elem_list_for_consistent_width(test_elem_gen)
        if len(element_list) != len(test_chars):
            print("FontProfile.prepare_monospace_filtration: not monospace! After filtering test_chars for chars of the median width, its size shrank from {} to {}.".format(len(test_chars), len(element_list)))
        self._monospace_width = element_list[0].image_width
        
        
    def filtered_elem_list_for_consistent_width(self, element_list):
        if iter(element_list) is iter(element_list):
            print("FontProfile.filtered_elem_list_for_consistent_width: warning: received a generator! it will be consumed.")
            element_list = [item for item in element_list]
        if len(element_list) == 0:
            raise ValueError("element_list cannot be empty!")
        median_width = sorted(elem.image_width for elem in element_list)[len(element_list)//2]
        result = [item for item in element_list if item.image_width == median_width]
        return result
        
        
    def get_char_picture(self, char):
        result = self.font.render(char, self._antialias, (255,255,255), (0,0,0))
        return result
        
        
    def get_char_element(self, char):        
        picture = self.get_char_picture(char)
        result = TextElement(self._name, self._size, self._antialias, char, picture, picture.get_width(), picture.get_height(), get_surface_luminosity_f(picture)) 
        return result
    """
    def make_char_picture(self, char):
        self.char_pictures[char] = self.get_char_picture(char)
        
    def make_char_pictures(self, include=KEYBOARD_CHARS, exclude=""):
        self.char_pictures = dict()
        for char in iter_include_exclude(include, exclude):
            self.make_char_picture(char)
    """
    """
    def _gen_char_pictures(self, include=KEYBOARD_CHARS, exclude="")
        for char in iter_include_exclude(include, exclude):
            yield char, self.get_char_picture(
            """
            
    def gen_elements(self, include=Characters.KEYBOARD_CHARS, exclude=Characters.SPECIALS_BASH, ignore_force_monospace=False):
        """
        include may be a generator.
        exclude should be a set for best performance.
        """
        for char in iter_include_exclude(include, exclude):
            newElement = self.get_char_element(char)
            if (not ignore_force_monospace) and self._force_monospace:
                if newElement.image_width != self._monospace_width:
                    continue
            yield newElement
            
            
    def get_alphabet_elements(self, quick_force_monospace=False, **other_kwargs):
        elemGen = self.gen_elements(**other_kwargs)
        result = [item for item in elemGen]
        
        if quick_force_monospace:
            if self._force_monospace:
                print("{}: warning: using quick_force_monospace in combination with force_monospace is slow.".format(repr(self)))
            result = self.filtered_elem_list_for_consistent_width(result)
            
        result.sort(key=(lambda item: item.luminosity))
        return result
        
        
    def get_alphabet_chars(self, **kwargs):
        return [elem.text for elem in self.get_alphabet_elements(**kwargs)]
        
        
    def get_alphabet_str(self, **kwargs):
        return "".join(self.get_alphabet_chars(**kwargs))
    


def create_common_order(char_alphabets):
    """
    when reconciling alphabets:
        -each ordered pair of letters is either allowed or disallowed.
        -each letter has a cost of letters that can't be used if the letter is used.
        -if there are two groups of _compatible letters_, group A and group B, and they are the same size, and the combined cost of group A letters is smaller than the combined cost of group B letters, then group A should be preferred over group B.
    Certain Rules:
        c1. if two letters each only have the other as a cost, they can be exluded from further calculations, or one can be chosen at random.
        c2 (done). if this letter has more than one cost letter, and this letter's cost letters each only have this letter as their cost, ban this letter.
        c3. if two letters have costs that include each other and the other letters in their costs are all the same, they should be considered one letter until the choice between them is made, or in some other way, the fact that their cost can't really be 2 should be accounted for.
        c4. if a letter's cost is larger than the union of the costs of all other letters, it should be banned.
        cFinal. all previous rules should be applied again whenever any change occurs.
    Uncertain Rules:
        u1. if this group of letters is self-compatible and each of its letters have the same cost letters, and the size of the cost is larger smaller than the size of the group, use the group.        
    """
    
    firstCharAlphabet = char_alphabets[0]
    otherCharAlphabets = char_alphabets[1:]
    charCosts = dict()
    for i1, char1 in enumerate(firstCharAlphabet[:-1]):
        char1Cost = set()
        for i2, char2 in enumerate(firstCharAlphabet[i1:]):
            for otherCharAlphabet in otherCharAlphabets:
                if otherCharAlphabet.index(char2) < otherCharAlphabet.index(char1):
                    char1Cost.add(char2)
                    break
        charCosts[char1] = char1Cost
        
    bannedChars = set()
    
    def banChar(charToBan):
        assert charToBan not in bannedChars
        bannedChars.add(charToBan)
        for costChar in charCosts[charToBan]:
            charCosts[costChar].remove(charToBan)
        del charCosts[charToBan]
        
    def applyRuleC2():
        changeCount = 0
        for baseCharI, baseChar in enumerate(firstCharAlphabet):
            for costCharI, costChar in enumerate(charCosts[baseChar]):
                if not len(charCosts[costChar]) == 1:
                    #rule c2 can't ban baseChar.
                    break
                else:
                    assert baseChar in charCosts[costChar]
            else:
                #rule c2 can ban baseChar.
                changeCount += 1
                banChar(baseChar)
        return changeCount
                
    def applyRuleC4():
        changeCount = 0
        for baseChar in firstCharAlphabet:
            if baseChar in bannedChars:
                continue
            #this set is built again every time because it is a simpler way to handle the body of this loop having banned chars.
            #even if no other rules were present, this rule should be run again if it makes any changes.
            othersSet = set(item for costSub in charCosts.values() for item in costSub if item not in charCosts[baseChar])
            #othersSet = set(item for item in firstCharAlphabet if item not in bannedChars)
            if len(charCosts[baseChar]) > len(othersSet):
                #ban char
                changeCount += 1
                banChar(baseChar)
        return changeCount
            
    def applyRuleCFinal():
        while True:
            if applyRuleC2() > 0:
                continue
            if applyRuleC4() > 0:
                continue
            return
            
    applyRuleCFinal()
    
    def genFinalAllowableChars():
        for char in firstCharAlphabet:
            if char in bannedChars:
                continue
            charCost = charCosts[char]
            charCostSize = len(charCost)
            if charCostSize == 0:
                yield char
                banChar(char)
            elif charCostSize == 1:
                yield char
                banChar(char)
                for i, costChar in enumerate(charCost):
                    assert i == 0
                    banChar(costChar)
    
    result = "".join(genFinalAllowableChars())
    
    return result
    
            
            
        
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