import pygame



"""
def arrange_horizontal_bar_surfaces(surfaces_to_arrange):
    lineHeightSum = sum(lineSurface.get_height() for lineSurface in surfaces_to_arrange)
    lineWidthMax = max(lineSurface.get_width() for lineSurface in surfaces_to_arrange)
    # print(f"{lineWidthMax=}, {lineHeightSum=}")
    
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
"""



def join_surfaces_horizontally(surfaces, *, assure_uniform=False, spacing=0, transparent=True):
    assert spacing >= 0
    if iter(surfaces) is iter(surfaces):
        surfaces = list(surfaces)
    assert len(surfaces) > 0
    resultWidth = sum(surf.get_width() for surf in surfaces)+spacing*(len(surfaces)-1)
    resultHeight = max(surf.get_height() for surf in surfaces)
    if assure_uniform:
        assert all(surf.get_height() == resultHeight for surf in surfaces), f"not uniform! sizes are {[surf.get_size() for surf in surfaces]}. Their heights should be equal."
    result = pygame.Surface((resultWidth, resultHeight), **({"flags":pygame.SRCALPHA} if transparent else {}))
    
    x = 0
    for surf in surfaces:
        result.blit(surf, (x, 0))
        x += surf.get_width()+spacing
        
    return result


def mirror_over_negative_diagonal(surface):
    surface = pygame.transform.rotate(surface, 90)
    surface = pygame.transform.flip(surface, False, True)
    return surface


def join_surfaces_vertically(surfaces, **kwargs):
    surfacesToUse = [mirror_over_negative_diagonal(surface) for surface in surfaces]
    result = join_surfaces_horizontally(surfacesToUse, **kwargs)
    result = mirror_over_negative_diagonal(result)
    return result
    