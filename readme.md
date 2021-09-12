

Requires pygame

This program internally renders characters into one image each, and uses these
images to sort all of the characters by order of their actual luminosity.

The resulting alphabets are ideal for their specified font, font size, and
antialiasing setting.

FontProfile excludes non-monospace characters by default.


usage:
    
    import PyLuminosityAlphabet as pla
    
    fontProfile = pla.FontProfile(<Full path of target font>, <font size>)
    
    fontProfile.get_alphabet_str()
