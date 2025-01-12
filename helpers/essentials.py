perception_to_target = {"breeze": "pit", "stench": "wumpus", "shininess": "gold"}
targets = ["pit", "wumpus", "gold"]

def parse_pos_str_to_tuple(s):
    s = s.replace('(', '')
    s = s.replace(')', '')
    x, y = s.split(',')
    return int(x), int(y)