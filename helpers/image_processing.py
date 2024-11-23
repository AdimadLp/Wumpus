import pygame

# Dictionary to cache loaded images
image_cache = {}


def load_and_scale_image(image_path, cell_size):
    """
    Load an image from the given path, scale it to fit within the cell size, and cache it.

    Parameters:
    -----------
    image_path : str
        The file path to the image.
    cell_size : int
        The size of the cell to scale the image to fit within.

    Returns:
    --------
    pygame.Surface
        The loaded and scaled image.
    """
    # Check if the image is already in the cache
    if image_path in image_cache:
        return image_cache[image_path]

    # Load the image from the file
    image = pygame.image.load(image_path)
    original_width, original_height = image.get_size()

    # Calculate the scaling factor to fit the image within the cell size
    scaling_factor = min(cell_size / original_width, cell_size / original_height)
    new_width = int(original_width * scaling_factor)
    new_height = int(original_height * scaling_factor)

    # Scale the image
    scaled_image = pygame.transform.smoothscale(image, (new_width, new_height))

    # Cache the scaled image
    image_cache[image_path] = scaled_image

    return scaled_image
