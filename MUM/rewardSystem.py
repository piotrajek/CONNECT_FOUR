import numpy as np
from typing import Dict


def crossed_row(pos: Dict, which_player: int,
                game_board: np.ndarray, game_parameters: Dict) -> bool:
    return counter_row(pos, which_player, game_board, game_parameters, 3) >= game_parameters['min_to_win'] or \
        counter_row(pos, which_player, game_board, game_parameters, 4) >= game_parameters['min_to_win']


def horizontal_vertical_row(pos: Dict, which_player: int,
                            game_board: np.ndarray, game_parameters: Dict) -> bool:
    return counter_row(pos, which_player, game_board, game_parameters, 1) >= game_parameters['min_to_win'] or \
        counter_row(pos, which_player, game_board, game_parameters, 2) >= game_parameters['min_to_win']


def counter_row(pos: Dict, which_player: int,
                game_board: np.ndarray, game_parameters: Dict, type_of_row: int) -> int:

    if type_of_row == 1:
        x_mod = 1
        y_mod = 0
    elif type_of_row == 2:
        x_mod = 0
        y_mod = -1
    elif type_of_row == 3:
        x_mod = 1
        y_mod = -1
    elif type_of_row == 4:
        x_mod = 1
        y_mod = 1
    else:
        x_mod = 0
        y_mod = 0
    row = 1
    if is_a_new_coin(x_mod, y_mod) is not True:
        for i in range(0, 2):
            row += counter(pos['pos_x'] + x_mod, pos['pos_y'] + y_mod, which_player, 0,
                           x_mod, y_mod, game_board, game_parameters['size_x'],
                           game_parameters['size_y'], game_parameters['min_to_win'])
            if type_of_row == 2:
                break
            x_mod *= -1
            y_mod *= -1
    return row


def counter(x: int, y: int, which_player: int, repeats: int, mod_x: int, mod_y: int,
            game_board: np.ndarray, size_x: int, size_y: int, max_repeats: int) -> int:
    """
    :param game_board:
    :param max_repeats: how many repeats to count
    :param x: x_cord
    :param y: y_cord
    :param which_player: which number is counted
    :param repeats: how many repeats have been counted
    :param mod_x: how to modify x_cord
    :param mod_y: how to modify y_cord
    :param size_x: horizontal size of the map
    :param size_y: vertical size of the map
    :return: how many repeats have been counted
    """
    if is_between_borders(x, y, size_x, size_y):
        if game_board[int(y)][x] != which_player:
            return repeats
        else:
            if repeats == max_repeats:
                return repeats
            else:
                return counter(x + mod_x, y + mod_y, which_player, repeats + 1,
                               mod_x, mod_y, game_board, size_x, size_y, max_repeats)
    else:
        return repeats


def is_a_new_coin(mod_x: int, mod_y: int) -> bool:
    return mod_x == mod_y and mod_x == 0


def is_between_borders(x: int, y: int,
                       size_x: int, size_y: int) -> bool:
    return size_x > x >= 0 and size_y > y >= 0


def is_the_winner(pos: Dict, which_player: int,
                  game_board: np.ndarray, game_parameters: Dict) -> bool:
    """
    :param pos:
    :param which_player:
    :param game_board:
    :param game_parameters:
    :return:
    """
    return crossed_row(pos, which_player, game_board, game_parameters) or \
        horizontal_vertical_row(pos, which_player, game_board, game_parameters)


def return_prize(pos: Dict, which_player: int,
                 game_board: np.ndarray, game_parameters: Dict) -> int:
    """
    :param pos: dict, containing x and y coords
    :param which_player: which player made a move
    :param game_board: visualized numpy array
    :param game_parameters: parameters of the game
    :return:
    """
    prize = game_parameters['move_point']
    if is_the_winner(pos, which_player, game_board, game_parameters):
        prize += game_parameters['win_prize']

    for i in range(1, 5):
        repeats = counter_row(pos, which_player, game_board, game_parameters, i) - 1
        if repeats != 0:
            if repeats == game_parameters['min_to_win'] - 1:
                prize += game_parameters['points_for_creating_ending_state']
            prize += repeats * game_parameters['points_for_rows']
        repeats = counter_row(pos, (which_player % 2) + 1, game_board, game_parameters, i) - 1
        if repeats != 0:
            if repeats == game_parameters['min_to_win'] - 1:
                prize += game_parameters['points_for_preventing_ending_state']
            prize += repeats * game_parameters['points_for_blocking']

    return prize
