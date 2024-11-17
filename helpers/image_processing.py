import pygame

def load_and_scale_image(image_path, cell_size):
    image = pygame.image.load(image_path)
    original_width, original_height = image.get_size()
    scaling_factor = min(cell_size / original_width, cell_size / original_height)
    new_width = int(original_width * scaling_factor)
    new_height = int(original_height * scaling_factor)
    return pygame.transform.smoothscale(image, (new_width, new_height))


def calculate_draw_position(x, y, image, cell_size):
    image_width, image_height = image.get_size()
    draw_x = x * cell_size + (cell_size - image_width) // 2
    draw_y = y * cell_size + (cell_size - image_height) // 2
    return draw_x, draw_y