import pygame

image_cache = {}

def load_and_scale_image(image_path, cell_size):
    if image_path in image_cache:
        return image_cache[image_path]
    
    image = pygame.image.load(image_path)
    original_width, original_height = image.get_size()
    scaling_factor = min(cell_size / original_width, cell_size / original_height)
    new_width = int(original_width * scaling_factor)
    new_height = int(original_height * scaling_factor)
    scaled_image = pygame.transform.smoothscale(image, (new_width, new_height))
    
    image_cache[image_path] = scaled_image
    return scaled_image