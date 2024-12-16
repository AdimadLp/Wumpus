def moore_neighborhood(x, y, size, multiplier=1):
    """
    Calculate the Moore neighborhood for a given position.

    Parameters:
    -----------
    x : int
        The x-coordinate of the position.
    y : int
        The y-coordinate of the position.
    size : int
        The size of the grid.
    multiplier : int
        The range multiplier for the neighborhood.

    Returns:
    --------
    list
        A list of (x, y) tuples representing the neighboring positions.
    """
    neighbors = []
    for dx in range(-multiplier, multiplier + 1):
        for dy in range(-multiplier, multiplier + 1):
            if dx == 0 and dy == 0:
                continue
            new_x = x + dx
            new_y = y + dy
            if 0 <= new_x < size and 0 <= new_y < size:
                neighbors.append((new_x, new_y))
    return neighbors


def neumann_neighborhood(x, y, size, multiplier=1):
    """
    Calculate the Neumann neighborhood for a given position.

    Parameters:
    -----------
    x : int
        The x-coordinate of the position.
    y : int
        The y-coordinate of the position.
    size : int
        The size of the grid.
    multiplier : int
        The range multiplier for the neighborhood.

    Returns:
    --------
    list
        A list of (x, y) tuples representing the neighboring positions.
    """
    neighbors = []
    for dx in range(-multiplier, multiplier + 1):
        for dy in range(-multiplier, multiplier + 1):
            if (dx == 0 and dy == 0) or (dx != 0 and dy != 0):
                continue
            new_x = x + dx
            new_y = y + dy
            if 0 <= new_x < size and 0 <= new_y < size:
                neighbors.append((new_x, new_y))
    return neighbors
