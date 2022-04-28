
"""
This file contains implementation of AI agent that uses minimax algorithm to find the best possible move
"""
from collections import namedtuple
from utilities import x_not_equals_y_operations, x_equals_y_operations, is_inside_board, is_game_over
import random
from datetime import datetime
from copy import deepcopy

Move = namedtuple("Move", "type frm to inter")
INF = float("inf")

class Agent(object):
    def __init__(self, board, turn,goats_in_hand,  dead_goats, depth=5):
        self.board = board
        self.depth = depth
        self.best_move = None
        self.winner = None
        self.turn = turn
        self.goats_in_hand = goats_in_hand
        self.dead_goats = dead_goats

    def is_vacant(self, i, j):
        return self.board[i][j] == '_'

    def number_of_movable_tigers(self):
        cnt = 0
        for i in range(5):
            for j in range(5):
                operations = x_not_equals_y_operations
                if i % 2 == j % 2:
                    operations = x_equals_y_operations
                if self.board[i][j] == 'T':
                    for offset_x, offset_y in operations:
                        next_i, next_j = i + offset_x, j + offset_y
                        if is_inside_board(next_i, next_j) and self.is_vacant(next_i, next_j):
                            cnt += 1
                            break
        assert(cnt <= 4)
        return cnt



    def number_of_closed_spaces(self):
        cnt = 0
        for i in range(5):
            for j in range(5):
                if self.board[i][j] == '_':
                    cnt += 1
        return cnt

    def evaluate(self, depth=0):
        winner = is_game_over(self.board, self.dead_goats)
        if not winner[0]:
             random.seed(datetime.now())
             return 5 * self.number_of_movable_tigers() + 50 * self.dead_goats + 15 * self.number_of_goats_that_can_be_captured() - random.random()
            # return depth

        if winner[1] == "Goat":
            return -INF
        elif winner[1] == "Tiger":
            return INF

    def place_goats(self):
        moves = []
        for i in range(5):
            for j in range(5):
                if self.is_vacant(i, j):
                    moves.append(Move("p", None, (i, j), None))
        return moves


    def number_of_goats_that_can_be_captured(self):
        cnt = 0
        board = deepcopy(self.board)
        for i in range(5):
            for j in range(5):
                if board[i][j] == 'T':
                    operations = x_not_equals_y_operations
                    if i % 2 == j % 2:
                        operations = x_equals_y_operations

                    for offset_x, offset_y in operations:
                        next_i, next_j = i + offset_x, j + offset_y
                        if is_inside_board(next_i, next_j) and board[next_i][next_j] == 'G':
                            next_next_i, next_next_j = i + 2 * offset_x, j + 2 * offset_y
                            if is_inside_board(next_next_i, next_next_j) and \
                                    board[next_next_i][next_next_j] == '_':
                                board[next_i][next_j] = '_'
                                cnt += 1

        return cnt

    def move_goats(self):
        moves = []
        for i in range(5):
            for j in range(5):
                if self.board[i][j] == 'G':
                    operations = x_not_equals_y_operations
                    if i % 2 == j % 2:
                        operations = x_equals_y_operations

                    for offset_x, offset_y in operations:
                        next_i, next_j = i + offset_x, j + offset_y
                        if is_inside_board(next_i, next_j) and self.is_vacant(next_i, next_j):
                            moves.append(Move("m", (i, j), (next_i, next_j), None))
        return moves

    def move_tigers(self):
        moves = []
        for i in range(5):
            for j in range(5):
                if self.board[i][j] == 'T':
                    operations = x_not_equals_y_operations
                    if i % 2 == j % 2:
                        operations = x_equals_y_operations

                    for offset_x, offset_y in operations:
                        next_i, next_j = i + offset_x, j + offset_y
                        if is_inside_board(next_i, next_j) and self.is_vacant(next_i, next_j):
                            moves.append(Move("m", (i, j), (next_i, next_j), None))
        return moves

    def eat_goats(self):
        moves = []
        for i in range(5):
            for j in range(5):
                if self.board[i][j] == 'T':
                    operations = x_not_equals_y_operations
                    if i % 2 == j % 2:
                        operations = x_equals_y_operations

                    for offset_x, offset_y in operations:
                        next_i, next_j = i + offset_x, j + offset_y
                        if is_inside_board(next_i, next_j) and self.board[next_i][next_j] == 'G':
                            next_next_i, next_next_j = i + 2 * offset_x, j + 2 * offset_y
                            if is_inside_board(next_next_i, next_next_j) and self.board[next_next_i][next_next_j] == '_':
                                moves.append(Move('e', (i, j), (next_next_i, next_next_j), (next_i, next_j)))
        return  moves



    def generate_move_list(self, is_max):
        move_list = []

        # Goat is minimizing
        if not is_max:
            if self.goats_in_hand > 0:
                move_list.extend(self.place_goats())
            else:
                move_list.extend(self.move_goats())
        # Tiger is maximizing
        else:
            move_list.extend(self.eat_goats())
            move_list.extend(self.move_tigers())
        return move_list

    def make_move(self, move, is_max):
        object_to_be_placed = 'T' if is_max else 'G'
        _, frm, to, inter = move
        if move.type == "p":
            row, col = to
            self.board[row][col] = object_to_be_placed
            self.goats_in_hand -= 1
        elif move.type == "m":
            row1, col1 = frm
            row2, col2 = to

            self.board[row1][col1] = '_'
            self.board[row2][col2] = object_to_be_placed
        elif move.type == "e":
            row1, col1 = frm
            goat_x, goat_y = inter
            row2, col2 = to
            self.dead_goats += 1
            self.board[row1][col1] = '_'
            self.board[goat_x][goat_y] = '_'
            self.board[row2][col2] = object_to_be_placed



    def revert_move(self, move,  is_max):
        object_to_be_placed = 'T' if is_max else 'G'
        _, frm, to, inter = move
        if move.type == "p":
            row, col = to
            self.board[row][col] = '_'
            self.goats_in_hand += 1
        elif move.type == "m":
            row1, col1 = frm
            row2, col2 = to

            self.board[row1][col1] = object_to_be_placed
            self.board[row2][col2] = '_'
        elif move.type == "e":
            row1, col1 = frm
            goat_x, goat_y = inter
            row2, col2 = to
            self.dead_goats -= 1
            self.board[row1][col1] = object_to_be_placed
            self.board[goat_x][goat_y] = 'G'
            self.board[row2][col2] = '_'

    def minimax(self, is_max=True, depth=0, alpha=-INF, beta=INF):
        score = self.evaluate(depth)

        if depth == self.depth or abs(score) == INF:
            return score


        if not is_max:
            value = INF

            for move in self.generate_move_list(is_max):
                self.make_move(move, is_max)
                current_value = self.minimax(True, depth + 1, alpha, beta)
                beta = min(beta, current_value)

                if current_value == value and depth == 0:
                    self.best_move = move
                if current_value < value:

                    value = current_value
                    beta = min(beta, value)
                    if depth == 0:
                        self.best_move = move

                self.revert_move(move, is_max)
                if alpha >= beta:
                    break
            return value

        else:
            value = -INF
            for move in self.generate_move_list(is_max):
                self.make_move(move, is_max)
                current_value = self.minimax(False, depth + 1, alpha, beta)
                alpha = max(alpha, value)
                if current_value == value and depth == 0:
                    self.best_move = move
                if current_value > value:

                    value = current_value
                    alpha = max(alpha, value)
                    if depth == 0:
                        self.best_move = move
                self.revert_move(move, is_max)

                if alpha >= beta:
                    break
            return value

    def best_tiger_move(self):
        self.minimax()
        return self.best_move

    def best_goat_move(self):
        self.minimax(is_max=False)
        return self.best_move

    def make_best_move(self):
        if self.turn == "Goat":
            move = self.best_goat_move()
        else:
            move = self.best_tiger_move()
        if self.turn == "Goat":
            is_max = False
        else:
            is_max = True
        self.make_move(move, is_max)


    def get_best_move(self):
        if self.turn == "Goat":
            move = self.best_goat_move()
        else:
            move = self.best_tiger_move()

        return move

# The heuristic value for the tiger piece was calculated based on the number of goats in the board, mobility of the piece and number of possible captures.