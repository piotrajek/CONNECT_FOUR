import numpy as np
import math
from typing import Dict
from MUM.aiSystem import alpha_beta, generate_board

MAX = 1
INFINITY_POSITIVE = math.inf
INFINITY_NEGATIVE = -math.inf


def is_ending_state(prizes: np.ndarray, game_parameters: Dict) -> bool:
    """
    checks if the game is in ending state
    :param prizes: numpy array containing prizes for playing certain moves
    :param game_parameters: parameters of the game
    :return: is in ending state or not, based od prizes
    """
    for i in range(0, game_parameters['size_x']):
        if prizes[i] != game_parameters['not_allowed_move_prize']:
            return False
    return True


def return_first_state(tables: Dict, game_parameters: Dict) -> int:
    """
    function which returns starting state
    :param tables: dict, which contains q-tables, prizes, how to change states, and how the boards looks like
    :param game_parameters: parameters of the game
    :return: index of first state
    """
    index = 0
    draw_map = np.zeros((game_parameters['size_y'],
                         game_parameters['size_x']), dtype=int)
    while index < len(tables['States'][0]):
        compare_maps = draw_map == tables['Boards'][0][index]
        if compare_maps.all():
            break
        index += 1
    return index


def play_game(model_first: bool, real_player: bool,
              game_parameters: Dict, tables: Dict) -> None:
    """
    function for testing trained model - YOU SHOULDN'T USE THIS FUNCTION, AS IT'S NOT FINISHED
    :param model_first: is model playing first or second
    :param real_player: set as false
    :param game_parameters: parameters of the game
    :param tables: dict, which contains q-tables, prizes, how to change states, and how the boards looks like
    :return:
    """
    which_player = 1
    number_of_moves = 0
    max_moves = game_parameters['max_n_moves']
    state = return_first_state(tables, game_parameters)
    while not is_ending_state(tables['Prizes'][which_player][state],
                              game_parameters) and number_of_moves != max_moves:
        if which_player == 1:
            if model_first:
                move = play_move_model(tables, which_player,
                                       state, game_parameters)
            else:
                if not real_player:
                    move = play_move_ai(tables['Boards'][which_player][state],
                                        game_parameters['depth_1'],
                                        which_player, generate_board(tables['Boards'][which_player][state],
                                                                     game_parameters),
                                        number_of_moves, which_player, game_parameters)
                else:
                    move = 0
        else:
            if not model_first:
                move = play_move_model(tables, which_player,
                                       state, game_parameters)
            else:
                if not real_player:
                    move = play_move_ai(tables['Boards'][which_player][state],
                                        game_parameters['depth_2'],
                                        which_player, generate_board(tables['Boards'][which_player][state],
                                                                     game_parameters),
                                        number_of_moves, which_player, game_parameters)
                else:
                    move = 0

        state = tables['States'][which_player - 1][move]
        number_of_moves += 1
        which_player = (which_player % 2) + 1


def play_move_model(tables: Dict, which_player: int,
                    current_state: int, game_parameters: Dict) -> int:
    """
    DON'T USE THIS FUNCTION, IT'S NOT DONE
    :param tables: dict, which contains q-tables, prizes, how to change states, and how the boards looks like
    :param which_player: who is playing a move
    :param current_state: index of state
    :param game_parameters: parameters of the game
    :return:
    """
    max_value = tables['Q-tables'][which_player][current_state][0]
    action = 0
    for i in range(0, game_parameters['size_x']):
        if tables['Q-tables'][which_player][current_state][i] > max_value:
            max_value = tables['Q-tables'][which_player][current_state][i]
            action = i

    return action


def play_move_ai(game_board: np.ndarray, depth: int, which_player: int, played_moves: np.ndarray,
                 number_of_moves: int, actual_player: int, game_parameters: Dict) -> int:
    """
    function for playing as AI
    :param game_board: map of game size_x x size_y
    :param depth: how many possible moves to analyze
    :param which_player: who is going to move - use 1 or 2
    :param played_moves: numpy array generated with generate_board
    :param number_of_moves: how many moves played
    :param actual_player: who is choosing move
    :param game_parameters: parameters of the game
    :return: which move is going to be the best
    """
    move = alpha_beta(game_board, depth, MAX, 0, INFINITY_NEGATIVE, INFINITY_POSITIVE,
                      which_player, played_moves, number_of_moves, actual_player, game_parameters)
    return move[0]
