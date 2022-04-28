#!/usr/bin/env python

from assets import Assets
from collections import namedtuple
from game import Game, Player
from agent import Agent
from tkinter import Tk, Label, Button, LabelFrame, Canvas, PhotoImage, NW, messagebox, Menu, Toplevel, ttk

from utilities import *
from configparser import ConfigParser


parser = ConfigParser()


Move = namedtuple("Move", "x y")


class UI(object):
    def __init__(self, master):
        self.master = master

        # Initilize path to images sounds and assets
        self.assets = Assets()
        parser.read(self.assets.configuration_path)

        self.blank_img = PhotoImage(file=self.assets.blank_image_path)
        self.tiger_img = PhotoImage(file=self.assets.tiger_image_path)
        self.goat_img = PhotoImage(file=self.assets.goat_image_path)

        self.game = Game()
        self.ai_turn = True
        self.ai_enabled = False
        self.graphic_board = None
        self.RECTANGLE_HEIGHT = self.RECTANGLE_WIDTH = None
        self.BOARD_HEIGHT = self.BOARD_WIDTH = None
        # Initialise all board parameters
        self.board_init()

        # Set Title window size
        self.ui_init()
        self.menu_init()

        # Make board frame
        self.board_frame = LabelFrame(master, text="Baagchal")
        self.board_frame.grid(row=1, column=0, padx=10, pady=10)
        self.canv = None
        self.board_frame_init()

        self.turn_label = self.goats_killed_label = self.goats_in_hand_label = self.role = None
        self.details_frame = LabelFrame(master, text="Details: ")
        self.details_frame.grid(row=1, column=1)
        self.details_frame_init()

        # Event parameters
        self.move_from = Move(None, None)
        self.move_to = Move(None, None)
        self.object_to_be_moved = None
        self.selected = None


    def new_game(self):
        self.__init__(root)
        self.game.board_init()
        self.game.reload_config()
        if not self.game.is_two_player_mode():
            if self.game.ai == "Tiger":
                self.ai_turn = False
            elif self.game.ai == "Goat":
                self.ai_turn = True
            self.ai_enabled = True
        else:
            self.ai_enabled = False
        self.refresh_board()

    def is_goat_turn(self):
        return self.game.current_turn == "Goat"

    def is_tiger_turn(self):
        return not self.is_goat_turn()

    def change_settings(self):
        pass

    def reset_move_from_to(self):
        self.move_from = Move(None, None)
        self.move_to = Move(None, None)
        self.object_to_be_moved = None
        self.selected = None

    def refresh_board(self):

        self.canv.delete(self.selected)
        self.reset_move_from_to()
        self.master.after(100, self.draw_board(self.game.grid))

    def update_detail_labels(self):
        self.turn_label.configure(text=f"Turn: {self.game.current_turn}")
        self.goats_in_hand_label.configure(text=f"Goats in hand: {self.game.goats_in_hand}")
        self.goats_killed_label.configure(text=f"Goats Killed: {self.game.goats_killed}")
        self.role.configure(text=f"Role {self.game.role.get(self.game.current_turn)}")

    def make_goat_move(self, obj, object_to_be_moved_tag):
        clicked_object_tag = self.canv.itemconfigure(obj).get('tags')[4].split()[0]
        # If goat is in hand
        if self.game.goats_in_hand:
            # Get Graphics Coordinate and convert to index
            x, y = Move(*self.canv.coords(obj))
            row_1, col_1 = graphics_coordinates_to_index(self.graphic_board, x, y)
            # If clicked location is vacant
            if self.game.grid[row_1][col_1] == '_':
                self.game.grid[row_1][col_1] = 'G'
                # Switch Turn and update details
                self.game.goats_in_hand -= 1
                self.game.switch_turn()
                self.update_detail_labels()
                self.ai_turn = not self.ai_turn
            self.refresh_board()
        # If no goat is left in hand the move goats on board
        else:
            # Get from location for goat
            if clicked_object_tag.startswith(self.game.current_turn[0].lower()) and self.move_from == (None, None):
                self.get_from_coordinates(obj, clicked_object_tag)

            # Move is possible
            elif object_to_be_moved_tag != "blank" and self.move_to == (None, None):
                self.move_to = Move(*self.canv.coords(obj))

                if self.move_from != self.move_to:
                    row_1, col_1 = graphics_coordinates_to_index(self.graphic_board, *self.move_from)
                    row_2, col_2 = graphics_coordinates_to_index(self.graphic_board, *self.move_to)

                    # Move to next Position
                    if is_reachable(row_1, col_1, row_2, col_2) and self.game.grid[row_2][col_2] == '_':
                        self.move_to_next_cell(object_to_be_moved_tag, row_1, col_1, row_2, col_2)
                        self.game.switch_turn()
                        self.update_detail_labels()
                        self.ai_turn = not self.ai_turn
                self.refresh_board()
            else:
                # From and to same
                self.refresh_board()

    def get_from_coordinates(self, obj, clicked_object_tag):
        self.move_from = Move(*self.canv.coords(obj))
        self.object_to_be_moved = obj
        self.selected = self.canv.create_rectangle(self.canv.bbox(clicked_object_tag),
                                                   outline="green",
                                                   width=4, tag="selected")

    def make_eat_move(self, object_to_be_moved_tag, row_1, col_1, row_2, col_2):
        goat_x, goat_y = locate_goat_to_be_eaten(self.game.grid, row_1, col_1, row_2, col_2)

        self.game.grid[row_1][col_1] = '_'
        self.game.grid[goat_x][goat_y] = '_'
        self.game.grid[row_2][col_2] = object_to_be_moved_tag[0].upper()

        self.game.goats_killed += 1


    def move_to_next_cell(self, object_to_be_moved_tag, row_1, col_1, row_2, col_2):
        # Update all the changes to game grid
        self.game.grid[row_1][col_1] = '_'
        self.game.grid[row_2][col_2] = object_to_be_moved_tag[0].upper()

    def make_tiger_move(self, obj, object_to_be_moved_tag):
        clicked_object_tag = self.canv.itemconfigure(obj).get('tags')[4].split()[0]

        if clicked_object_tag.startswith(self.game.current_turn[0].lower()) and self.move_from == (None, None):
            self.get_from_coordinates(obj, clicked_object_tag)

         # Move is possible
        elif object_to_be_moved_tag != "blank" and self.move_to == (None, None):
            self.move_to = Move(*self.canv.coords(obj))

            if self.move_from != self.move_to:
                row_1, col_1 = graphics_coordinates_to_index(self.graphic_board, *self.move_from)
                row_2, col_2 = graphics_coordinates_to_index(self.graphic_board, *self.move_to)

                # Normal Move
                if is_reachable(row_1, col_1, row_2, col_2) and self.game.grid[row_2][col_2] == '_':
                    self.move_to_next_cell(object_to_be_moved_tag, row_1, col_1, row_2, col_2)
                    self.game.switch_turn()
                    self.update_detail_labels()
                    self.ai_turn = not self.ai_turn
                # Eat move
                elif is_reachable_to_eat(self.game.grid, row_1, col_1, row_2, col_2) and self.game.grid[row_2][col_2] == '_':
                    self.make_eat_move(object_to_be_moved_tag, row_1, col_1, row_2, col_2)
                    self.game.switch_turn()
                    self.update_detail_labels()
                    self.ai_turn = not self.ai_turn
            self.refresh_board()
        else:
            # From and to same
            self.refresh_board()

    def onObjectClick(self, event):
        obj = event.widget.find_closest(event.x, event.y, halo=5)
        object_to_be_moved_tag = "blank"
        if self.object_to_be_moved is not None:
            object_to_be_moved_tag = self.canv.itemconfigure(self.object_to_be_moved).get('tags')[4].split()[
                0]
            if object_to_be_moved_tag.startswith("blank"):
                object_to_be_moved_tag = "blank"

        if self.ai_enabled and self.ai_turn:
           pass
        else:
            if self.is_goat_turn():
                self.make_goat_move(obj, object_to_be_moved_tag)
            else:
                self.make_tiger_move(obj, object_to_be_moved_tag)

    def board_init(self):

        self.RECTANGLE_HEIGHT = self.RECTANGLE_WIDTH = 150
        self.BOARD_HEIGHT = self.BOARD_WIDTH = 600

        self.graphic_board = [
            [(20, 10), (170, 10), (320, 10), (470, 10), (620, 10)],
            [(20, 160), (170, 160), (320, 160), (470, 160), (620, 160)],
            [(20, 310), (170, 310), (320, 310), (470, 310), (620, 310)],
            [(20, 460), (170, 460), (320, 460), (470, 460), (620, 460)],
            [(20, 600), (170, 600), (320, 600), (470, 600), (620, 600)],
        ]

    def make_ai_move(self):
        ag = Agent(self.game.grid, self.game.current_turn, self.game.goats_in_hand, self.game.goats_killed, self.game.depth)
        # move = ag.get_best_move()
        ag.make_best_move()
        self.game.goats_killed = ag.dead_goats
        self.game.goats_in_hand = ag.goats_in_hand
        self.game.board = ag.board
        self.update_detail_labels()

    def draw_board(self, board):
        def draw_lines():
            line_coordinates = [[(x, y), (x + self.BOARD_WIDTH, y + self.BOARD_HEIGHT)],
                                [(x + self.BOARD_WIDTH // 2, y),
                                 (x + self.BOARD_WIDTH, y + self.BOARD_HEIGHT // 2)],
                                [(x, y + self.BOARD_HEIGHT), (x + self.BOARD_WIDTH, y)],
                                [(x, y + self.BOARD_HEIGHT // 2), (x + self.BOARD_WIDTH // 2, y)],
                                [(x, y + self.BOARD_HEIGHT // 2),
                                 (x + self.BOARD_WIDTH // 2, y + self.BOARD_HEIGHT)],
                                [(x + self.BOARD_WIDTH // 2, y + self.BOARD_WIDTH),
                                 (x + self.BOARD_WIDTH, y + self.BOARD_HEIGHT // 2)],
                                ]
            # Draw Lines
            for (x1, y1), (x2, y2) in line_coordinates:
                self.canv.create_line((x1, y1), (x2, y2), width=8)

        def draw_boxes():
            for i in range(4):
                for j in range(4):
                    bottom_corner_coordinates = (x + i * self.RECTANGLE_WIDTH, y + j * self.RECTANGLE_HEIGHT)
                    top_corner_coordinates = (
                        x + (i + 1) * self.RECTANGLE_WIDTH, y + (j + 1) * self.RECTANGLE_HEIGHT)
                    self.canv.create_rectangle(bottom_corner_coordinates, top_corner_coordinates,
                                          width=8)

        def place_objects():
            tiger_cnt, goat_cnt, blank_cnt = 0, 0, 0
            for i in range(5):
                for j in range(5):
                    x1, y1 = self.graphic_board[i][j]
                    if board[i][j] == 'T':
                        tiger = self.canv.create_image(x1, y1, image=self.tiger_img, anchor=NW,
                                                  tag="tiger_" + str(tiger_cnt))
                        self.canv.tag_bind(tiger, '<Button-1>', self.onObjectClick)
                        tiger_cnt += 1

                    elif board[i][j] == 'G':
                        goat = self.canv.create_image(x1, y1, image=self.goat_img, anchor=NW,
                                                 tag="goat_" + str(goat_cnt))
                        self.canv.tag_bind(goat, '<Button-1>', self.onObjectClick)
                        goat_cnt += 1
                    else:
                        blank = self.canv.create_image(x1, y1, image=self.blank_img, anchor=NW,
                                                  tag="blank_" + str(blank_cnt))
                        self.canv.tag_bind(blank, '<Button-1>', self.onObjectClick)

                        blank_cnt += 1

        if self.ai_enabled and self.ai_turn:
            self.make_ai_move()
            self.game.switch_turn()
            self.update_detail_labels()
            self.ai_turn = not self.ai_turn

            # CLear the canvas first
        self.canv.delete("all")
        x = y = 50

        draw_lines()
        draw_boxes()
        place_objects()

        if self.game.is_game_over():
            messagebox.showinfo("Game Over", f"{self.game.winner} wins the game")
            self.master.destroy()

    def board_frame_init(self):
        self.canv = Canvas(self.board_frame, width=700, height=700, bg='#87ceeb')
        self.canv.grid(row=0)

    def settings(self):
        setting_window = Toplevel(self.master)
        setting_window.title("Settings")
        setting_window.geometry("300x300")

        setting_window.transient(self.master)
        setting_window.grab_set()

        goat_label = Label(setting_window, text="Goat")
        goat_label.grid(row=0, column=0, pady=10, padx=10)

        options_1 = ttk.Combobox(setting_window, state="readonly",
                                    values=[
                                        "Human",
                                        "AI",
                                    ])
        options_1.grid(row=0, column=1)

        options_1_current = parser.get("settings", "goat")
        selected = dict(options_1)['values'].index(options_1_current)
        options_1.current(selected)

        tiger_label = Label(setting_window, text="Tiger")
        tiger_label.grid(row=1, column=0, pady=10, padx=10)
        options_2 = ttk.Combobox(setting_window, state="readonly",
                                 values=[
                                     "Human",
                                     "AI",
                                 ])
        options_2.grid(row=1, column=1)

        options_2_current = parser.get("settings", "tiger")
        selected = dict(options_2)['values'].index(options_2_current)
        options_2.current(selected)

        difficulty_label = Label(setting_window, text="Difficulty")
        difficulty_label.grid(row=2, column=0, pady=10, padx=10)
        difficulty_options = ttk.Combobox(setting_window, state="readonly",
                                 values=[
                                     "Easy",
                                     "Medium",
                                     "Hard",
                                 ])
        difficulty_options.grid(row=2, column=1)

        difficulty_current = parser.get("settings", "difficulty")
        selected = dict(difficulty_options)['values'].index(difficulty_current)
        difficulty_options.current(selected)

        okay = Button(setting_window, text="Save", command=lambda:self.save_settings(options_1, options_2, difficulty_options))
        okay.grid(row=3, column=0)

    def save_settings(self,options_1, options_2, difficulty_options):
        parser["settings"]["goat"] = options_1.get()
        parser["settings"]["tiger"] = options_2.get()
        parser["settings"]["difficulty"] = difficulty_options.get()

        with open(self.assets.configuration_path, "w") as f:
            parser.write(f)
        messagebox.showinfo("Settings saved. ", "Settings updated. Restart to apply the changes")

    def menu_init(self):
        menubar = Menu(self.master)
        menubar.add_command(label="New Game", command=self.new_game)
        menubar.add_command(label="Settings", command=self.settings)

        menubar.add_command(label="Quit!", command=self.master.quit)

        # display the menu
        self.master.config(menu=menubar)

    def details_frame_init(self):
        # Turn Label
        self.turn_label = Label(self.details_frame, text=f"Turn: {self.game.current_turn}", font=("Helvetica", 16),
                           fg="red")
        self.turn_label.grid(row=0, column=0)

        # Player Role
        self.role = Label(self.details_frame,
                                         text=f"Role: {self.game.role.get(self.game.current_turn)}",
                                         font=("Helvetica", 16))
        self.role .grid(row=1, column=0)
        # Goats killed
        self.goats_killed_label = Label(self.details_frame, text=f"Goats Killed: {self.game.goats_killed}",
                                   font=("Helvetica", 16))
        self.goats_killed_label.grid(row=2, column=0)

        # Goats in hand
        self.goats_in_hand_label = Label(self.details_frame, text=f"Goats in hand: {self.game.goats_in_hand}",
                                    font=("Helvetica", 16))
        self.goats_in_hand_label.grid(row=3, column=0)

    def ui_init(self):
        """
        Set windows title and sizes, icons
        """
        self.master.title("AI Plays Baagchal")
        self.master.geometry("1024x800")
        self.master.resizable(False, False)

        Label(self.master, text="Baagchal").grid(row=0, column=0)


root = Tk()
my_gui = UI(root)
my_gui.new_game()
root.mainloop()