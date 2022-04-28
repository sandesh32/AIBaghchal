from typing import Type

import numpy as np

from utils.agents import (
    QSheep,
    QWolves,
)


class BaghChal:
    def __init__(self, sheep_agent_cls: Type[QSheep], wolves_agent_cls: Type[QWolves]):
        self._board = self._create_board()

        self.sheep = sheep_agent_cls()
        self.wolves = wolves_agent_cls()

        self.done = False

    def get_state(self):
        # print(self._board)
        return self._board

    @staticmethod
    def _create_board():
        """Initiate game board and place wolves pieces to each corner"""
        board = np.zeros((5, 5), dtype=np.int32)
        # Put all wolves to the board's corners
        board[[0, 0, 4, 4], [0, 4, 0, 4]] = -1
        return board

    def step(self, state: np.array):
        """Bring system to a new state"""
        self._board[:] = state[:]

    def restart(self):
        self._board = self._create_board()
        self.sheep.in_reserve = 20
        self.wolves.captured_sheep = 0


if __name__ == "__main__":
    env = BaghChal(QSheep, QWolves)

    _round = 1
    while True:

        # Sheep turn:
        new_state = env.sheep.make_turn(env.get_state())
        if new_state is None:
            print("Wolves won!")
            break
        env.step(new_state)

        # Wolves turn
        new_state = env.wolves.make_turn(env.get_state())
        if new_state is None:
            print("Sheep won!")
            break
        env.step(new_state)
        _round += 1

    print(f"Num of turns: {_round}")
    print(f"Captured sheep: {env.wolves.captured_sheep}")
    print('----- final board state -----')
    print(env.get_state())

