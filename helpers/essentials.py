perception_to_target = {"breeze": "pit", "stench": "wumpus", "shininess": "gold"}
targets = ["pit", "wumpus", "gold"]

delta_to_direction = {
    (1, 0): "right",
    (-1, 0): "left",
    (0, 1): "front",
    (0, -1): "back",
}

def parse_pos_str_to_tuple(s):
    s = s.replace('(', '')
    s = s.replace(')', '')
    x, y = s.split(',')
    return int(x), int(y)

def get_direction(subject_pos, target_pos):
    dx = target_pos[0] - subject_pos[0]
    dy = target_pos[1] - subject_pos[1]
    return delta_to_direction[(dx, dy)]