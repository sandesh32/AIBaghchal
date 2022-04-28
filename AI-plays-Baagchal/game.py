
'''
Has board config, goats_in_hand, goats_killed, current_turn
'''
from utilities import can_move
from collections import namedtuple
from configparser import  ConfigParser
from assets import Assets

parser = ConfigParser()


Player = namedtuple("Player", "role type")

INF = float("inf")

class Game(object):
    def __init__(self):
        self.asset = Assets()
        parser.read(self.asset.configuration_path)
        self.current_turn = 'Goat'
        self.winner = None
        self.goats_in_hand = 20
        self.goats_killed = 0

        self.player_1 = Player("Goat", parser.get("settings", "Goat"))
        self.player_2 = Player("Tiger", parser.get("settings", "Tiger"))

        self.depth = 4
        self.set_difficulty()

        self.ai = None
        self.role = dict()
        self.role["Goat"] = "Human"
        self.role["Tiger"] = "Human"
        if self.player_1.type == "AI":
            self.ai = "Goat"
            self.role["Goat"] = "AI"
        elif self.player_2.type == "AI":
            self.ai = "Tiger"
            self.role["Tiger"] = "AI"

        self.grid = None
        self.board_init()

    def set_difficulty(self):
        if parser.get("settings", "difficulty") == "Medium":
            self.depth = 4
        elif parser.get("settings", "difficulty") == "Hard":
            self.depth = 5
        else:
            self.depth = 3

    def reload_config(self):
        self.player_1 = Player("Goat", parser.get("settings", "goat"))
        self.player_2 = Player("Tiger", parser.get("settings", "tiger"))

    @classmethod
    def reset(cls):
        cls.__init__()

    def is_two_player_mode(self):
        return self.player_1.type == "Human" and self.player_2.type == "Human"

    def get_role(self):
        return self.role[self.current_turn]

    def board_init(self):
        self.grid = [['_' for _ in range(5)] for _ in range(5)]
        # Place tiger at corners
        self.grid[0][0] = self.grid[0][4] = self.grid[4][0] = self.grid[4][4] = 'T'

    def switch_turn(self):
        if self.current_turn == 'Goat':
            self.current_turn = 'Tiger'
        else:
            self.current_turn = 'Goat'

    def is_game_over(self):
        if self.goats_killed >= 5:
            self.winner = "Tiger"
            return True

        for i in range(5):
            for j in range(5):
                if self.grid[i][j] == 'T':
                    if can_move(self.grid, i, j):
                        return False

        self.winner = "Goat"
        return True

    def __repr__(self):
        return f"Current Turn {self.current_turn} | Goats in hand {self.goats_in_hand}"
