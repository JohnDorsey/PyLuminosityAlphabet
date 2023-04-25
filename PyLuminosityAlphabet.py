"""

PyLuminosityAlphabet.py by John Dorsey.

"""




import pathlib
from collections import namedtuple
import itertools
import time
from typing import Iterable, Iterator, List, NoReturn


import pygame
pygame.init()

import Characters
from Characters import gen_chunks_as_lists
from Colors import get_surface_absolute_luminosity_int, get_surface_relative_luminosity_float
import Graphics



DEFAULT_FONT_PATH_STR = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

def stall_pygame():
    running = True
    while running:
        time.sleep(0.1)
        pygame.display.flip()
        for event in pygame.event.get():
            #print(event)
            #print(dir(event))
            #print(event.type)
            if event.type in [pygame.K_ESCAPE, pygame.KSCAN_ESCAPE, pygame.QUIT]:
                pygame.display.quit()
                running = False
                break
                

def assert_not_generator(input_seq):
    assert iter(input_seq) is not iter(input_seq), "received a generator!"


def iter_include_exclude(include, exclude):
    for item in include:
        if item in exclude:
            continue
        yield item
        
        
def gen_deduped(input_seq, key_fun=(lambda x: x)):
    historySet = set()
    for item in input_seq:
        itemKey = key_fun(item)
        if itemKey in historySet:
            continue
        else:
            historySet.add(itemKey)
            yield item
        
        
def surface_to_tuple_list_list(surf):
    # this is necessary because two identical pygame surfaces are not equal.
    result = []
    for y in range(surf.get_height()):
        for x in range(surf.get_width()):
            color = surf.get_at((x,y))
            assert len(color) == 4
            currentTuple = tuple(color[i] for i in range(4)) # pygame colors are not iterable.
            result.append(currentTuple)
    return result
    
def iter_flatly(data):
    for item in data:
        if hasattr(item, "__iter__"):
            for subItem in iter_flatly(item):
                yield subItem
        else:
            assert not hasattr(item, "__len__"), (item, type(item))
            yield item
            
assert list(iter_flatly([[1,2],[3,4],(5,),(6,7)])) == [1,2,3,4,5,6,7]
assert list(iter_flatly([[(1,2)],[(3,),(),4],((5,),(6,7))])) == [1,2,3,4,5,6,7]
            
class HashableList(list):
    def __init__(self, data):
        #print("init")
        list.__init__(self, data)
        #return self
    def __hash__(self):
        result = 0
        for item in self:
            result = hash(result + hash(item))
        return result
        
    def __repr__(self):
        return "HashableList({})".format(list.__repr__(self))

TextElement = namedtuple("TextElement",["font_name", "font_size", "antialias", "text", "image", "image_width", "image_height", "absolute_luminosity", "relative_luminosity"])





def path_from_str(path_str):
    return pathlib.Path(path_str)

def make_pygame_font(path_str, size):
    return pygame.font.Font(path_from_str(path_str), size)
    
    
    
    
    
    
    
    

