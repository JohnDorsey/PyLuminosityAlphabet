import pygame



def arrange_horizontal_bar_surfaces(surfaces_to_arrange):
    lineHeightSum = sum(lineSurface.get_height() for lineSurface in surfaces_to_arrange)
    lineWidthMax = max(lineSurface.get_width() for lineSurface in surfaces_to_arrange)
    print(f"{lineWidthMax=}, {lineHeightSum=}")
    
    destSurface = pygame.Surface((lineWidthMax, lineHeightSum))
    assert isinstance(destSurface, pygame.Surface)
    
    y = 0
    for lineIndex, lineSurface in enumerate(surfaces_to_arrange):
        destSurface.blit(lineSurface, (0, y))
        y += lineSurface.get_height()
        
    return destSurface
    
    
    
def mirror_over_negative_diagonal(surface):
    surface = pygame.transform.rotate(surface, 90)
    surface = pygame.transform.flip(surface, False, True)
    return surface
    
    
def arrange_vertical_bar_surfaces(surfaces_to_arrange):
    surfacesToUse = [mirror_over_negative_diagonal(surface) for surface in surfaces_to_arrange]
    result = arrange_horizontal_bar_surfaces(surfacesToUse)
    result = mirror_over_negative_diagonal(result)
    return result