import numpy as np
import copy
import math
from typing import Dict, Tuple
from MUM.rewardSystem import is_the_winner, is_between_borders
from MUM.stateSystem import available_moves

MIN = -1
MAX = 1
INFINITY_POSITIVE = math.inf
INFINITY_NEGATIVE = -math.inf


def generate_board(game_board: np.ndarray, game_parameters: Dict) -> np.ndarray:
    """
    function used for generating possible moves
    [0] - how many moves played
    [1] - index of move
    :param game_board: map of game size_x x size_y
    :param game_parameters: parameters of the game
    :return: numpy array of moves and how many times they were played
    """
    to_return = [[], []]
    for i in range(0, game_parameters['size_x']):
        to_add = 0
        for j in range(0, game_parameters['size_y']):
            if game_board[j][i] == 0:
                break
            else:
                to_add += 1
        to_return[0].append(to_add)
        to_return[1].append(i)
    return np.array(to_return)


def alpha_beta(game_board: np.ndarray, depth: int, min_or_max: int, move: int,
               alfa: float, beta: float, which_player: int, played_moves: np.ndarray,
               number_of_moves: int, actual_player: int, game_parameters: Dict) -> Tuple:
    """
    function for more intelligent agent, which plays against model, based on alpha-beta algorithm, which
    uses heuristic functions in order to make agent smarter
    :param game_board: map of game size_x x size_y
    :param depth: how many possible moves to analyze
    :param min_or_max: start as MAX (1)
    :param move: played move
    :param alfa: alpha-beta parameter - start as -math.inf
    :param beta: alpha-beta parameter - start as math.inf
    :param which_player: who is going to move - use 1 or 2
    :param played_moves: numpy array generated with generate_board
    :param number_of_moves: how many moves played
    :param actual_player: who is choosing move
    :param game_parameters: parameters of the game
    :return: which move is going to be the best and how valuable it is
    """
    alfa_v = alfa
    beta_v = beta
    if number_of_moves != 0:
        current_prize = return_prize({'pos_x': move, 'pos_y': played_moves[1][move] - 1},
                                     (which_player % 2) + 1, game_board,
                                     number_of_moves, game_parameters)
        if (which_player % 2) + 1 != actual_player:
            current_prize *= -1
    else:
        current_prize = 0

    if map_full(played_moves, game_parameters) or depth == 0:
        return move, current_prize

    best_score = INFINITY_NEGATIVE * min_or_max
    best_max_move = -1
    moves = available_moves(played_moves, game_parameters['size_y'], game_parameters['size_x'])

    if which_player == 1:
        random_play = game_parameters['random_plays1']
    else:
        random_play = game_parameters['random_plays2']

    heuristic_values = np.zeros(moves.size, dtype=int)
    if int(number_of_moves / 2) >= random_play:
        for i in range(0, moves.size):
            heuristic_values[i] = heuristic_function(game_board, played_moves, which_player,
                                                     moves[i], number_of_moves, game_parameters)
        for i in range(0, moves.size):
            for j in range(i, moves.size):
                if heuristic_values[i] < heuristic_values[j]:
                    heuristic_values[i], heuristic_values[j] = heuristic_values[j], heuristic_values[i]
                    moves[i], moves[j] = moves[j], moves[i]
    else:
        np.random.shuffle(moves)

    for i in range(0, moves.size):
        copy_of_map = copy.deepcopy(game_board)
        copy_of_board = copy.deepcopy(played_moves)
        play_move(copy_of_map, moves[i], which_player, game_parameters['size_y'])
        copy_of_board[0][moves[i]] += 1
        best = alpha_beta(copy_of_map, depth - 1, min_or_max * -1, moves[i], alfa_v, beta_v,
                          (which_player % 2) + 1, copy_of_board, number_of_moves + 1,
                          actual_player, game_parameters)
        score = best[1] + heuristic_values[i]
        if (min_or_max == MAX and score > best_score) or \
                (min_or_max == MIN and score < best_score):
            best_score = score
            best_max_move = best[0]
        if min_or_max == MAX:
            if score >= beta:
                break
            alfa_v = max(alfa, score)
        else:
            if score <= alfa:
                break
            beta_v = min(beta, score)

    return best_max_move, best_score


def map_full(played_moves: np.ndarray, game_parameters: Dict) -> bool:
    """
    checks if map is full
    :param played_moves: numpy array generated with generate_board
    :param game_parameters: parameters of the game
    :return: is full or not
    """
    for i in range(0, game_parameters['size_x']):
        if played_moves[1][i] != game_parameters['size_y']:
            return False
    return True


def heuristic_function(game_board: np.ndarray, played_moves: np.ndarray,
                       which_player: int, move: int, number_of_moves: int,
                       game_parameters: Dict) -> int:
    """
    function for giving additional prize for AI agent
    :param game_board: map of game size_x x size_y
    :param played_moves: numpy array generated with generate_board
    :param which_player: who is going to move - use 1 or 2
    :param move: played move
    :param number_of_moves: how many moves played
    :param game_parameters: parameters of the game
    :return: additional prize for blocking / creating new row
    """
    x_mod = -1
    y_mod = -1
    prize = 0
    for i in range(0, 7):
        if i == 3:
            x_mod *= -1
            y_mod = -1
        elif i == 6:
            x_mod = 0
            y_mod = -1
        if is_between_borders(move + x_mod, played_moves[1][move] + y_mod,
                              game_parameters['size_x'], game_parameters['size_y']):
            if game_board[played_moves[1][move] + y_mod][move + x_mod] == which_player:
                prize += 2
            elif game_board[played_moves[1][move] + y_mod][move + x_mod] == (which_player % 2) + 1:
                prize += 1
            else:
                if number_of_moves > 7:
                    prize -= 1
        y_mod += 1
    return prize


def return_prize(pos: Dict, which_player: int, game_board: np.ndarray,
                 number_of_moves: int, game_parameters: Dict) -> int:
    """
    function for returning prize of AI agent
    :param pos: where is new coin
    :param which_player: who placed new coin
    :param game_board: map of game size_x x size_y
    :param number_of_moves: how many moves played
    :param game_parameters: parameters of the game
    :return: prize for played move
    """
    if number_of_moves < game_parameters['min_to_win'] * 2 - 1:
        current_prize = 0
    else:
        if is_the_winner(pos, which_player, game_board, game_parameters):
            current_prize = 10
        else:
            current_prize = 0
    return current_prize


def play_move(map_of_game: np.ndarray, x_position: int,
              which_player: int, size_y: int) -> None:
    """
    function for updating map of the game
    :param map_of_game: map of game size_x x size_y
    :param x_position: where moved was played
    :param which_player: who played move
    :param size_y: vertical size of map of game
    :return:
    """
    i = 0
    while i != size_y - 1 and map_of_game[i][x_position] != 0:
        i += 1
    map_of_game[i][x_position] = which_player
