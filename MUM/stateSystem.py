import json
import multiprocessing as mp
import time
import os

import numpy as np
import copy
from typing import List, Dict, Set
from MUM.rewardSystem import return_prize, is_the_winner
from MUM.data_handler import append_to_csv


def process_number(percent: float) -> int:
    """
    :param: percent: max percent of CPU usage
    :return: number of threads to obtain
    """
    return int(min(max(int(mp.cpu_count() * percent), 1),
                   mp.cpu_count()))


def available_move(played_moves: np.ndarray, size_y: int, move: int) -> int:
    """
    :param move: which move might be played
    :param played_moves: [0] - how many moves played, [1] - move
    :param size_y: height of game board
    :return: is move available (by giving its index) or not (-1)
    """
    # print(played_moves)
    if played_moves[0][move] != size_y:
        return played_moves[1][move]
    else:
        return -1


def available_moves(played_moves: np.ndarray, size_y: int, size_x: int) -> np.ndarray:
    """
    :param size_x:
    :param played_moves: 2D tab - index and how many coins in column
    :param size_y: height of game board
    :return: available moves to play
    """

    return np.array(list(filter(lambda e: e != -1,
                                [available_move(played_moves, size_y, i) for i in range(0, size_x)])),
                    dtype=int)


def return_list_of_lists(how_many_lists: int) -> List[List]:
    return [[] for row in range(0, how_many_lists)]


def is_in_list(hash_value: int, hash_list: Set) -> bool:
    """
    :param hash_value:
    :param hash_list:
    :return:
    """
    return hash_value in hash_list


def return_game_map(game_board: np.ndarray, move: int,
                    which_player: int, moves_board: np.ndarray,
                    how_many_moves: int) -> Dict:
    """
    :param game_board: map of the game, size_x x size_y
    :param move: played move
    :param which_player: who played move
    :param moves_board: numpy array: [0] - how many moves played [1] - index of move
    :param how_many_moves: how many moves played
    :return: dict containing updated board, its moves, move, where on board is new coin, move number and who moved
    """
    return_game_board = copy.deepcopy(game_board)
    return_game_board[moves_board[0][move]][move] = which_player
    return_moves_board = copy.deepcopy(moves_board)
    return_moves_board[0][move] += 1
    return {"board": return_game_board, "moves_board": return_moves_board,
            "move": move, "add_pos": {"pos_x": move, "pos_y": return_moves_board[0][move] - 1},
            "move_number": how_many_moves, "who_moved": which_player}


def prepare_list_of_boards(game_board: np.ndarray, how_many_moves: int,
                           moves_board: np.ndarray, game_parameters: Dict,
                           is_ending_state: bool, list_to_append: List[List[Dict]],
                           hash_set: Set) -> None:
    """
    function for preparing list of all boards
    :param hash_set: list of hashes
    :param game_board: current map of the game, size_x x size_y
    :param how_many_moves: how many moves already played
    :param moves_board: numpy array: [0] - how many moves played [1] - index of move
    :param game_parameters: parameters of the game
    :param is_ending_state: is it a last, possible state or not
    :param list_to_append: where to add new, generated map of the game
    :return:
    """
    new_hash = hash(game_board.tobytes())
    if not is_in_list(new_hash, hash_set):
        hash_set.add(new_hash)
        prizes_1 = [game_parameters['not_allowed_move_prize']
                    for i in range(0, game_parameters['size_x'])]
        if how_many_moves % 2 == 0:
            which_player = 1
        else:
            which_player = 2
        if is_ending_state:
            possible_next_states = []
        else:
            moves = available_moves(moves_board, game_parameters['size_y'], game_parameters['size_x'])
            possible_next_states = [return_game_map(game_board, move, which_player, moves_board, how_many_moves + 1)
                                    for move in moves]
            prizes_2 = [(return_prize({"pos_x": state['add_pos']['pos_x'], "pos_y": state['add_pos']['pos_y']},
                                      which_player, state['board'], game_parameters), state['move'])
                        for state in possible_next_states]
            for prize in prizes_2:
                prizes_1[prize[1]] = prize[0]

        prizes = prizes_1

        list_to_append[how_many_moves].append({"state": game_board, "prizes": prizes,
                                               "next_states": [{"board_hash": hash(next_state['board'].tobytes()),
                                                                "move": next_state['move']}
                                                               for next_state in possible_next_states],
                                               "who_moved": which_player})
        """
        print({"state": game_board, "prizes": prizes,
               "next_states": possible_next_states,
               "who_moved": which_player})
        """
        if len(possible_next_states) != 0:
            for i in range(0, len(possible_next_states)):
                pos = {"pos_x": possible_next_states[i]['add_pos']['pos_x'],
                       "pos_y": possible_next_states[i]['add_pos']['pos_y']}
                if is_the_winner(pos, which_player, possible_next_states[i]['board'], game_parameters):
                    ending = True
                else:
                    ending = False
                prepare_list_of_boards(possible_next_states[i]['board'], possible_next_states[i]['move_number'],
                                       possible_next_states[i]['moves_board'], game_parameters, ending, list_to_append,
                                       hash_set)