def median_nosub(input_seq):
    storage = sorted(input_seq)
    return storage[len(storage)//2]
        
        
def gen_elems_with_exact_width(elems: Iterable[TextElement], width: int) -> Iterator[TextElement]:
    for elem in elems:
        if elem.image_width == width:
            yield elem
        else:
            continue
            
            
def filtered_elem_list_for_exact_width(element_list: Iterable[TextElement], width) -> List[TextElement]:
    assert_not_generator(element_list)
    result = list(gen_elems_with_exact_width(element_list, width))
    return result
        
        
def filtered_elem_list_for_consistent_width(element_list: Iterable[TextElement]) -> List[TextElement]:
    assert_not_generator(element_list)
    if len(element_list) == 0:
        raise ValueError("element_list cannot be empty!")
    median_width = median_nosub(elem.image_width for elem in element_list)
    return filtered_elem_list_for_exact_width(element_list, median_width)
    
    
    
    
class ValidationFailure(ValueError):
    pass
    
class UnusableCharError(ValueError):
    pass
    
    
def validate_metrics(font, char) -> NoReturn:
    # verify that the character is not negative-width, and that its advance and offset are equal (it is not weird). 
    # https://www.pygame.org/docs/ref/font.html#pygame.font.Font.metrics
    assert len(char) == 1
    charCode = ord(char)
    charMetrics = font.metrics(char)[0]
    if min(charMetrics) < 0:
        raise ValidationFailure("char code {}, metrics {}: had negative value.".format(charCode, charMetrics))
    if charMetrics[1] != charMetrics[-1]:
        raise ValidationFailure("char code {}, metrics {}: advance did not equal max x offset.".format(charCode, charMetrics))
    
    
    
    
    
class FullFont:
    def __init__(self, name, size, antialias, color=(255,255,255), background=(0,0,0)):
        self.name, self.size, self.antialias = (name, size, antialias)
        self.color, self.background = (color, background)
        self.pygame_font = make_pygame_font(name, size)
    
    def render_char(self, char):
        assert len(char) == 1
        return self.pygame_font.render(char, self.antialias, self.color, self.background)
    
    def metrics(self, text):
        return self.pygame_font.metrics(text)
        
    def char_to_element(self, char) -> TextElement:
        assert len(char) == 1
        picture = self.render_char(char)
        result = TextElement(
            self.name,
            self.size,
            self.antialias,
            char,
            picture,
            picture.get_width(),
            picture.get_height(),
            get_surface_absolute_luminosity_int(picture),
            get_surface_relative_luminosity_float(picture),
        ) 
        return result




class MonospaceFont(FullFont):
    # class NotMonospace:
    #     pass
        
        
    def __init__(self, full_font, test_chars=None):
        assert test_chars is not None
        self.test_chars = list(iter(test_chars))
        self.full_font = full_font
        self.monospace_width = None
        self._prepare_filtration(self.test_chars)
    
    """
    def __repr__(self):
        return f"MonospaceFont({self.full_font}, test_chars={self.test_chars!r})"
    """
        
    def _prepare_filtration(self, test_chars):
        assert self.monospace_width is None
        test_elem_list = [self.full_font.char_to_element(testChar) for testChar in test_chars]
        element_list = filtered_elem_list_for_consistent_width(test_elem_list)
        if len(element_list) != len(test_chars):
            print("MonospaceFont._prepare_filtration: not monospace! After filtering test_chars for chars of the median width, its size shrank from {} to {}.".format(len(test_chars), len(element_list)))
        
        self.monospace_width = element_list[0].image_width
        if test_elem_list[0].image_width != self.monospace_width:
            raise AssertionError("MonospaceFont._prepare_filtration: first test char is not of the median width!")
        
        
    def __getattr__(self, name):
        return getattr(self.full_font, name)
        
        
    def render_char(self, char):
        assert len(char) == 1
        result = self.full_font.render_char(char)
        if result.get_width() != self.monospace_width:
            raise UnusableCharError()
        else:
            return result
        
        
    def render_error_char(self):
        template = self.render_char(self.test_chars[0])
        for y in range(template.get_height()):
            for x in range(template.get_width()):
                color = ((0 if ((x+y)%2==0) else 255), 0, 0)
                template.set_at((x,y), color)
        return template
    
    

        
        
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
    



        
        
def deal_cards_to_hands(deck, hands):
    for handToModify, cardToAdd in itertools.zip_longest(itertools.cycle(hands), deck):
        if cardToAdd is None:
            break
        handToModify.append(cardToAdd)
        
        
def deal_chunks_to_hands(deck, hands, chunk_width):
    chunkGen = gen_chunks_as_lists(deck, chunk_width)
    deal_cards_to_hands(chunkGen, hands)
        

        
        
def columnize_text(text, line_length, column_width=None, column_header="", column_line_format="{content}"):
    if column_width is None:
        wrappingText = "\n".join("".join(chunk) for chunk in gen_chunks_as_lists(text, line_length))
        return [wrappingText]
    else:
        wrapColumnCount = line_length // column_width
        wrapColumns = [([] if column_header == "" else [column_header.replace("{column_index}", str(i))]) for i in range(wrapColumnCount)]
        
        deal_chunks_to_hands(text, wrapColumns, column_width)
            
        for wrapColumnIndex, wrapColumn in enumerate(wrapColumns):
            wrapColumns[wrapColumnIndex] = "\n".join(
                column_line_format.replace(
                    "{content}", "".join(wrapColumnLine)
                ).replace(
                    "{line_number}", str(lineNumber)
                ) for lineNumber, wrapColumnLine in enumerate(wrapColumn)
            )
        return wrapColumns
        
        
        
        
class BadDrawError(ValueError):
    """
    raised when the char that was just drawn breaks the rules set by the FontProfile.
    """
    pass
    
    
    

class FontProfile:
    def __init__(self, name, size, antialias=True, force_monospace=True, screen_metrics=False, test_chars=Characters.KEYBOARD_CHARS):
        if name is None:
            name = DEFAULT_FONT_PATH_STR
        self._name, self._size = name, size
        self._antialias = antialias
        self._force_monospace = force_monospace
        self._screen_metrics = screen_metrics
        
        fullFont = FullFont(name, size, antialias)
        if self._force_monospace:
            self.font = MonospaceFont(fullFont, test_chars=test_chars)
        else:
            self.font = fullFont
        
        
    def __repr__(self):
        return "FontProfile(name={}, size={}, antialias={}, force_monospace={}, screen_metrics={})".format(self._name, self._size, self._antialias, self._force_monospace, self._screen_metrics)
        
        
    def render_char(self, char) -> pygame.Surface:
        assert len(char) == 1
        if self._screen_metrics:
            try:
                validate_metrics(self.font, char)
            except ValidationFailure as vf:
                raise UnusableCharError("while screening metrics : {}.".format(vf))
        result = self.font.render_char(char)
        assert isinstance(result, pygame.Surface)
        return result
        
        
    def render_line(self, text) -> pygame.Surface:
        assert "\n" not in text
        surfacesToCombine = []
        for char in text:
            try:
                currentSurface = self.render_char(char)
            except UnusableCharError:
                currentSurface = self.font.render_error_char() # self.font should be monospace if this error is ever encountered anyway.
            surfacesToCombine.append(currentSurface)
        outputSurface = Graphics.join_surfaces_horizontally(surfacesToCombine, assure_uniform=False) # even in monospace fonts, some characters are taller than others, so don't assure uniform.
        return outputSurface
        
        
    def render_lines(self, text) -> pygame.Surface:
        surfacesToCombine = [self.render_line(line) for line in text.split("\n")]
        outputSurface = Graphics.join_surfaces_vertically(surfacesToCombine, assure_uniform=False) # some lines may have fewer chars than others, so don't assure uniform.
        return outputSurface
        
        
    def char_to_element(self, char) -> TextElement:
        return self.font.char_to_element(char)

            
    def _gen_elements(self, include=Characters.KEYBOARD_CHARS, exclude=Characters.SPECIAL_CHAR_SET) -> Iterator[TextElement]:
        """
        include may be a generator. exclude should be a set for best performance.
        """
        for char in iter_include_exclude(include, exclude):
            try:
                newElement = self.char_to_element(char)
            except UnusableCharError:
                continue
            yield newElement
            
            
    def gen_elements(self, visually_dedupe=False, **other_kwargs):
        elementIterator = self._gen_elements(**other_kwargs)
    
        if visually_dedupe:
            # raise NotImplementedError("not ready yet, currently excludes all items.")
            keyFun = (lambda elem: HashableList(iter_flatly(surface_to_tuple_list_list(elem.image))))
            return gen_deduped(elementIterator, key_fun=keyFun)
        else:
            return elementIterator
        
            
            
    def get_alphabet_elements(self, max_segment_count=None, **other_kwargs) -> List[TextElement]:
        """
        Create a list of elements representing characters in a luminosity alphabet.
        max_segment_count - if set, this filters elements for uniform density, dividing the space between 0.0 inclusive and 1.0 exclusive into segments and keeping a maximum of one character per segment. Good for reducing memory usage when processing thousands or millions of characters.
        """
        elemGen = self.gen_elements(**other_kwargs)
        if max_segment_count is not None:
            result = filtered_for_uniform_density(elemGen, (lambda inputElem: inputElem.relative_luminosity), max_segment_count)
        else:
            result = [item for item in elemGen]
            
        result.sort(key=(lambda item: item.absolute_luminosity))
        return result
        
        
    def get_preview_surface(self, text, width=None, aspect_ratio=2, **column_kwargs) -> pygame.Surface:
        if len(text) == 0:
            return pygame.Surface((0,0))
        assert isinstance(text, str)
        if width is None:
            lineLength = int((len(text)**0.5)*aspect_ratio)
        else:
            lineLength = width
        lineCount = len(text)//lineLength + (1 if len(text)%lineLength>0 else 0)
        assert (lineCount-1)*lineLength < len(text)
        #print("{} x {}.".format(lineLength, lineCount))
        
        wrapColumns = columnize_text(text, line_length=lineLength, **column_kwargs)
        
        wrapColumnSurfaces = [self.render_lines(wrapColumn) for wrapColumn in wrapColumns]
        result = Graphics.join_surfaces_horizontally(wrapColumnSurfaces)
        #print(result.get_size())
        return result
            
    
    def preview(self, text, **kwargs):
        if len(text) == 0:
            print("no text to preview.")
            return
        outputSurface = self.get_preview_surface(text, **kwargs)
        try:
            screen = pygame.display.set_mode(outputSurface.get_size())
            screen.blit(outputSurface, (0, 0))
            stall_pygame()
        finally:
            pygame.display.quit()
        
        
    def get_alphabet_chars(self, **kwargs):
        return [elem.text for elem in self.get_alphabet_elements(**kwargs)]
        
    def get_alphabet_ords(self, **kwargs):
        return [ord(char) for char in self.get_alphabet_chars(**kwargs)]
        
    def get_alphabet_ords_and_chars(self, **kwargs):
        return [(ord(char), char) for char in self.get_alphabet_chars(**kwargs)]
        
    def get_alphabet_str(self, **kwargs):
        return "".join(self.get_alphabet_chars(**kwargs))
    








#not fully tested!
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