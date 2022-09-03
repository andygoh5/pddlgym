from xml.dom import NotFoundErr
from .utils import get_asset_path, render_from_layout, render_from_layout_crisp

import matplotlib.pyplot as plt
import numpy as np

NUM_OBJECTS = 13
CLEAR, PLAYER, COUNTER, BOARD, STOVE, LETTUCE, TOMATO, LETTUCE_COUNTER, TOMATO_COUNTER, LETTUCE_BOARD, TOMATO_BOARD, AGENT_WITH_LETTUCE, AGENT_WITH_TOMATO = range(NUM_OBJECTS)

TOKEN_IMAGES = {
    PLAYER : plt.imread(get_asset_path('sokoban_player.png')),
    COUNTER : plt.imread(get_asset_path('counter.png')),
    CLEAR : plt.imread(get_asset_path('sokoban_clear.png')),
    BOARD: plt.imread(get_asset_path('board.png')),
    STOVE: plt.imread(get_asset_path('stove_counter.png')),
    LETTUCE: plt.imread(get_asset_path('lettuce.png')),
    TOMATO: plt.imread(get_asset_path('tomato.png')),
    LETTUCE_COUNTER: plt.imread(get_asset_path('lettuce_on_counter.png')),
    TOMATO_COUNTER: plt.imread(get_asset_path('tomato_on_counter.png')),
    LETTUCE_BOARD: plt.imread(get_asset_path('lettuce_on_board.png')),
    TOMATO_BOARD: plt.imread(get_asset_path('tomato_on_board.png')),
    AGENT_WITH_LETTUCE: plt.imread(get_asset_path('agent_with_lettuce.png')),
    AGENT_WITH_TOMATO: plt.imread(get_asset_path('agent_with_tomato.png'))
}

def loc_str_to_loc(loc_str):
    _, r, c = loc_str.split('-')
    return (int(r), int(c))

def get_locations(obs, thing):
    locs = []
    for lit in obs:
        if lit.predicate.name != 'at':
            continue
        if thing in lit.variables[0]:
            locs.append(loc_str_to_loc(lit.variables[1]))
    return locs

def get_values(obs, name):
    values = []
    for lit in obs:
        if lit.predicate.name == name:
            values.append(lit.variables)
    return values

def build_layout(obs):
    # Get location boundaries
    max_r, max_c = -np.inf, -np.inf
    holding = None
    for lit in obs:
        for v in lit.variables:
            if v.startswith('pos-'):
                r, c = loc_str_to_loc(v)
                max_r = max(max_r, r)
                max_c = max(max_c, c)
        if lit.__str__().startswith("holding"):
            holding = lit.__str__().split(',')[1].split(":")[0].split('-')[0]
    layout = CLEAR * np.ones((max_r+1, max_c+1), dtype=np.uint8)

    # Put things in the layout
    # Also track seen locs and goal locs
    seen_locs = set()
    goal_locs = set()

     # clear grids
    for v in get_values(obs, 'clear'):
        r, c = loc_str_to_loc(v[0])
        if (r, c) in goal_locs:
            continue
        layout[r, c] = CLEAR
        seen_locs.add((r, c))

    # counters
    for v in get_values(obs, 'is-counter'):
        r, c = loc_str_to_loc(v[0])
        if (r, c) in seen_locs:
            continue
        layout[r, c] = COUNTER

    # board
    for v in get_values(obs, 'is-board'):
        r, c = loc_str_to_loc(v[0])
        if (r, c) in seen_locs:
            continue
        layout[r, c] = BOARD

    # stove
    for v in get_values(obs, 'is-stove'):
        r, c = loc_str_to_loc(v[0])
        if (r, c) in seen_locs:
            continue
        layout[r, c] = STOVE
    
    # agent
    for r, c in get_locations(obs, 'player'):
        if holding is not None:
            if holding == 'tomato':
                layout[r, c] = AGENT_WITH_TOMATO
            if holding == 'lettuce':
                layout[r, c] = AGENT_WITH_LETTUCE
        else:
            layout[r, c] = PLAYER
        seen_locs.add((r, c))

    # lettuce
    for r, c in get_locations(obs, 'lettuce'):
        if layout[r, c] == CLEAR:
            layout[r, c] = LETTUCE
        elif layout[r, c] == COUNTER:
            layout[r, c] = LETTUCE_COUNTER
        elif layout[r, c] == BOARD:
            layout[r, c] = LETTUCE_BOARD
        seen_locs.add((r, c))

    # tomato
    for r, c in get_locations(obs, 'tomato'):
        if layout[r, c] == CLEAR:
            layout[r, c] = TOMATO
        elif layout[r, c] == COUNTER:
            layout[r, c] = TOMATO_COUNTER
        elif layout[r, c] == BOARD:
            layout[r, c] = TOMATO_BOARD
        seen_locs.add((r, c))

    # 1 indexing
    layout = layout[1:, 1:]

    # r-c flip
    layout = np.transpose(layout)

    # print("layout:")
    # print(layout)
    # import ipdb; ipdb.set_trace()
    return layout

def get_token_images(obs_cell):
    return [TOKEN_IMAGES[obs_cell]]

def render(obs, mode='human', close=False):
    if mode == "egocentric":
        layout = build_layout_egocentric(obs)
        return render_from_layout(layout, get_token_images)
    elif mode == "human":
        layout = build_layout(obs)
        return render_from_layout(layout, get_token_images)
    elif mode == "egocentric_crisp":
        layout = build_layout_egocentric(obs)
        return render_from_layout_crisp(layout, get_token_images)
    elif mode == "human_crisp":
        layout = build_layout(obs)
        return render_from_layout_crisp(layout, get_token_images)
    elif mode == "layout":
        return build_layout(obs)
    elif mode == "egocentric_layout":
        return build_layout_egocentric(obs)