def prepare_tables(all_states: List[Dict], game_parameters: Dict) -> Dict:
    """
    function to return compressed information about all, possible states
    :param all_states: list of dicts, which contains all possible states
    :param game_parameters: parameters of the game
    :return: compressed dict, which is then saved to json file
    """
    print("Preparing lists")
    t0 = time.time()
    state1 = list(filter(lambda e: e['who_moved'] == 1, all_states))
    state2 = list(filter(lambda e: e['who_moved'] == 2, all_states))
    t1 = time.time()
    print(str(t1 - t0) + " seconds")

    print("Indexing states")
    t0 = time.time()
    state1 = [{"board": row} for row in state1]
    state2 = [{"board": row} for row in state2]
    # print(state1[0])
    state1 = [{"board": state1[i]['board'], "id": i} for i in range(0, len(state1))]
    state2 = [{"board": state2[i]['board'], "id": i} for i in range(0, len(state2))]

    t1 = time.time()
    print(str(t1 - t0) + " seconds")
    append_to_csv("time_data.csv", [t1 - t0, "IndexingStates", game_parameters['size_x'],
                                    game_parameters['size_y'], game_parameters['min_to_win'], "no"])

    print("Preparing q-tables")
    t0 = time.time()
    q_table = [np.zeros((len(state1), game_parameters['size_x']), dtype=float),
               np.zeros((len(state2), game_parameters['size_x']), dtype=float)]
    t1 = time.time()
    print(str(t1 - t0) + " seconds")
    append_to_csv("time_data.csv", [t1 - t0, "PreparingQTables", game_parameters['size_x'],
                                    game_parameters['size_y'], game_parameters['min_to_win'], "no"])

    print("Preparing Prizes")
    t0 = time.time()
    prizes = [[state['board']['prizes'] for state in state1],
              [state['board']['prizes'] for state in state2]]
    t1 = time.time()
    print(str(t1 - t0) + " seconds")
    append_to_csv("time_data.csv", [t1 - t0, "PreparingPrizes", game_parameters['size_x'],
                                    game_parameters['size_y'], game_parameters['min_to_win'], "no"])

    print("Preparing game boards")
    t0 = time.time()
    boards = [[state['board']['state'] for state in state1],
              [state['board']['state'] for state in state2]]
    t1 = time.time()
    print(str(t1 - t0) + " seconds")
    append_to_csv("time_data.csv", [t1 - t0, "PreparingGameBoards", game_parameters['size_x'],
                                    game_parameters['size_y'], game_parameters['min_to_win'], "no"])

    # print(state1[0])
    print("Hashing")
    t0 = time.time()
    """
    states = [[{"board_hash": hash(row['board']['state'].tobytes()), "id": row['id'],
                "possible_next_states": [{"board_hash": hash(next_state['board'].tobytes()), "move": next_state['move']}
                                         for next_state in row['board']['next_states']]} for row in state1],
              [{"board_hash": hash(row['board']['state'].tobytes()), "id": row['id'],
                "possible_next_states": [{"board_hash": hash(next_state['board'].tobytes()), "move": next_state['move']}
                                         for next_state in row['board']['next_states']]} for row in state2]
              ]
              """
    states = [[{"board_hash": hash(row['board']['state'].tobytes()), "id": row['id'],
                "possible_next_states": row['board']['next_states']} for row in state1],
              [{"board_hash": hash(row['board']['state'].tobytes()), "id": row['id'],
                "possible_next_states": row['board']['next_states']} for row in state2]
              ]
    # print(states[0][0])
    t1 = time.time()
    print(str(t1 - t0) + " seconds")
    append_to_csv("time_data.csv", [t1 - t0, "Hashing", game_parameters['size_x'],
                                    game_parameters['size_y'], game_parameters['min_to_win'], "no"])

    print("Preparing states")
    t0 = time.time()
    states_dict = [{list_elem['board_hash']: hash_index
                    for hash_index, list_elem in enumerate(states[0])},
                   {list_elem['board_hash']: hash_index
                    for hash_index, list_elem in enumerate(states[1])}]

    states = [[{"id": row['id'],
                "possible_next_states": [{"board_hash": next_state['board_hash'], "move": next_state['move']}
                                         for next_state in row['board']['next_states']]} for row in state1],
              [{"id": row['id'],
                "possible_next_states": [{"board_hash": next_state['board_hash'], "move": next_state['move']}
                                         for next_state in row['board']['next_states']]} for row in state2]
              ]

    """
    number_of_processes = process_number(game_parameters['process_percent'])
    work_list1 = [np.array(states[0][i::number_of_processes], dtype=dict) for i in range(0, number_of_processes)]
    work_list2 = [np.array(states[1][i::number_of_processes], dtype=dict) for i in range(0, number_of_processes)]
    generate_work_files(work_list1, states[1], game_parameters, number_of_processes, 1)
    generate_work_files(work_list2, states[0], game_parameters, number_of_processes, 2)
    state_table = load_files(game_parameters, number_of_processes)
    """
    state_table = [[test_next_state(row, states[1], game_parameters, states_dict[1]) for row in states[0]],
                   [test_next_state(row, states[0], game_parameters, states_dict[0]) for row in states[1]]]
    t1 = time.time()
    print(str(t1 - t0) + " seconds")
    append_to_csv("time_data.csv", [t1 - t0, "PreparingStates", game_parameters['size_x'],
                                    game_parameters['size_y'], game_parameters['min_to_win'], "no"])
    """
    possible_next_states = [ {"board": return_game_board, "moves_board": return_moves_board,
            "move": move, "add_pos": {"pos_x": move, "pos_y": return_moves_board[0][move] - 1},
            "move_number": how_many_moves, "who_moved": which_player}]
    
    list_to_append[how_many_moves].append({"state": game_board, "prizes": prizes,
                                               "next_states": possible_next_states,
                                               "who_moved": which_player})
    """
    return {"States": state_table, "Q-Tables": q_table,
            "Prizes": prizes, "Boards": boards}


