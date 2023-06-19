import copy
import sys
import os
import numpy as np
import random
from typing import Dict, List
from gameSystem import is_ending_state, return_first_state, play_move_ai, generate_board
from stateSystem import save_tables, available_moves, convert_dict_read, read_tables
import multiprocessing as mp
from data_handler import append_to_txt


def is_draw(board: np.ndarray, game_parameters: Dict) -> bool:
    """
    function to check if there is a draw
    :param board: map of game size_x x size_y
    :param game_parameters: parameters of the game
    :return: is a draw or not
    """
    draw_map = np.zeros((game_parameters['size_y'],
                         game_parameters['size_x']), dtype=int)
    compare_maps = draw_map == board
    return not compare_maps.any()


def return_next_max(tables: Dict, which_player: int,
                    next_state_p: int, game_parameters: Dict) -> int:
    """
    function to return next max q-value
    :param tables: dict, which contains q-tables, prizes, how to change states, and how the boards looks like
    :param which_player: who played move
    :param next_state_p: next state of the current state
    :param game_parameters: parameters of the game
    :return: next q-max
    """
    if is_ending_state(tables['Prizes'][which_player % 2][next_state_p], game_parameters):
        return game_parameters['win_prize']
    elif is_draw(tables['States'][which_player % 2][next_state_p], game_parameters):
        return game_parameters['draw_prize']
    else:
        action = 0
        max_value = tables['Prizes'][which_player % 2][next_state_p][0]
        for i in range(0, game_parameters['size_x']):
            if tables['Prizes'][which_player % 2][next_state_p][i] > max_value:
                max_value = tables['Prizes'][which_player % 2][next_state_p][i]
                action = i
        next_state = tables['States'][which_player % 2][next_state_p][action]
        max_value = tables['Q-Tables'][which_player - 1][next_state][0]
        for i in range(0, game_parameters['size_x']):
            if tables['Q-Tables'][which_player - 1][next_state][i] > max_value:
                max_value = tables['Q-Tables'][which_player - 1][next_state][i]

        return max_value


def train_model(tables: Dict, which_player: int,
                current_state: int, game_parameters: Dict) -> int:
    """
    function to train by playing one move
    :param tables: dict, which contains q-tables, prizes, how to change states, and how the boards looks like
    :param which_player: who played move
    :param current_state: state, in which model is currently
    :param game_parameters: parameters of the game
    :return: next state
    """
    if random.uniform(0, 1) <= game_parameters['epsilon']:
        action = random.randint(0, game_parameters['size_x'] - 1)
        while tables['States'][which_player - 1][current_state][action] == -1:
            action = random.randint(0, game_parameters['size_x'] - 1)
    else:
        moves = available_moves(generate_board(tables['Boards'][which_player - 1][current_state],
                                               game_parameters), game_parameters['size_y'], game_parameters['size_x'])
        action = moves[0]
        max_value = tables['Q-Tables'][which_player - 1][current_state][action]
        for i in range(0, game_parameters['size_x']):
            if tables['Q-Tables'][which_player - 1][current_state][i] > max_value and \
                    tables['States'][which_player - 1][current_state][i] != -1:
                max_value = tables['Q-Tables'][which_player - 1][current_state][i]
                action = i
    next_state = tables['States'][which_player - 1][current_state][action]
    reward = tables['Prizes'][which_player - 1][current_state][action]
    old_value = tables['Q-Tables'][which_player - 1][current_state][action]
    next_max = return_next_max(tables, which_player, next_state, game_parameters)
    new_value = (1 - game_parameters['alpha']) * old_value + game_parameters['alpha'] * \
                (reward + game_parameters['gamma'] * next_max)
    tables['Q-Tables'][which_player - 1][current_state][action] = new_value
    return next_state


def random_agent(game_parameters: Dict, model_first: bool) -> bool:
    """
    function which defines whether opponent of the model is using AI or is choosing moves randomly
    :param game_parameters: parameters of the game
    :param model_first: is model playing first
    :return: is agent "stupid" or not
    """
    if not model_first:
        return random.uniform(0, 1) <= game_parameters['random_moves1']
    else:
        return random.uniform(0, 1) <= game_parameters['random_moves2']


