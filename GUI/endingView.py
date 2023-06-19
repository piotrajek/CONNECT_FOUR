import arcade
import arcade.gui
import const
import game
import main
from typing import Dict, Optional, List


class MenuView(arcade.View):
    def __init__(self, spirits, mode: int, tables: Dict, test_counter: Optional[int] = None,
                 test_list: Optional[List[int]] = None):
        self.selected_mode = None
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.background = None
        self.spirits = spirits
        self.mode = mode
        self.tables = tables
        self.test_counter = test_counter
        self.test_list = test_list

        self.title = arcade.gui.UILabel(text="END OF THE GAME", font_size=40,
                                        align="centre", text_color=arcade.make_transparent_color((245, 5, 117),
                                                                                                 240),
                                        font_name="Kenney Future", bold=True)
        default_style = const.DEFAULT_STYLE
        self.v_box = arcade.gui.UIBoxLayout(space_between=20)

        self.start = arcade.gui.UIFlatButton(text="One more\nround?", width=200, height=75, style=default_style)
        self.quit_button = arcade.gui.UIFlatButton(text="Quit to\nmain menu", width=200, height=75, style=default_style)
        self.quit_button.on_click = self.on_quit_pressed
        self.start.on_click = self.on_play_press
        self.v_box.add(self.title)
        self.v_box.add(self.start)
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
        arcade.draw_rectangle_filled(const.SCREEN_WIDTH / 2, const.SCREEN_HEIGHT / 2, const.SCREEN_WIDTH,
                                     const.SCREEN_HEIGHT, arcade.make_transparent_color((180, 180, 180),
                                                                                        150))
        arcade.draw_rectangle_filled(const.SCREEN_WIDTH / 2, const.SCREEN_HEIGHT / 2, const.SCREEN_WIDTH * 0.70,
                                     const.SCREEN_HEIGHT * 0.70, arcade.make_transparent_color((100, 100, 100),
                                                                                               170))
        arcade.draw_rectangle_outline(const.SCREEN_WIDTH / 2, const.SCREEN_HEIGHT / 2, const.SCREEN_WIDTH * 0.70,
                                      const.SCREEN_HEIGHT * 0.70, arcade.make_transparent_color((180, 180, 180),
                                                                                                180))
        self.spirits.draw()
        arcade.draw_rectangle_filled(const.SCREEN_WIDTH / 2, const.SCREEN_HEIGHT / 2, const.SCREEN_WIDTH,
                                     const.SCREEN_HEIGHT, arcade.make_transparent_color((100, 100, 100),
                                                                                        190))
        self.manager.draw()

    def on_quit_pressed(self, event):
        menu = main.MenuView(self.tables)
        menu.setup()
        self.window.show_view(menu)

    def on_play_press(self, event):
        game_play = game.GameView(self.mode, self.tables, self.test_counter, self.test_list)
        game_play.setup()
        self.window.show_view(game_play)