def generate_work_files(boards: List[np.array], state: List[Dict], game_parameters: Dict,
                        number_of_processes: int, which_player: int) -> None:
    data_manager = mp.Manager()
    state_dict = data_manager.dict({list_elem['board_hash']: hash_index
                                    for hash_index, list_elem in enumerate(state)})
    processes = []
    for i in range(0, number_of_processes):
        process = mp.Process(target=create_work_file, args=(boards[i], state, game_parameters, i, which_player))
        processes.append(process)
        process.start()

    for i in range(0, number_of_processes):
        processes[i].join()


def load_files(game_parameters: Dict, number_of_processes: int) -> List[List[int]]:
    states = [[], []]
    for i in range(1, 3):
        work_states = []
        for j in range(0, number_of_processes):
            work_states.append(load_work_file(game_parameters, j, i))
            file_name = str(i) + "_" + str(j) + ".json"
            path = os.path.join(game_parameters['folder_name'], file_name)
            os.remove(path)
        for j in range(0, len(work_states[0])):
            for k in range(0, number_of_processes):
                if j < len(work_states[k]):
                    states[i - 1].append(work_states[k][j])
    return states


def create_work_file(boards_to_check: np.array, state: List[Dict], game_parameters: Dict,
                     which_process: int, which_player: int) -> None:
    work_list = [{"board": state[i]['board'],
                  "hash": hash(state[i]['board'].tobytes()),
                  "id": state[i]['id']} for i in range(0, len(state))]
    work_list = [return_next_state(board, work_list, game_parameters)
                 for board in boards_to_check]
    file_name = str(which_player) + "_" + str(which_process) + ".json"
    path = os.path.join(game_parameters['folder_name'], file_name)
    file = open(path, "w")
    json.dump(work_list, file)


