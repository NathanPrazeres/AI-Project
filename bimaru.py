# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 47:
# 103145 Nathaniel Prazeres
# 102890 David Nunes

import sys
from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)

NUM_EDGES = 12
NUM_MIDDLES = 4
NUM_CIRCLES = 4

TOP = ['T', 't']
BOTTOM = ['B', 'b']
LEFT = ['L', 'l']
RIGHT = ['R', 'r']
CIRCLE = ['C', 'c']
MIDDLE = ['M', 'm']
EDGES = [x for x in TOP + BOTTOM + LEFT + RIGHT]
EMPTY_SPACE = [None, '.', 'W']
EMPTY_ADJACENT = [(x, y) for x in EMPTY_SPACE for y in EMPTY_SPACE]

BATTLESHIP_V = [(w, x, y, z) for w in TOP for x in MIDDLE for y in MIDDLE for z in BOTTOM]
BATTLESHIP_H = [(w, x, y, z) for w in LEFT for x in MIDDLE for y in MIDDLE for z in RIGHT]

CRUISER_V = [(w, x, y) for w in TOP for x in MIDDLE for y in BOTTOM]
CRUISER_H = [(w, x, y) for w in LEFT for x in MIDDLE for y in RIGHT]

DESTROYER_V = [(w, x) for w in TOP for x in BOTTOM]
DESTROYER_H = [(w, x) for w in LEFT for x in RIGHT]

class BimaruState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = BimaruState.state_id
        BimaruState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    def get_board(self):
        return self.board
    

    # TODO: outros metodos da classe

####################################################################################################

