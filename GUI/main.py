import arcade
import arcade.gui
import game
import const
from MUM.stateSystem import read_tables
from typing import Dict, Optional, List


def on_quit_pressed(event):
    arcade.exit()


class MenuView(arcade.View):
    def __init__(self, tables: Dict, test_counter: Optional[int] = None,
                 test_list: Optional[List[int]] = None):
        self.selected_mode = None
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.background = None
        # self.tables = read_tables(const.GAME_PARAMETERS['To_read_tables'])
        self.tables = tables
        self.test_counter = test_counter
        self.test_list = test_list
        self.title = arcade.gui.UILabel(text="Connect four", font_size=40,
                                        align="centre", text_color=arcade.make_transparent_color((245, 5, 117),
                                                                                                 240),
                                        font_name="Kenney Future", bold=True)
        self.v_box = arcade.gui.UIBoxLayout(space_between=20)

        self.start_1 = arcade.gui.UIFlatButton(text="Start as 1st\nplayer", width=200, height=75, style=const.DEFAULT_STYLE)
        self.start_2 = arcade.gui.UIFlatButton(text="Start as 2nd\nplayer", width=200, height=75,
                                               style=const.DEFAULT_STYLE)
        self.quit_button = arcade.gui.UIFlatButton(text="Quit game", width=200, height=75, style=const.DEFAULT_STYLE)
        self.quit_button.on_click = on_quit_pressed
        self.start_1.on_click = self.on_play1_press
        self.start_2.on_click = self.on_play2_press
        self.v_box.add(self.title)
        self.v_box.add(self.start_1)
        self.v_box.add(self.start_2)
        self.v_box.add(self.quit_button)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def setup(self):
        self.background = arcade.load_texture("bg_img.png")

    def on_draw(self):
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0, const.SCREEN_WIDTH,
                                            const.SCREEN_HEIGHT, self.background)
        self.manager.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            arcade.exit()

    def on_play1_press(self, event):
        game_play = game.GameView(1, self.tables)
        self.window.show_view(game_play)

    def on_play2_press(self, event):
        if self.test_counter and self.test_list:
            game_play = game.GameView(2, self.tables, self.test_counter, self.test_list)
        else:
            game_play = game.GameView(2, self.tables)
        self.window.show_view(game_play)


def main():
    window = arcade.Window(const.SCREEN_WIDTH, const.SCREEN_HEIGHT, const.SCREEN_TITLE)
    menu_view = MenuView(read_tables(const.GAME_PARAMETERS['To_read_tables']))
    menu_view.setup()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