def learn_model(model_first: bool, game_parameters: Dict,
                tables: Dict, iterations: int) -> None:
    """
    functions, which allows model to learn
    :param model_first: is model playing first or not
    :param game_parameters: parameters of the game
    :param tables: dict, which contains q-tables, prizes, how to change states, and how the boards looks like
    :param iterations: how many iterations of learning
    :return:
    """
    work_tables = copy.deepcopy(tables)
    max_moves = game_parameters['max_n_moves']
    ten_percentage = iterations / 10
    percentage = 0
    for i in range(1, iterations + 1):
        which_player = 1
        number_of_moves = 0
        is_random_agent = random_agent(game_parameters, model_first)
        state = return_first_state(work_tables, game_parameters)
        while not is_ending_state(work_tables['Prizes'][which_player - 1][state],
                                  game_parameters) and number_of_moves < max_moves:
            if which_player == 1:
                if model_first:
                    state = train_model(work_tables, which_player,
                                        state, game_parameters)
                else:
                    if is_random_agent:
                        moves = available_moves(generate_board(work_tables['Boards'][which_player - 1][state],
                                                               game_parameters),
                                                game_parameters['size_y'], game_parameters['size_x'])
                        np.random.shuffle(moves)
                        move = moves[0]
                    else:
                        move = play_move_ai(work_tables['Boards'][which_player - 1][state],
                                            game_parameters['depth_2'], which_player,
                                            generate_board(work_tables['Boards'][which_player - 1][state],
                                                           game_parameters),
                                            number_of_moves, which_player, game_parameters)
                    state = work_tables['States'][which_player - 1][state][move]
            else:
                if not model_first:
                    state = train_model(work_tables, which_player,
                                        state, game_parameters)
                else:
                    if is_random_agent:
                        moves = available_moves(generate_board(work_tables['Boards'][which_player - 1][state],
                                                               game_parameters),
                                                game_parameters['size_y'], game_parameters['size_x'])
                        np.random.shuffle(moves)
                        move = moves[0]
                    else:
                        move = play_move_ai(work_tables['Boards'][which_player - 1][state],
                                            game_parameters['depth_1'], which_player,
                                            generate_board(work_tables['Boards'][which_player - 1][state],
                                                           game_parameters),
                                            number_of_moves, which_player, game_parameters)
                    state = work_tables['States'][which_player - 1][state][move]

            number_of_moves += 1
            which_player = (which_player % 2) + 1

        if i % ten_percentage == 0:
            percentage += 10
            if model_first:
                print("First model: " + str(percentage) + " %")
            else:
                print("Second model: " + str(percentage) + " %")

    if model_first:
        which_player = 0
    else:
        which_player = 1
    save_dict = {"States": work_tables['States'][which_player], "Q-Tables": work_tables['Q-Tables'][which_player],
                 "Prizes": work_tables['Prizes'][which_player], "Boards": work_tables['Boards'][which_player]}
    if which_player == 0:
        save_tables(save_dict, game_parameters['Updated_table_1'], game_parameters, 1)
    else:
        save_tables(save_dict, game_parameters['Updated_table_2'], game_parameters, 1)


def train_both_models(game_parameters: Dict, iterations: int,
                      tables: Dict) -> None:
    """
    function for running both models simultaneously - after that, it is saving updated tables as json file
    :param game_parameters: parameters of the game
    :param iterations: how many iterations of learning
    :param tables: dict, which contains q-tables, prizes, how to change states, and how the boards looks like
    :return:
    """
    process1 = mp.Process(target=learn_model, args=(True, game_parameters, tables, iterations))
    process2 = mp.Process(target=learn_model, args=(False, game_parameters, tables, iterations))
    process1.start()
    process2.start()
    process1.join()
    process2.join()
    first_dict = read_tables(game_parameters['Updated_table_1'], game_parameters)
    second_dict = read_tables(game_parameters['Updated_table_2'], game_parameters)
    to_save_dict = {"States": [first_dict['States'], second_dict['States']],
                    "Q-Tables": [first_dict['Q-Tables'], second_dict['Q-Tables']],
                    "Prizes": [first_dict['Prizes'], second_dict['Prizes']],
                    "Boards": [first_dict['Boards'], second_dict['Boards']]}
    save_tables(convert_dict_read(to_save_dict), game_parameters['Updated_tables'], game_parameters)


