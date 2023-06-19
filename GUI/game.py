import arcade
import arcade.gui
import const
import main
import time
import endingView
from MUM.gameSystem import is_ending_state, return_first_state
from MUM.stateSystem import available_moves
from MUM.aiSystem import generate_board
from typing import Dict, Optional, List


class Coin(arcade.SpriteCircle):
    def __init__(self, player: int, radius: int,
                 pos_x: int, pos_y: int, model_first: bool):
        self.player = player
        if model_first:
            if player == 1:
                color = const.COLOR_AI
            else:
                color = const.COLOR_PLAYER
        else:
            if player == 2:
                color = const.COLOR_AI
            else:
                color = const.COLOR_PLAYER
        super().__init__(radius, color)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.center_y = const.SCREEN_HEIGHT / 2
        self.center_x = const.SCREEN_WIDTH / 2
        if pos_y < 2:
            self.center_y -= radius + (1 - pos_y) * (2 * radius + 20)
        else:
            self.center_y += radius + 20 + (pos_y - 2) * (2 * radius + 20)

        if pos_x < 2:
            self.center_x -= 2 * radius + 30 + (1 - pos_x) * (2 * radius + 30)
        elif pos_x > 2:
            self.center_x += 2 * radius + 30 + (pos_x - 3) * (2 * radius + 30)


