
def validated_color(color):
    assert len(color) >= 3
    if not len(color) == 3:
        assert color[3] in [0, 255], "custom alpha not supported"
    color = color[:3]
    return color
    
def luminosity_int_to_float(value):
    return float(value)/(3.0*256.0)

def get_color_luminosity_int(color):
    color = validated_color(color)
    return sum(color)
    
def get_color_luminosity_float(color):
    return luminosity_int_to_float(get_color_luminosity_int(color))
    
    
def get_surface_absolute_luminosity_int(surface):
    colorGen = (surface.get_at((x,y)) for y in range(surface.get_height()) for x in range(surface.get_width()))
    return sum(get_color_luminosity_int(color) for color in colorGen)
    
def get_surface_absolute_luminosity_float(surface):
    return luminosity_int_to_float(get_surface_absolute_luminosity_int(surface))
    
    
def get_surface_relative_luminosity_float(surface):
    abs_lum_int = get_surface_absolute_luminosity_int(surface)
    area = surface.get_height() * surface.get_width()
    return luminosity_int_to_float(float(abs_lum_int)/float(area))