def validate_models(game_parameters: Dict, tables: Dict,
                    states1: List[int], moves_to_make1: List[int],
                    states2: List[int], moves_to_make2: List[int]) -> float:
    counter = 0
    for i in range(0, len(states1)):
        moves = available_moves(generate_board(tables['Boards'][0][states1[i]],
                                               game_parameters), game_parameters['size_y'],
                                game_parameters['size_x'])
        action = moves[0]
        max_value = tables['Q-Tables'][0][states1[i]][action]
        for j in range(0, game_parameters['size_x']):
            if tables['Q-Tables'][0][states1[i]][j] > max_value and \
                    tables['States'][0][states1[i]][j] != - 1:
                max_value = tables['Q-Tables'][0][states1[i]][j]
                action = j

        if action == moves_to_make1[i]:
            counter += 1

    for i in range(0, len(states2)):
        moves = available_moves(generate_board(tables['Boards'][1][states2[i]],
                                               game_parameters), game_parameters['size_y'],
                                game_parameters['size_x'])
        action = moves[0]
        max_value = tables['Q-Tables'][1][states2[i]][action]
        for j in range(0, game_parameters['size_x']):
            if tables['Q-Tables'][1][states2[i]][j] > max_value and \
                    tables['States'][1][states2[i]][j] != - 1:
                max_value = tables['Q-Tables'][1][states2[i]][j]
                action = j

        if action == moves_to_make2[i]:
            counter += 1

    return counter / (len(states1) + len(states2))


def output_tables(game_parameters: Dict, tables: Dict,
                  states: List[int], which_player: int) -> None:
    for i in range(0, len(states)):
        file_name = "output_" + sys.argv[1] + "_" + sys.argv[2] + "_" + sys.argv[10] + "_" + \
                    str(which_player) + ".txt"
        path = os.path.join(game_parameters["folder_name"], file_name)
        append_to_txt(path, "State" + str(i) + "\n")
        append_to_txt(path, str(tables['Boards'][which_player - 1][states[i]]))
        append_to_txt(path, "\n")


def validation(game_parameters: Dict, tables: Dict, mode: int = 1) -> None:
    if mode == 0:
        output_tables(game_parameters, tables, [1300225, 412033, 887171, 1595524, 699396, 1155329, 141959, 1214218,
                                                80275, 1867667, 292633, 108698, 1713181, 1074978, 679843, 361251,
                                                226596, 1429030, 1584046, 1167154, 728755, 672820, 1432115, 527411,
                                                439863, 1231929, 131515, 367804, 1218367, 1751872, 176578, 886339,
                                                1823299, 744260, 531914, 1266379, 1430862, 37332, 859734, 765411,
                                                281958, 521447, 1762792, 1797865, 1162604, 396527, 1028723, 1002995,
                                                859130, 1863291], 1)
        output_tables(game_parameters, tables, [1962752, 707077, 727948, 670399, 1728530, 862492, 1757349, 271141,
                                                199719, 641064, 221865, 1930286, 1716912, 1286321, 1018290, 1995700,
                                                774456, 1798713, 1115067, 1745086, 835263, 1012800, 536001, 53954,
                                                877762, 1823684, 1941317, 1374278, 194111, 1284543, 381513, 786509,
                                                1791057, 14291, 1737559, 1247703, 1986903, 653021, 1981920, 968933,
                                                438128, 1736176, 1409393, 1959280, 453748, 502899, 1473910, 1922296,
                                                662778, 179835], 2)
    else:
        pass