def load_work_file(game_parameters: Dict, which_process: int, which_player: int) -> List[int]:
    file_name = str(which_player) + "_" + str(which_process) + ".json"
    path = os.path.join(game_parameters['folder_name'], file_name)
    with open(path, "r") as file:
        to_return = json.load(file)
    # print(to_return)
    return to_return


def test_next_state(board: Dict, state: List[Dict], game_parameters: Dict, state_indexes: Dict) -> List[int]:
    states = [test_return_index_of_state(board, state, i, state_indexes)
              for i in range(0, game_parameters['size_x'])]
    return states


def test_return_index_of_state(board: Dict, state: List[Dict], played_move: int, state_indexes: Dict) -> int:
    work_list = [row for row in board['possible_next_states'] if row['move'] == played_move]
    if len(work_list) == 0:
        return -1
    else:
        return state[state_indexes[work_list[0]['board_hash']]]['id']


def return_next_state(board: Dict, state: List[Dict], game_parameters: Dict) -> List[int]:
    """
    function, which is used for searching boards in list of boards
    :param board: for which map of game are you searching, size_x x size_y
    :param state: list of states of the opponent
    :param game_parameters: parameters of the game
    :return: list of indexes of states of the opponent
    """

    """
    states = [-1 for i in range(0, game_parameters['size_x'])]
    
    for next_state in board[1]['next_states']:
        for i in range(0, len(state)):
            if np.array_equal(next_state['board'], state[i]['state']):
                states[next_state['move']] = i
    return states
    """
    states = [return_index_of_state(board, state, i)
              for i in range(0, game_parameters['size_x'])]
    return states


def return_index_of_state(board: Dict, state: List[Dict], played_move: int) -> int:
    """
    :param board:
    :param state:
    :param played_move:
    :return:
    """
    work_list = [row for row in board['possible_next_states'] if row['move'] == played_move]
    if len(work_list) == 0:
        return -1
    else:
        hash_id = hash(work_list[0]['board'].tobytes())
        work_list = [row for row in state if row['hash'] == hash_id]
        return work_list[0]['id']


def return_all_states(all_dicts: List[List[Dict]]) -> List[Dict]:
    """
    function which returns all possible states in form list[dict]
    :param all_dicts: all states
    :return:
    """
    return_list = []
    for boards in all_dicts:
        return_list += boards
    return return_list


def save_tables(tables: Dict, file_name: str, game_parameters: Dict, mode: int = 0) -> None:
    """
    save tables to json file
    :param game_parameters:
    :param tables: dict, which contains q-tables, prizes, how to change states, and how the boards looks like
    :param file_name: name of the file
    :param mode: does dict contain tables of both players (0) or one (any other int)
    :return:
    """
    path = os.path.join(game_parameters['folder_name'], file_name)
    with open(path, "w") as file:
        json.dump(convert_dict_write(tables, mode), file)


def read_tables(file_name: str, game_parameters: Dict = None, mode: int = 0) -> Dict:
    """
    loads tables do dict
    :param game_parameters:
    :param file_name: name of the json file, where table/tables are located
    :param mode: does file contain tables of both players (0) or one (any other int)
    :return: dict of tables
    """
    if game_parameters is not None:
        path = os.path.join(game_parameters['folder_name'], file_name)
        with open(path, "r") as file:
            to_return = json.load(file)
    else:
        with open(file_name, "r") as file:
            to_return = json.load(file)
    return convert_dict_read(to_return, mode)