class GameView(arcade.View):
    def __init__(self, mode: int, tables: Dict, test_counter: Optional[int] = None,
                 test_list: Optional[List[int]] = None):
        self.selected_mode = mode
        super().__init__()
        self.background = None
        if mode == 1:
            self.blocked = False
            self.model_first = False
        else:
            self.blocked = True
            self.model_first = True
        self.game_parameters = const.GAME_PARAMETERS
        # self.tables = read_tables(self.game_parameters['To_read_tables'])
        self.tables = tables
        self.which_player = 1
        self.number_of_moves = 0
        self.test_counter = test_counter
        self.test_list = test_list
        if test_counter and test_list:
            self.state = test_list[test_counter]
        else:
            self.state = return_first_state(self.tables, self.game_parameters)
        self.coins = arcade.SpriteList()
        self.time = None
        self.pause = False
        self.move_ending_state = False
        self.setup()

    def setup(self):
        self.background = arcade.load_texture("bg_img.png")

    def on_draw(self):
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0, const.SCREEN_WIDTH,
                                            const.SCREEN_HEIGHT, self.background)
        arcade.draw_rectangle_filled(const.SCREEN_WIDTH / 2, const.SCREEN_HEIGHT / 2, const.SCREEN_WIDTH,
                                     const.SCREEN_HEIGHT, arcade.make_transparent_color((180, 180, 180),
                                                                                        150))
        arcade.draw_rectangle_filled(const.SCREEN_WIDTH / 2, const.SCREEN_HEIGHT / 2, const.SCREEN_WIDTH * 0.70,
                                     const.SCREEN_HEIGHT * 0.70, arcade.make_transparent_color((100, 100, 100),
                                                                                               170))
        arcade.draw_rectangle_outline(const.SCREEN_WIDTH / 2, const.SCREEN_HEIGHT / 2, const.SCREEN_WIDTH * 0.70,
                                      const.SCREEN_HEIGHT * 0.70, arcade.make_transparent_color((180, 180, 180),
                                                                                                180))
        self.coins.draw()
        arcade.draw_text("Player", 10, const.SCREEN_HEIGHT - const.TEXT_SPACE_FROM_TOP, const.COLOR_PLAYER,
                         const.DEFAULT_STYLE['font_size'], font_name=const.DEFAULT_STYLE['font_name'])
        arcade.draw_text("AI", 10, const.SCREEN_HEIGHT - (const.TEXT_SPACE_FROM_TOP + const.SPACING_TEXT),
                         const.COLOR_AI,
                         const.DEFAULT_STYLE['font_size'], font_name=const.DEFAULT_STYLE['font_name'])
        arcade.draw_text("Moves played: " + str(self.number_of_moves), 10,
                         const.SCREEN_HEIGHT - (const.TEXT_SPACE_FROM_TOP + 2 * const.SPACING_TEXT),
                         const.DEFAULT_STYLE['font_color'],
                         const.DEFAULT_STYLE['font_size'], font_name=const.DEFAULT_STYLE['font_name'])
        arcade.draw_text("ESC - GIVE UP", 10,
                         const.SCREEN_HEIGHT - (const.TEXT_SPACE_FROM_TOP + 4 * const.SPACING_TEXT),
                         const.DEFAULT_STYLE['font_color'],
                         const.DEFAULT_STYLE['font_size'] - 3, font_name=const.DEFAULT_STYLE['font_name'])
        arcade.draw_text("CONTROL", 10,
                         const.SCREEN_HEIGHT - (const.TEXT_SPACE_FROM_TOP + 6 * const.SPACING_TEXT),
                         const.DEFAULT_STYLE['font_color'],
                         const.DEFAULT_STYLE['font_size'] - 3, font_name=const.DEFAULT_STYLE['font_name'])
        arcade.draw_text("1 - column 1", 10,
                         const.SCREEN_HEIGHT - (const.TEXT_SPACE_FROM_TOP + 7 * const.SPACING_TEXT),
                         const.DEFAULT_STYLE['font_color'],
                         const.DEFAULT_STYLE['font_size'] - 3, font_name=const.DEFAULT_STYLE['font_name'])
        arcade.draw_text("2 - column 2", 10,
                         const.SCREEN_HEIGHT - (const.TEXT_SPACE_FROM_TOP + 8 * const.SPACING_TEXT),
                         const.DEFAULT_STYLE['font_color'],
                         const.DEFAULT_STYLE['font_size'] - 3, font_name=const.DEFAULT_STYLE['font_name'])
        arcade.draw_text("3 - column 3", 10,
                         const.SCREEN_HEIGHT - (const.TEXT_SPACE_FROM_TOP + 9 * const.SPACING_TEXT),
                         const.DEFAULT_STYLE['font_color'],
                         const.DEFAULT_STYLE['font_size'] - 3, font_name=const.DEFAULT_STYLE['font_name'])
        arcade.draw_text("4 - column 4", 10,
                         const.SCREEN_HEIGHT - (const.TEXT_SPACE_FROM_TOP + 10 * const.SPACING_TEXT),
                         const.DEFAULT_STYLE['font_color'],
                         const.DEFAULT_STYLE['font_size'] - 3, font_name=const.DEFAULT_STYLE['font_name'])
        arcade.draw_text("5 - column 5", 10,
                         const.SCREEN_HEIGHT - (const.TEXT_SPACE_FROM_TOP + 11 * const.SPACING_TEXT),
                         const.DEFAULT_STYLE['font_color'],
                         const.DEFAULT_STYLE['font_size'] - 3, font_name=const.DEFAULT_STYLE['font_name'])

    def on_update(self, delta_time: float):
        if not self.pause:
            if self.blocked:
                move = self.play_move_model()
                self.state = self.tables['States'][self.which_player - 1][self.state][move]
                self.number_of_moves += 1
                self.which_player = (self.which_player % 2) + 1
                self.time = time.time()
                self.pause = True
        if self.pause:
            if time.time() - self.time > 0.75:
                self.set_new_map()
                if not self.move_ending_state:
                    if is_ending_state(self.tables['Prizes'][self.which_player - 1][self.state],
                                       self.game_parameters) or \
                            self.number_of_moves == self.game_parameters['max_n_moves']:
                        self.move_ending_state = True
                        self.time = time.time()
                        print("END OF GAME")
                    else:
                        self.pause = False
                        if self.model_first:
                            if (self.which_player % 2) + 1 == 1:
                                self.blocked = False
                        else:
                            if (self.which_player % 2) + 1 == 2:
                                self.blocked = False
                else:
                    if self.test_counter:
                        ending = endingView.MenuView(self.coins, self.selected_mode, self.tables,
                                                     self.test_counter + 1, self.test_list)
                    else:
                        ending = endingView.MenuView(self.coins, self.selected_mode, self.tables)

                    ending.setup()
                    self.window.show_view(ending)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            menu = main.MenuView(self.tables)
            menu.setup()
            self.window.show_view(menu)
        if not self.blocked:
            moves = available_moves(generate_board(self.tables['Boards'][self.which_player - 1][self.state],
                                                   self.game_parameters),
                                    self.game_parameters['size_y'], self.game_parameters['size_x'])
            played_move = None
            if symbol == arcade.key.KEY_1:
                if 0 in moves:
                    played_move = 0
            elif symbol == arcade.key.KEY_2:
                if 1 in moves:
                    played_move = 1
            elif symbol == arcade.key.KEY_3:
                if 2 in moves:
                    played_move = 2
            elif symbol == arcade.key.KEY_4:
                if 3 in moves:
                    played_move = 3
            elif symbol == arcade.key.KEY_5:
                if 4 in moves:
                    played_move = 4
            if played_move is not None:
                print("MOVED MADE BY PLAYER " + str(played_move))
                self.blocked = True
                self.time = time.time()
                self.pause = True
                self.state = self.tables['States'][self.which_player - 1][self.state][played_move]
                self.number_of_moves += 1
                self.which_player = (self.which_player % 2) + 1

    def play_move_model(self) -> int:
        moves = available_moves(generate_board(self.tables['Boards'][self.which_player - 1][self.state],
                                               self.game_parameters), self.game_parameters['size_y'],
                                self.game_parameters['size_x'])
        action = moves[0]
        max_value = self.tables['Q-Tables'][self.which_player - 1][self.state][action]
        for i in range(0, self.game_parameters['size_x']):
            if self.tables['Q-Tables'][self.which_player - 1][self.state][i] > max_value and \
                    self.tables['States'][self.which_player - 1][self.state][i] != - 1:
                max_value = self.tables['Q-Tables'][self.which_player - 1][self.state][i]
                action = i
        print("MOVE MADE BY AI " + str(action))

        return action

    def set_new_map(self):
        for coin in self.coins:
            coin.kill()
        for x in range(0, self.game_parameters['size_x']):
            for y in range(0, self.game_parameters['size_y']):
                self.put_new_coin(x, y)

    def put_new_coin(self, pos_x: int, pos_y: int):
        x = pos_x
        y = self.game_parameters['size_y'] - pos_y - 1
        player = self.tables['Boards'][self.which_player - 1][self.state]
        player = player[y][x]
        if player != 0:
            self.coins.append(Coin(player, 50, x, y, self.model_first))
