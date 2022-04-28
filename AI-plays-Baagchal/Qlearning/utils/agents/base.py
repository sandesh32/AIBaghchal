from abc import abstractmethod
from typing import List, Tuple, Union

import numpy as np


class Player:
    # self.__class__.__bases__.__name__ --> 'Player'

    @abstractmethod
    def get_states(self, current_state: np.array) -> List[np.array]:
        """
        Return tuple of available moves.
        0 - empty field
        1 - field occupied with sheep
       -1 - field occupied with wolf
        :return: list of next possible states (state0, state1, ...) - states are numpy arrays (5x5)
        """

    @abstractmethod
    def pick_state(self, states: List[np.array]) -> np.array:
        """
        Pick one board state as next state (can be understood as player move)
        :param states: list of all available next states
        :return: next state chosen by agent
        """

    @abstractmethod
    def make_turn(self, state: np.array) -> Tuple[np.array, bool, int]:
        """
        get_state -> pick_state -> set_state
        :return: new_state, is_game_over, reward
        """
    @staticmethod
    @abstractmethod
    def _extract_pieces_position(state: np.array) -> np.array:
        """get array of x,y coordinates for all player figures"""


class Sheep(Player):
    """figures are marked with 1 in board array"""

    def __init__(self):
        self.in_reserve = 20
        self.color = "white"

    def get_states(self, current_state: np.array):
        """
        Generate all possible next board states
        :return: list of states -  List[array(5x5)]
        """
        if self.in_reserve > 0:
            _positions = self._get_empty_fields(current_state)
            _available_states = self._generate_states(current_state, _positions, add_new=True)
            self.in_reserve -= 1
        else:
            _positions = self._extract_pieces_position(current_state)
            _available_states = self._generate_states(current_state, _positions)
        return _available_states

    def pick_state(self, states: List[np.array]) -> np.array:
        """picks randomly next state (turn)"""
        return states[np.random.choice(np.arange(len(states)))]

    def make_turn(self, current_state: np.array) -> Union[np.array, None]:
        if (current_state > 0).sum() + self.in_reserve < 16:
            # Sheep agent lose
            return None
        _states = self.get_states(current_state)
        new_state = self.pick_state(_states)
        return new_state

    @staticmethod
    def _extract_pieces_position(state: np.array) -> np.array:
        return np.array(np.where(state > 0)).T

    def _generate_states(self, state: np.array, positions: np.array, add_new: bool = False) -> np.array:
        _states = []
        if add_new:
            for pos in positions:
                _states.append(self._create_state(state, None, pos))
        else:
            for pos in positions:
                available_tiles = self._get_available_actions(state, *pos)
                for target in available_tiles:
                    _states.append(self._create_state(state, pos, target))
        return _states

    @staticmethod
    def _create_state(state: np.array, start_tile, target_tile):
        board = np.copy(state)
        if start_tile is not None:
            x0, y0 = start_tile
            board[x0][y0] = 0
        x, y = target_tile
        board[x][y] = 1
        return board

    @staticmethod
    def _get_empty_fields(state: np.array) -> np.array:
        return np.array(np.where(state == 0)).T

    @staticmethod
    def _get_available_actions(state: np.array, x0: int, y0: int):
        tiles = []

        for x in range(x0 - 1, x0 + 2):
            if not 4 >= x >= 0:
                # out of board size
                continue
            for y in range(y0 - 1, y0 + 2):
                if not 4 >= y >= 0:
                    # out of board size
                    continue
                if (x0, y0) == (x, y):
                    continue
                if (x0 + y0) % 2 == 0:
                    if state[x][y] == 0:
                        tiles.append([x, y])
                else:
                    if x == x0 or y == y0:
                        if state[x][y] == 0:
                            tiles.append([x, y])
        return tiles


class Wolves(Player):
    """figures are marked with -1 in board array"""

    def __init__(self):
        self.captured_sheep = 0
        self.color = "black"

        # Place wolves in the corner of the game board:

    def get_states(self, current_states: np.array):
        _positions = self._extract_pieces_position(current_states)
        _states = self._generate_states(current_states, _positions)
        return _states

    def pick_state(self, states: List[np.array]) -> np.array:
        """picks randomly next state (turn)"""
        return states[np.random.choice(np.arange(len(states)))]

    def make_turn(self, current_state: np.array) -> Union[None, np.array]:

        _states = self.get_states(current_state)
        if not _states:
            # Wolves agent lose
            return None
        new_state = self.pick_state(_states)

        if (current_state - new_state).sum() > 0:
            # one sheep was captured at this turn
            self.captured_sheep += 1

        return new_state

    @staticmethod
    def _extract_pieces_position(state: np.array) -> np.array:
        return np.array(np.where(state < 0)).T

    def _generate_states(self, current_state: np.array, positions: np.array):
        _states = []
        for pos in positions:
            available_tiles = self._get_available_actions(current_state, *pos)
            for target, prey in available_tiles:
                _states.append(self._create_state(current_state, pos, target, prey))
        return _states

    @staticmethod
    def _get_available_actions(state: np.array, x0: int, y0: int):
        tiles = []

        for x in range(x0 - 1, x0 + 2):
            if not 4 >= x >= 0:
                # out of board size
                continue
            for y in range(y0 - 1, y0 + 2):
                if not 4 >= y >= 0:
                    # out of board size
                    continue
                if x0 == x and y0 == y:
                    # init tile
                    continue
                if (x0 + y0) % 2 == 0:
                    if state[x][y] == 0:
                        tiles.append(([x, y], None))
                    elif state[x][y] == 1:  # with sheep figure
                        # check tile behind sheep
                        xp = x + (x - x0)
                        yp = y + (y - y0)
                        if all([4 >= z >= 0 for z in (xp, yp)]) and state[xp][yp] == 0:
                            tiles.append(([xp, yp], [x, y]))
                else:
                    #
                    if x != x0 and y != y0:
                        # exclude diagonal direction
                        continue
                    if state[x][y] == 0:
                        tiles.append(([x, y], None))
                    elif state[x][y] == 1:  # with sheep figure
                        # check tile behind sheep
                        xp = x + (x - x0)
                        yp = y + (y - y0)
                        if all([4 >= z >= 0 for z in (xp, yp)]) and state[xp][yp] == 0:
                            tiles.append(([xp, yp], [x, y]))
        return tiles

    @staticmethod
    def _create_state(current_state: np.array, start_tile, target_tile, prey_tile):
        board = np.copy(current_state)
        if prey_tile:
            xp, yp = prey_tile
            board[xp][yp] = 0
        x0, y0 = start_tile
        board[x0][y0] = 0
        x, y = target_tile
        board[x][y] = -1
        return board