class Board:
    """Representação interna de um tabuleiro de Bimaru."""
    hints = []
    
    num_battleships = 1
    num_cruisers = 2
    num_destroyers = 3
    num_submarines = 4

    def __init__(self, rows: int, cols: int):
        """Construtor: recebe o número de linhas e colunas do tabuleiro."""
        self.rows = rows
        self.cols = cols
        self.board = [[None for _ in range(cols + 1)] for _ in range(rows + 1)] # +1 para guardar os valores totais da linha e coluna

    """ def get_n_rows(self):
        return self.rows
    
    def get_n_cols(self):
        return self.cols """
    
    def isolated(self, row: int, col: int) -> bool:
        """Verifica se a posição é isolada, ou seja, não tem barcos adjacentes (nem na diagonal)."""
        return self.adjacent_horizontal_values(row, col) == EMPTY_ADJACENT \
            and self.adjacent_vertical_values(row, col) == EMPTY_ADJACENT \
            and self.adjacent_vertical_values(row, col - 1) == EMPTY_ADJACENT \
            and self.adjacent_vertical_values(row, col + 1) == EMPTY_ADJACENT \

    def copy_board(self):
        """Devolve uma cópia do tabuleiro."""
        new_board = Board(self.rows, self.cols)
        new_board.board = [[self.board[row][col] for col in range(self.cols + 1)] for row in range(self.rows + 1)]
        new_board.num_battleships = self.num_battleships
        new_board.num_cruisers = self.num_cruisers
        new_board.num_destroyers = self.num_destroyers
        new_board.num_submarines = self.num_submarines
        return new_board
    
    def set_value(self, row: int, col: int, value):
        """Altera o valor na respetiva posição do tabuleiro."""
        self.board[row][col] = value

    def get_value(self, row: int, col: int):
        """Devolve o valor na respetiva posição do tabuleiro."""
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return None
        return self.board[row][col]
    
    def get_row_total(self, row: int) -> int:
        """Devolve o número de barcos na linha."""
        return int(self.board[row][self.cols])
    
    def get_col_total(self, col: int) -> int:
        """Devolve o número de barcos na coluna."""
        return int(self.board[self.rows][col])
    
    def lower_total(self, row: int, col: int):
        """Diminui o número de barcos por colocar na linha e coluna."""
        self.set_value(row, self.cols, self.get_row_total(row) - 1)
        self.set_value(self.rows, col, self.get_col_total(col) - 1)

    def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""
        return (self.get_value(row - 1, col), self.get_value(row + 1, col))

    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""
        return (self.get_value(row, col - 1), self.get_value(row, col + 1))

    @staticmethod
    def parse_instance(from_input=sys.stdin):
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.

        Por exemplo:
            $ python3 bimaru.py < input_T01

            > from sys import stdin
            > line = stdin.readline().split()
        """
        rows = from_input.readline().split()[1:]
        cols = from_input.readline().split()[1:]
        n_rows = len(rows)
        n_cols = len(cols)
        board = Board(n_rows, n_cols)

        # Para guardar os valores do número de navios que podem estar na linha e coluna
        for row in range(n_rows):
            board.set_value(row, n_cols, rows[row])
        for col in range(n_cols):
            board.set_value(n_rows, col, cols[col])

        n_hints = eval(from_input.readline())
        for _ in range(n_hints):
            hint = from_input.readline().split()[1:]
            board.set_value(int(hint[0]), int(hint[1]), hint[2])
            if hint[2] != 'W':
                board.hints.append((int(hint[0]), int(hint[1]), hint[2]))
                board.lower_total(int(hint[0]), int(hint[1]))

        board.remove_complete_hints()
        return board
    
    def remove_complete_hints(self):
        new_hints = list(self.hints)
        for hint in new_hints:
            row, col = hint[0], hint[1]
            if self.get_value(row, col) == 'C':
                self.num_submarines -= 1
                self.hints.remove(hint)
            if self.get_value(row, col) == 'T':
                if self.get_value(row + 1, col) == 'B':
                    self.num_destroyers -= 1
                    self.hints.remove(hint)
                    self.hints.remove((row + 1, col, self.get_value(row + 1, col)))
                elif self.get_value(row + 1, col) == 'M':
                    if self.get_value(row + 2, col) == 'B':
                        self.num_cruisers -= 1
                        self.hints.remove(hint)
                        self.hints.remove((row + 1, col, self.get_value(row + 1, col)))
                        self.hints.remove((row + 2, col, self.get_value(row + 2, col)))
                    elif self.get_value(row + 2, col) == 'M':
                        if self.get_value(row + 3, col) == 'B':
                            self.num_battleships -= 1
                            self.hints.remove(hint)
                            self.hints.remove((row + 1, col, self.get_value(row + 1, col)))
                            self.hints.remove((row + 2, col, self.get_value(row + 2, col)))
                            self.hints.remove((row + 3, col, self.get_value(row + 3, col)))
            elif self.get_value(row, col) == 'L':
                if self.get_value(row, col + 1) == 'R':
                    self.num_destroyers -= 1
                    self.hints.remove(hint)
                    self.hints.remove((row, col + 1, self.get_value(row, col + 1)))
                elif self.get_value(row, col + 1) == 'M':
                    if self.get_value(row, col + 2) == 'R':
                        self.num_cruisers -= 1
                        self.hints.remove(hint)
                        self.hints.remove((row, col + 1, self.get_value(row, col + 1)))
                        self.hints.remove((row, col + 2, self.get_value(row, col + 2)))
                    elif self.get_value(row, col + 2) == 'M':
                        if self.get_value(row, col + 3) == 'R':
                            self.num_battleships -= 1
                            self.hints.remove(hint)
                            self.hints.remove((row, col + 1, self.get_value(row, col + 1)))
                            self.hints.remove((row, col + 2, self.get_value(row, col + 2)))
                            self.hints.remove((row, col + 3, self.get_value(row, col + 3)))

    def print_board(self):
        """Imprime o tabuleiro no standard output (stdout)."""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.get_value(row, col) is None:
                    print('.', end='')
                else:
                    print(self.get_value(row, col), end='')
            print()

    def board_toString(self):
        """Devolve o tabuleiro como uma string."""
        string = ''
        for row in range(self.rows):
            for col in range(self.cols):
                if self.get_value(row, col) is None:
                    string += '.'
                else:
                    string += self.get_value(row, col)
            string += '\n'
        return string

####################################################################################################

class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        self.state = BimaruState(board)
        super().__init__(self.state)

    def incomplete_ships(self, state: BimaruState):
        """Devolve as ações possíveis para completar navios incompletos."""
        valid_actions = []
        board: Board = state.get_board()
        hints = board.hints
        for hint in hints:
            row, col, hint_type = hint[0], hint[1], hint[2]
            if hint_type == 'T':
                if board.get_value(row + 1, col) is None:
                    if board.num_destroyers > 0:
                        valid_actions.append((row, col, ' b', 'v'))
                    if board.get_value(row + 2, col) is None and board.adjacent_horizontal_values(row + 2, col) in EMPTY_ADJACENT \
                    and board.adjacent_horizontal_values(row + 3, col) in EMPTY_ADJACENT and board.get_col_total(col) > 1 and board.get_row_total(row + 2) >= 1:
                        if board.get_value(row + 3, col) is None:
                            valid_actions.append((row, col, ' mb', 'v'))
                            if board.get_value(row + 4, col) is None and board.adjacent_horizontal_values(row + 4, col) in EMPTY_ADJACENT \
                            and board.get_col_total(col) > 2 and board.get_row_total(row + 3) >= 1:
                                valid_actions.append((row, col, ' mmb', 'v'))
                        elif board.get_value(row + 3, col) in BOTTOM:
                            valid_actions.append((row, col, ' mm ', 'v'))
                    elif board.get_value(row + 2, col) in MIDDLE:
                        if board.get_value(row + 3, col) is None:
                            valid_actions.append((row, col, ' m b', 'v'))
                        elif board.get_value(row + 3, col) in BOTTOM:
                            valid_actions.append((row, col, ' m  ', 'v'))
                    elif board.get_value(row + 2, col) in BOTTOM:
                        valid_actions.append((row, col, ' m ', 'v'))
                elif board.get_value(row + 1, col) in MIDDLE:
                    if board.get_value(row + 2, col) is None:
                        valid_actions.append((row, col, '  b', 'v'))
                        if board.get_value(row + 3, col) is None and board.get_col_total(col) > 1 and board.get_row_total(row + 3) >= 1 \
                        and board.get_value(row + 4, col) is None and board.adjacent_horizontal_values(row + 4, col) in EMPTY_ADJACENT:
                            valid_actions.append((row, col, '  mb', 'v'))
                        elif board.get_value(row + 3, col) in BOTTOM:
                            valid_actions.append((row, col, '  m ', 'v'))
                    elif board.get_value(row + 2, col) in MIDDLE and board.get_value(row + 3, col) is None:
                        valid_actions.append((row, col, '   b', 'v'))
                    
            elif hint_type == 'L':
                if board.get_value(row, col + 1) is None:
                    if board.num_destroyers > 0:
                        valid_actions.append((row, col, ' r', 'h'))
                    if board.get_value(row, col + 2) is None and board.adjacent_vertical_values(row, col + 2) in EMPTY_ADJACENT \
                    and board.adjacent_vertical_values(row, col + 3) in EMPTY_ADJACENT and board.get_row_total(row) > 1 and board.get_col_total(col + 2) >= 1:
                        if board.get_value(row, col + 3) is None:
                            valid_actions.append((row, col, ' mr', 'h'))
                            if board.get_value(row, col + 4) is None and board.adjacent_vertical_values(row, col + 4) in EMPTY_ADJACENT \
                            and board.get_row_total(row) > 2 and board.get_col_total(col + 3) >= 1:
                                valid_actions.append((row, col, ' mmr', 'h'))
                        elif board.get_value(row, col + 3) in RIGHT:
                            valid_actions.append((row, col, ' mm ', 'h'))
                    elif board.get_value(row, col + 2) in MIDDLE:
                        if board.get_value(row, col + 3) is None:
                            valid_actions.append((row, col, ' m r', 'h'))
                        elif board.get_value(row, col + 3) in RIGHT:
                            valid_actions.append((row, col, ' m  ', 'h'))
                    elif board.get_value(row, col + 2) in RIGHT:
                        valid_actions.append((row, col, ' m ', 'h'))
                elif board.get_value(row, col + 1) in MIDDLE:
                    if board.get_value(row, col + 2) is None:
                        valid_actions.append((row, col, '  r', 'h'))
                        if board.get_value(row, col + 3) is None and board.get_row_total(row) > 1 and board.get_col_total(col + 3) >= 1 \
                        and board.get_value(row, col + 4) is None and board.adjacent_vertical_values(row, col + 4) in EMPTY_ADJACENT:
                            valid_actions.append((row, col, '  mr', 'h'))
                        elif board.get_value(row, col + 3) in RIGHT:
                            valid_actions.append((row, col, '  m ', 'h'))
                    elif board.get_value(row, col + 2) in MIDDLE:
                        valid_actions.append((row, col, '   r', 'h'))
 
            elif hint_type == 'R':
                if board.get_value(row, col - 1) is None:
                    if board.num_destroyers > 0:
                        valid_actions.append((row, col - 1, 'l ', 'h'))
                    if col > 1 and board.get_value(row, col - 2) is None and board.adjacent_vertical_values(row, col - 2) in EMPTY_ADJACENT \
                    and board.adjacent_vertical_values(row, col - 3) in EMPTY_ADJACENT and board.get_row_total(row) > 1 and board.get_col_total(col - 2) >= 1:
                        if board.get_value(row, col - 3) is None:
                            valid_actions.append((row, col - 2, 'lm ', 'h'))
                            if col > 2 and board.get_value(row, col - 4) is None and board.adjacent_vertical_values(row, col - 4) in EMPTY_ADJACENT \
                            and board.get_row_total(row) > 2 and board.get_col_total(col - 3) >= 1:
                                valid_actions.append((row, col - 3, 'lmm ', 'h'))
                        elif board.get_value(row, col - 3) in LEFT:
                            valid_actions.append((row, col - 3, ' mm ', 'h'))
                    elif board.get_value(row, col - 2) in MIDDLE:
                        if board.get_value(row, col - 3) is None:
                            valid_actions.append((row, col - 3, 'l m ', 'h'))
                        elif board.get_value(row, col - 3) in LEFT:
                            valid_actions.append((row, col - 3, '  m ', 'h'))
                    elif board.get_value(row, col - 2) in LEFT:
                        valid_actions.append((row, col - 2, ' m ', 'h'))
                elif board.get_value(row, col - 1) in MIDDLE:
                    if board.get_value(row, col - 2) is None:
                        valid_actions.append((row, col - 2, 'l  ', 'h'))
                        if board.get_value(row, col - 3) is None and board.get_row_total(row) > 1 and board.get_col_total(col - 3) >= 1 \
                        and board.get_value(row, col - 4) is None and board.adjacent_vertical_values(row, col - 4) in EMPTY_ADJACENT:
                            valid_actions.append((row, col - 3, 'lm  ', 'h'))
            
            elif hint_type == 'B':
                if board.get_value(row - 1, col) is None:
                    if board.num_destroyers > 0:
                        valid_actions.append((row - 1, col, 't ', 'v'))
                    if row > 1 and board.get_value(row - 2, col) is None and board.adjacent_horizontal_values(row - 2, col) in EMPTY_ADJACENT \
                    and board.adjacent_horizontal_values(row - 3, col) in EMPTY_ADJACENT and board.get_col_total(col) > 1 and board.get_row_total(row - 2) >= 1:
                        if board.get_value(row - 3, col) is None:
                            valid_actions.append((row - 2, col, 'tm ', 'v'))
                            if row > 2 and board.get_value(row - 4, col) is None and board.adjacent_horizontal_values(row - 4, col) in EMPTY_ADJACENT \
                            and board.get_col_total(col) > 2 and board.get_row_total(row - 3) >= 1:
                                valid_actions.append((row - 3, col, 'tmm', 'v'))
                        elif board.get_value(row - 3, col) in TOP:
                            valid_actions.append((row - 3, col, ' mm ', 'v'))
                    elif board.get_value(row - 2, col) in MIDDLE:
                        if board.get_value(row - 3, col) is None:
                            valid_actions.append((row - 3, col, 't m ', 'v'))
                        elif board.get_value(row - 3, col) in TOP:
                            valid_actions.append((row - 3, col, '  m ', 'v'))
                    elif board.get_value(row - 2, col) in TOP:
                        valid_actions.append((row - 2, col, ' m ', 'v'))
                elif board.get_value(row - 1, col) in MIDDLE:
                    if board.get_value(row - 2, col) is None:
                        valid_actions.append((row - 2, col, 't  ', 'v'))
                        if board.get_value(row - 3, col) is None and board.get_col_total(col) > 1 and board.get_row_total(row - 3) >= 1 \
                        and board.get_value(row - 4, col) is None and board.adjacent_horizontal_values(row - 4, col) in EMPTY_ADJACENT:
                            valid_actions.append((row - 3, col, 'tm  ', 'v'))

            elif hint_type == 'M':

                # horizontal

                if col > 0 and col < board.cols - 1 and board.get_row_total(row) > 1 \
                and board.adjacent_vertical_values(row, col) in EMPTY_ADJACENT:
                    
                    if board.get_value(row, col - 1) is None and board.get_col_total(col - 1) > 0 \
                    and board.get_value(row, col + 1) is None and board.get_col_total(col + 1) > 0 \
                    and board.adjacent_vertical_values(row, col - 1) in EMPTY_ADJACENT \
                    and board.adjacent_vertical_values(row, col + 1) in EMPTY_ADJACENT:
                        
                        if board.get_value(row, col + 2) in EMPTY_SPACE and board.adjacent_vertical_values(row, col + 2) in EMPTY_ADJACENT:
                            if board.get_value(row, col - 2) is None and board.adjacent_vertical_values(row, col - 2) in EMPTY_ADJACENT:
                                valid_actions.append((row, col - 1, 'l r', 'h'))
                            if col > 2 and board.get_row_total(row) > 2 and board.get_value(row, col - 2) is None and board.get_col_total(col - 2) > 0 \
                            and board.get_value(row, col - 3) is None and board.adjacent_vertical_values(row, col - 3) in EMPTY_ADJACENT and row > 1:
                                valid_actions.append((row, col - 2, 'lm r', 'h'))
                            if col < board.cols - 2 and board.get_row_total(row) > 2 and board.get_value(row, col + 2) is None and board.get_col_total(col + 2) > 0 \
                            and board.get_value(row, col + 3) is None and board.adjacent_vertical_values(row, col + 3) in EMPTY_ADJACENT and row > board.rows - 2:
                                valid_actions.append((row, col - 1, 'l mr', 'h'))
                            elif board.get_value(row, col - 2) in LEFT:
                                valid_actions.append((row, col - 2, ' m r', 'h'))
                        elif board.get_value(row, col + 2) in RIGHT and board.get_value(row, col - 2) is None \
                        and board.adjacent_vertical_values(row, col - 2) in EMPTY_ADJACENT:
                            valid_actions.append((row, col - 1, 'l m ', 'h'))

                    elif board.get_value(row, col + 1) in MIDDLE:
                        if board.get_value(row, col - 1) in LEFT:
                            valid_actions.append((row, col - 1, '   r', 'h'))
                        elif board.get_value(row, col + 2) in RIGHT:
                            valid_actions.append((row, col - 1, 'l   ', 'h'))
                        else:
                            valid_actions.append((row, col - 1, 'l  r', 'h'))

                    elif board.get_value(row, col - 1) in MIDDLE:
                        if board.get_value(row, col - 2) in LEFT:
                            valid_actions.append((row, col - 2, '   r', 'h'))
                        elif board.get_value(row, col + 1) in RIGHT:
                            valid_actions.append((row, col - 2, 'l   ', 'h'))
                        else:
                            valid_actions.append((row, col - 2, 'l  r', 'h'))

                # vertical

                if board.get_col_total(col) > 1 and board.adjacent_horizontal_values(row, col) in EMPTY_ADJACENT:
                    if board.get_value(row - 1, col) is None and board.get_row_total(row - 1) > 0 \
                    and board.get_value(row + 1, col) is None and board.get_row_total(row + 1) > 0 \
                    and board.adjacent_horizontal_values(row - 1, col) in EMPTY_ADJACENT \
                    and board.adjacent_horizontal_values(row + 1, col) in EMPTY_ADJACENT:
                        
                        if board.get_value(row + 2, col) in EMPTY_SPACE and board.adjacent_horizontal_values(row + 2, col) in EMPTY_ADJACENT:
                            if board.get_value(row - 2, col) is None and board.adjacent_horizontal_values(row - 2, col) in EMPTY_ADJACENT:
                                valid_actions.append((row - 1, col, 't b', 'v'))
                            if row > 1 and board.get_value(row - 2, col) is None and board.get_row_total(row - 2) > 0 \
                            and board.get_value(row - 3, col) is None and board.adjacent_horizontal_values(row - 3, col) in EMPTY_ADJACENT and col > 1:
                                valid_actions.append((row - 2, col, 'tm b', 'v'))
                            if row < board.rows - 2 and board.get_value(row + 2, col) is None and board.get_row_total(row + 2) > 0 \
                            and board.get_value(row + 3, col) is None and board.adjacent_horizontal_values(row + 3, col) in EMPTY_ADJACENT and col > board.cols - 2:
                                valid_actions.append((row - 1, col, 't mb', 'v'))
                            elif board.get_value(row - 2, col) in TOP:
                                valid_actions.append((row - 2, col, ' m b', 'v'))
                        elif board.get_value(row + 2, col) in BOTTOM and board.get_value(row - 2, col) is None \
                        and board.adjacent_horizontal_values(row - 2, col) in EMPTY_ADJACENT:
                            valid_actions.append((row - 1, col, 't m ', 'v'))

                    elif board.get_value(row + 1, col) in MIDDLE:
                        if board.get_value(row - 1, col) in TOP:
                            valid_actions.append((row - 1, col, '   b', 'v'))
                        elif board.get_value(row + 2, col) in BOTTOM:
                            valid_actions.append((row - 1, col, 't   ', 'v'))
                        else:
                            valid_actions.append((row - 1, col, 't  b', 'v'))
                    
                    elif board.get_value(row - 1, col) in MIDDLE:
                        if board.get_value(row - 2, col) in TOP:
                            valid_actions.append((row - 2, col, '   b', 'v'))
                        elif board.get_value(row + 1, col) in BOTTOM:
                            valid_actions.append((row - 2, col, 't   ', 'v'))
                        else:
                            valid_actions.append((row - 2, col, 't  b', 'v'))

        return valid_actions

    def battleship_actions(self, state: BimaruState):
        valid_actions = []
        board: Board = state.get_board()
        # Try to place a horizinatal battleship
        for row in range(board.rows):
            if board.get_row_total(row) <= 3:
                continue
            for col in range(board.cols - 3):
                if board.get_col_total(col) <= 0 or board.get_col_total(col + 1) <= 0 \
                or board.get_col_total(col + 2) <= 0 or board.get_col_total(col + 3) <= 0:
                    continue
                if board.get_value(row, col) is None \
                and board.get_value(row, col + 1) is None \
                and board.get_value(row, col + 2) is None \
                and board.get_value(row, col + 3) is None \
                and (col == 0 or (board.adjacent_vertical_values(row, col - 1) in EMPTY_ADJACENT \
                and board.get_value(row, col - 1) in EMPTY_SPACE)) \
                and (col == board.cols - 4 or (board.adjacent_vertical_values(row, col + 4) in EMPTY_ADJACENT \
                and board.get_value(row, col + 4) in EMPTY_SPACE)) \
                and board.adjacent_vertical_values(row, col) in EMPTY_ADJACENT \
                and board.adjacent_vertical_values(row, col + 1) in EMPTY_ADJACENT \
                and board.adjacent_vertical_values(row, col + 2) in EMPTY_ADJACENT \
                and board.adjacent_vertical_values(row, col + 3) in EMPTY_ADJACENT:
                    valid_actions.append((row, col, 'lmmr', 'h'))
        # Try to place a vertical battleship
        for col in range(board.cols):
            if board.get_col_total(col) <= 3:
                continue
            for row in range(board.rows - 3):
                if board.get_row_total(row) <= 0 or board.get_row_total(row + 1) <= 0 \
                or board.get_row_total(row + 2) <= 0 or board.get_row_total(row + 3) <= 0:
                    continue
                if board.get_value(row, col) is None \
                and board.get_value(row + 1, col) is None \
                and board.get_value(row + 2, col) is None \
                and board.get_value(row + 3, col) is None \
                and (row == 0 or (board.adjacent_horizontal_values(row - 1, col) in EMPTY_ADJACENT \
                and board.get_value(row - 1, col) in EMPTY_SPACE)) \
                and (row == board.rows - 4 or (board.adjacent_horizontal_values(row + 4, col) in EMPTY_ADJACENT \
                and board.get_value(row + 4, col) in EMPTY_SPACE)) \
                and board.adjacent_horizontal_values(row, col) in EMPTY_ADJACENT \
                and board.adjacent_horizontal_values(row + 1, col) in EMPTY_ADJACENT \
                and board.adjacent_horizontal_values(row + 2, col) in EMPTY_ADJACENT \
                and board.adjacent_horizontal_values(row + 3, col) in EMPTY_ADJACENT:
                    valid_actions.append((row, col, 'tmmb', 'v'))
        return valid_actions

    def cruiser_actions(self, state: BimaruState):
        valid_actions = []
        board: Board = state.get_board()
        # Try to place a horizinatal cruiser
        for row in range(board.rows):
            if board.get_row_total(row) <= 2:
                continue
            for col in range(board.cols - 2):
                if board.get_col_total(col) <= 0 or board.get_col_total(col + 1) <= 0 or board.get_col_total(col + 2) <= 0:
                    continue
                if board.get_value(row, col) is None \
                and board.get_value(row, col + 1) is None \
                and board.get_value(row, col + 2) is None \
                and (col == 0 or (board.adjacent_vertical_values(row, col - 1) in EMPTY_ADJACENT \
                and board.get_value(row, col - 1) in EMPTY_SPACE)) \
                and (col == board.cols - 3 or (board.adjacent_vertical_values(row, col + 3) in EMPTY_ADJACENT \
                and board.get_value(row, col + 3) in EMPTY_SPACE)) \
                and board.adjacent_vertical_values(row, col) in EMPTY_ADJACENT \
                and board.adjacent_vertical_values(row, col + 1) in EMPTY_ADJACENT \
                and board.adjacent_vertical_values(row, col + 2) in EMPTY_ADJACENT:
                    valid_actions.append((row, col, 'lmr', 'h'))
        # Try to place a vertical cruiser
        for col in range(board.cols):
            if board.get_col_total(col) <= 2:
                continue
            for row in range(board.rows - 2):
                if board.get_row_total(row) <= 0 or board.get_row_total(row + 1) <= 0 or board.get_row_total(row + 2) <= 0:
                    continue
                if board.get_value(row, col) is None \
                and board.get_value(row + 1, col) is None \
                and board.get_value(row + 2, col) is None \
                and (row == 0 or (board.adjacent_horizontal_values(row - 1, col) in EMPTY_ADJACENT \
                and board.get_value(row - 1, col) in EMPTY_SPACE)) \
                and (row == board.rows - 3 or (board.adjacent_horizontal_values(row + 3, col) in EMPTY_ADJACENT \
                and board.get_value(row + 3, col) in EMPTY_SPACE)) \
                and board.adjacent_horizontal_values(row, col) in EMPTY_ADJACENT \
                and board.adjacent_horizontal_values(row + 1, col) in EMPTY_ADJACENT \
                and board.adjacent_horizontal_values(row + 2, col) in EMPTY_ADJACENT:
                    valid_actions.append((row, col, 'tmb', 'v'))
        return valid_actions
    
    def destroyer_actions(self, state: BimaruState):
        valid_actions = []
        board: Board = state.get_board()
        # Try to place a horizinatal cruiser
        for row in range(board.rows):
            if board.get_row_total(row) <= 1:
                continue
            for col in range(board.cols - 1):
                if board.get_col_total(col) <= 0 or board.get_col_total(col + 1) <= 0:
                    continue
                if board.get_value(row, col) is None \
                and board.get_value(row, col + 1) is None \
                and (col == 0 or (board.adjacent_vertical_values(row, col - 1) in EMPTY_ADJACENT \
                and board.get_value(row, col - 1) in EMPTY_SPACE)) \
                and (col == board.cols - 2 or (board.adjacent_vertical_values(row, col + 2) in EMPTY_ADJACENT \
                and board.get_value(row, col + 2) in EMPTY_SPACE)) \
                and board.adjacent_vertical_values(row, col) in EMPTY_ADJACENT \
                and board.adjacent_vertical_values(row, col + 1) in EMPTY_ADJACENT:
                    valid_actions.append((row, col, 'lr', 'h'))
        # Try to place a vertical cruiser
        for col in range(board.cols):
            if board.get_col_total(col) <= 1:
                continue
            for row in range(board.rows - 1):
                if board.get_row_total(row) <= 0 or board.get_row_total(row + 1) <= 0:
                    continue
                if board.get_value(row, col) is None \
                and board.get_value(row + 1, col) is None \
                and (row == 0 or (board.adjacent_horizontal_values(row - 1, col) in EMPTY_ADJACENT \
                and board.get_value(row - 1, col) in EMPTY_SPACE)) \
                and (row == board.rows - 2 or (board.adjacent_horizontal_values(row + 2, col) in EMPTY_ADJACENT \
                and board.get_value(row + 2, col) in EMPTY_SPACE)) \
                and board.adjacent_horizontal_values(row, col) in EMPTY_ADJACENT \
                and board.adjacent_horizontal_values(row + 1, col) in EMPTY_ADJACENT:
                    valid_actions.append((row, col, 'tb', 'v'))
        return valid_actions
    
    def submarine_actions(self, state: BimaruState):
        valid_actions = []
        board: Board = state.get_board()
        for row in range(board.rows):
            if board.get_row_total(row) <= 0:
                continue
            for col in range(board.cols):
                if board.get_col_total(col) <= 0:
                    continue
                if board.get_value(row, col) is None \
                and (col == 0 or board.adjacent_vertical_values(row, col - 1) in EMPTY_ADJACENT) \
                and (col == board.cols - 1 or board.adjacent_vertical_values(row, col + 1) in EMPTY_ADJACENT) \
                and (row == 0 or board.adjacent_horizontal_values(row - 1, col) in EMPTY_ADJACENT) \
                and (row == board.rows - 1 or board.adjacent_horizontal_values(row + 1, col) in EMPTY_ADJACENT) \
                and board.adjacent_vertical_values(row, col) in EMPTY_ADJACENT \
                and board.adjacent_horizontal_values(row, col) in EMPTY_ADJACENT:
                    valid_actions.append((row, col, 'c', ''))
        return valid_actions


    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        board: Board = state.get_board()
        actions = self.incomplete_ships(state)
        if actions == [] and board.num_battleships > 0:
            actions = self.battleship_actions(state)
        elif actions == [] and board.num_cruisers > 0:
            actions = self.cruiser_actions(state)
        elif actions == [] and board.num_destroyers > 0:
            actions = self.destroyer_actions(state)
        elif actions == [] and board.num_submarines > 0:
            actions = self.submarine_actions(state)
        print("Battleships: " + str(board.num_battleships), "Cruisers: " + str(board.num_cruisers), "Destroyers: " + str(board.num_destroyers), "Submarines: " + str(board.num_submarines))
        return actions


    def result(self, state: BimaruState, action) -> BimaruState:
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        old_board: Board = state.get_board()
        copy: Board = old_board.copy_board()
        child_state: BimaruState = BimaruState(copy)
        row = action[0]
        col = action[1]
        move = action[2]
        direction = action[3]
        for x in move:
            if x != ' ':
                child_state.board.set_value(int(row), int(col), str(x))
                child_state.board.lower_total(row, col)
            if direction == 'h':
                col += 1
            elif direction == 'v':
                row += 1
        if len(move) == 1:
            child_state.board.num_submarines -= 1
        elif len(move) == 2:
            child_state.board.num_destroyers -= 1
        elif len(move) == 3:
            child_state.board.num_cruisers -= 1
        elif len(move) == 4:
            child_state.board.num_battleships -= 1
        print(child_state.board.print_board())
        return child_state

            

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        if state is None:
            return False
        board: Board = state.get_board()
        if board.num_submarines != 0 or board.num_destroyers != 0 or \
        board.num_cruisers != 0 or board.num_battleships != 0:
            return False
        for row in range(board.rows):
            if board.get_row_total(row) != 0:
                return False
            for col in range(board.cols):
                if board.get_col_total(col) != 0:
                    return False
                
                if board.get_value(row, col) not in EMPTY_SPACE:
                    # Horizontal tests
                    if board.get_value(row, col) in ['L', 'l']:
                        if col >= board.cols - 1 or board.get_value(row, col + 1) not in ['M', 'm', 'R', 'r']:
                            return False
                        if board.get_value(row, col + 1) in ['M', 'm']:
                            if col >= board.cols - 2 or board.get_value(row, col + 2) not in ['M', 'm', 'R', 'r']:
                                return False
                            if board.get_value(row, col + 2) in ['M', 'm']:
                                if col >= board.cols - 3 or board.get_value(row, col + 3) not in ['R', 'r']:
                                    return False
                    
                    # Vertical tests
                    elif board.get_value(row, col) in ['T', 't']:
                        if row >= board.rows - 1 or board.get_value(row + 1, col) not in ['M', 'm', 'B', 'b']:
                            return False
                        if board.get_value(row + 1, col) in ['M', 'm']:
                            if row >= board.rows - 2 or board.get_value(row + 2, col) not in ['M', 'm', 'B', 'b']:
                                return False
                            if board.get_value(row + 2, col) in ['M', 'm']:
                                if row >= board.rows - 3 or board.get_value(row + 3, col) not in ['B', 'b']:
                                    return False

        return True

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        return 0


if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro do standard input,
    board: Board = Board.parse_instance()
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.

    problem = Bimaru(board)


    goal_node: Node = depth_first_tree_search(problem)

    print("Is goal?", problem.goal_test(goal_node.state))
    goal_node.state.get_board().print_board()