def convert_dict_write(tables: Dict, mode: int = 0) -> Dict:
    """
    function to convert dict of tables to write to json file
    :param tables: dict, which contains q-tables, prizes, how to change states, and how the boards looks like
    :param mode: 0 for both players, any other int for only one
    :return: dict, which can be saved
    """
    if mode == 0:
        tables['Q-Tables'][0] = tables['Q-Tables'][0].tolist()
        tables['Q-Tables'][1] = tables['Q-Tables'][1].tolist()
        tables['Boards'][0] = [tables['Boards'][0][i].tolist() for i in range(0, len(tables['Boards'][0]))]
        tables['Boards'][1] = [tables['Boards'][1][i].tolist() for i in range(0, len(tables['Boards'][1]))]
    else:
        tables['Q-Tables'] = tables['Q-Tables'].tolist()
        tables['Boards'] = [tables['Boards'][i].tolist() for i in range(0, len(tables['Boards']))]
    return tables


def convert_dict_read(tables: Dict, mode: int = 0) -> Dict:
    """
    function to convert dict from json file to dict which uses numpy arrays and lists
    :param tables: dict, which contains q-tables, prizes, how to change states, and how the boards looks like
    :param mode: 0 for both players, any other int for only one
    :return: dict, which can be used for learning and playing
    """
    if mode == 0:
        tables['Q-Tables'][0] = np.array(tables['Q-Tables'][0], dtype=float)
        tables['Q-Tables'][1] = np.array(tables['Q-Tables'][1], dtype=float)
        tables['Boards'][0] = [np.array(tables['Boards'][0][i], dtype=int) for i in range(0, len(tables['Boards'][0]))]
        tables['Boards'][1] = [np.array(tables['Boards'][1][i], dtype=int) for i in range(0, len(tables['Boards'][1]))]
    else:
        tables['Q-Tables'] = np.array(tables['Q-Tables'], dtype=float)
        tables['Boards'] = [np.array(tables['Boards'][i], dtype=int) for i in range(0, len(tables['Boards']))]
    return tables


def save_and_prepare_tables(game_parameters: Dict) -> None:
    """
    function, which generates and saves generated tables
    :param game_parameters: parameters of the game
    :return:
    """
    list_of_all_dicts = return_list_of_lists(game_parameters['max_n_moves'] + 1)
    moves_table = np.zeros((2, game_parameters['size_x']), dtype=int)
    for i in range(0, game_parameters['size_x']):
        moves_table[1][i] = i

    print("Preparing game tree")
    t0 = time.time()
    prepare_list_of_boards(np.zeros((game_parameters['size_y'], game_parameters['size_x']), dtype=int), 0,
                           moves_table, game_parameters, False,
                           list_of_all_dicts, set())
    t1 = time.time()
    print(str(t1 - t0) + " seconds")
    append_to_csv("time_data.csv", [t1 - t0, "PreparingGameTree", game_parameters['size_x'],
                                    game_parameters['size_y'], game_parameters['min_to_win'], "no"])

    print("Conversion")
    t0 = time.time()
    all_states = return_all_states(list_of_all_dicts)
    tables = prepare_tables(all_states, game_parameters)
    t1 = time.time()
    print(str(t1 - t0) + " seconds")
    append_to_csv("time_data.csv", [t1 - t0, "GeneratedDataConversion", game_parameters['size_x'],
                                    game_parameters['size_y'], game_parameters['min_to_win'], "no"])

    print("Saving")
    t0 = time.time()
    save_tables(tables, game_parameters['Generate_tables'], game_parameters)
    t1 = time.time()
    print(str(t1 - t0) + " seconds")
    append_to_csv("time_data.csv", [t1 - t0, "SavingJSONFile", game_parameters['size_x'],
                                    game_parameters['size_y'], game_parameters['min_to_win'], "no"])
