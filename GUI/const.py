import arcade

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 704
SCREEN_TITLE = "Connect four"
PANEL_WIDTH = 130
DEFAULT_STYLE = {
    "font_name": "Kenney Future",
    "font_size": 15,
    "font_color": arcade.make_transparent_color((255, 255, 255),
                                                230),
    "border_width": 2,
    "border_color": None,
    "bg_color": arcade.make_transparent_color((153, 153, 153),
                                              230),
    "bg_color_pressed": arcade.make_transparent_color((230, 230, 230),
                                                      230),
    "border_color_pressed": arcade.make_transparent_color((230, 230, 230),
                                                          230),
    "font_color_pressed": arcade.make_transparent_color((230, 230, 230),
                                                        230),
}
COLOR_AI = (252, 186, 3)
COLOR_PLAYER = (252, 3, 202)
TEXT_SPACE_FROM_TOP = 15
SPACING_TEXT = 20
GAME_PARAMETERS = {"size_x": 5,
                   "size_y": 4,
                   "max_n_moves": 20,
                   "min_to_win": 4,
                   "not_allowed_move_prize": -100,
                   "To_read_tables": "tables_5_4_4_trained_0.75_0.75_0.3.json"}
