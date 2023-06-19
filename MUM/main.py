import json
import sys
import time
import os
from MUM.learningSystem import train_both_models
from MUM.stateSystem import read_tables, save_and_prepare_tables
from typing import Dict
from data_handler import append_to_csv


def generate_meta_file() -> Dict:
    folder_name = "MUM_" + sys.argv[1] + "_" + sys.argv[2] + "_" + sys.argv[10]
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    game_parameters = {"size_x": int(sys.argv[1]),
                       "size_y": int(sys.argv[2]),
                       "random_plays1": int(sys.argv[3]),
                       "random_plays2": int(sys.argv[4]),
                       "depth_1": int(sys.argv[5]),
                       "depth_2": int(sys.argv[6]),
                       "random_moves1": float(sys.argv[7]),
                       "random_moves2": float(sys.argv[8]),
                       "max_n_moves": int(sys.argv[9]),
                       "min_to_win": int(sys.argv[10]),
                       "not_allowed_move_prize": int(sys.argv[11]),
                       "draw_prize": int(sys.argv[12]),
                       "win_prize": int(sys.argv[13]),
                       "move_point": int(sys.argv[14]),
                       "points_for_rows": int(sys.argv[15]),
                       "points_for_blocking": int(sys.argv[16]),
                       "points_for_creating_ending_state": int(sys.argv[17]),
                       "points_for_preventing_ending_state": int(sys.argv[18]),
                       "alpha": float(sys.argv[19]),
                       "gamma": float(sys.argv[20]),
                       "epsilon": float(sys.argv[21]),
                       "Generate_tables": "tables_" + sys.argv[1] + "_" + sys.argv[2] + "_" + sys.argv[10] + ".json",
                       "Updated_tables": "tables_" + sys.argv[1] + "_" + sys.argv[2] + "_" + sys.argv[10] +
                                         "_trained_" + sys.argv[19] + "_" + sys.argv[20] + "_" + sys.argv[21] + ".json",
                       "Updated_table_1": "tables1_" + sys.argv[1] + "_" + sys.argv[2] + "_" + sys.argv[10] + ".json",
                       "Updated_table_2": "tables2_" + sys.argv[1] + "_" + sys.argv[2] + "_" + sys.argv[10] + ".json",
                       "process_percent": float(sys.argv[24]),
                       "folder_name": folder_name}
    file_name = "metafile_" + sys.argv[1] + "_" + sys.argv[2] + "_" + sys.argv[10] + ".json"
    path = os.path.join(folder_name, file_name)
    with open(path, "w") as file:
        json.dump(game_parameters, file)
    return game_parameters


def main() -> None:
    """
    sys.argv[22]:
        > 1 - only generate data needed to play a game and for a model
        > 2 - only learning of a model
        > 3 - generate and learn
    :return:
    """
    game_parameters = generate_meta_file()
    if int(sys.argv[22]) == 1 or int(sys.argv[22]) == 3:
        t0 = time.time()
        save_and_prepare_tables(game_parameters)
        t1 = time.time()
        append_to_csv("time_data.csv", [t1 - t0, "GeneratingData", game_parameters['size_x'],
                                        game_parameters['size_y'], game_parameters['min_to_win'], "no"])
    if int(sys.argv[22]) == 2 or int(sys.argv[22]) == 3:
        iterations = int(sys.argv[23])
        t0 = time.time()
        # train_both_models(game_parameters, iterations, read_tables(game_parameters['Generate_tables'],
        # game_parameters))
        train_both_models(game_parameters, iterations, read_tables(game_parameters['Updated_tables'],
                                                                   game_parameters))
        t1 = time.time()
        append_to_csv("time_data.csv", [t1 - t0, "TrainingModel", game_parameters['size_x'],
                                        game_parameters['size_y'], game_parameters['min_to_win'], "no"])
        print("Training model: " + str(t1 - t0) + " seconds.")


if __name__ == '__main__':
    main()
