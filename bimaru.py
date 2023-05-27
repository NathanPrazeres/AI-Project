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
    recursive_best_first_search
)


TOP = ('T', 't')
BOTTOM = ('B', 'b')
LEFT = ('L', 'l')
RIGHT = ('R', 'r')
MIDDLE = ('M', 'm')
CIRCLE = ('C', 'c')
EMPTY_SPACE = (None, '.', 'W')
EMPTY_ADJACENT = [(x, y) for x in EMPTY_SPACE for y in EMPTY_SPACE]

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
    
    def fill_pos_water(self, row: int, col: int, value: str):
        if not value in EMPTY_SPACE:
            if row > 0:
                if col > 0 and self.board[row-1][col-1] != 'W':
                    self.board[row-1][col-1] = '.'
                if col < self.cols-1 and self.board[row-1][col+1] != 'W':
                    self.board[row-1][col+1] = '.'
            if row < self.rows-1:
                if col > 0 and self.board[row+1][col-1] != 'W':
                    self.board[row+1][col-1] = '.'
                if col < self.cols-1 and self.board[row+1][col+1] != 'W':
                    self.board[row+1][col+1] = '.'    
        if value in TOP:
            if row > 0 and self.board[row-1][col] != 'W':
                self.board[row-1][col] = '.'
            if col > 0:
                if self.board[row][col-1] != 'W':
                    self.board[row][col-1] = '.'
                if row < self.rows-2 and self.board[row+2][col-1] != 'W':
                    self.board[row+2][col-1] = '.'
            if col < self.cols-1:
                if self.board[row][col+1] != 'W':
                    self.board[row][col+1] = '.'
                if row < self.rows-2 and self.board[row+2][col+1] != 'W':
                    self.board[row+2][col+1] = '.'
        elif value in BOTTOM:
            if row < self.rows-1 and self.board[row+1][col] != 'W':
                self.board[row+1][col] = '.'
            if col > 0:
                if self.board[row][col-1] != 'W':
                    self.board[row][col-1] = '.'
                if row > 1 and self.board[row-2][col-1] != 'W':
                    self.board[row-2][col-1] = '.'
            if col < self.cols-1:
                if self.board[row][col+1] != 'W':
                    self.board[row][col+1] = '.'
                if row > 1 and self.board[row-2][col+1] != 'W':
                    self.board[row-2][col+1] = '.'
        elif value in LEFT:
            if col > 0 and self.board[row][col-1] != 'W':
                self.board[row][col-1] = '.'
            if row > 0:
                if self.board[row-1][col] != 'W':
                    self.board[row-1][col] = '.'
                if col < self.cols-2 and self.board[row-1][col+2] != 'W':
                    self.board[row-1][col+2] = '.'
            if row < self.rows-1:
                if self.board[row+1][col] != 'W':
                    self.board[row+1][col] = '.'
                if col < self.cols-2 and self.board[row+1][col+2] != 'W':
                    self.board[row+1][col+2] = '.'
        elif value in RIGHT:
            if col < self.cols-1 and self.board[row][col+1] != 'W':
                self.board[row][col+1] = '.'
            if row > 0:
                if self.board[row-1][col] != 'W':
                    self.board[row-1][col] = '.'
                if col > 1 and self.board[row-1][col-2] != 'W':
                        self.board[row-1][col-2] = '.'
            if row < self.rows-1:
                if self.board[row+1][col] != 'W':
                    self.board[row+1][col] = '.'
                if col > 1 and self.board[row+1][col-2] != 'W':
                        self.board[row+1][col-2] = '.'
        elif value in CIRCLE:
            if row > 0 and self.get_value(row-1, col) != 'W':
                self.set_value(row-1, col, '.')
            if row < self.rows-1 and self.get_value(row+1, col) != 'W':
                self.set_value(row+1, col, '.')
            if col > 0 and self.get_value(row, col-1) != 'W':
                self.set_value(row, col-1, '.')
            if col < self.cols-1 and self.get_value(row, col+1) != 'W':
                self.set_value(row, col+1, '.')
            
    def fill_board_water(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if (self.get_row_total(row) == 0 or self.get_col_total(col) == 0) and self.get_value(row, col) is None:
                    self.set_value(row, col, '.')
                elif self.get_value(row, col) not in EMPTY_SPACE:
                    if self.get_value(row, col) in MIDDLE:
                        # If M/m is connected to a horizontal boat
                        if not self.adjacent_horizontal_values(row, col) in EMPTY_ADJACENT and self.adjacent_vertical_values(row, col) in EMPTY_ADJACENT:
                            if row > 0:
                                if self.get_value(row-1, col) != 'W':
                                    self.set_value(row-1, col, '.')
                                if col > 1 and self.get_value(row-1, col-2) != 'W':
                                    self.set_value(row-1, col-2, '.')
                                if col < self.cols-2 and self.get_value(row-1, col+2) != 'W':
                                    self.set_value(row-1, col+2, '.')
                            if row < self.rows-1:
                                if self.get_value(row+1, col) != 'W':
                                    self.set_value(row+1, col, '.')
                                if col > 1 and self.get_value(row+1, col-2) != 'W':
                                    self.set_value(row+1, col-2, '.')
                                if col < self.cols-2 and self.get_value(row+1, col+2) != 'W':
                                    self.set_value(row+1, col+2, '.')
                        # If M/m is connected to a vertical boat
                        elif self.adjacent_horizontal_values(row, col) in EMPTY_ADJACENT and not self.adjacent_vertical_values(row, col) in EMPTY_ADJACENT:
                            if col > 0:
                                if self.get_value(row, col-1) != 'W':
                                    self.set_value(row, col-1, '.')
                                if row > 1 and self.get_value(row-2, col-1) != 'W':
                                    self.set_value(row-2, col-1, '.')
                                if row < self.rows-2 and self.get_value(row+2, col-1) != 'W':
                                    self.set_value(row+2, col-1, '.')
                            if col < self.cols-1:
                                if self.get_value(row, col+1) != 'W':
                                    self.set_value(row, col+1, '.')
                                if row > 1 and self.get_value(row-2, col+1) != 'W':
                                    self.set_value(row-2, col+1, '.')
                                if row < self.rows-2 and self.get_value(row+2, col+1) != 'W':
                                    self.set_value(row+2, col+1, '.')
                    self.fill_pos_water(row, col, self.get_value(row, col))

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
        board.fill_board_water()
        return board
    
    def remove_complete_hints(self):
        hints_copy = list(self.hints)
        used_hints = []
        for hint in hints_copy:
            row, col = hint[0], hint[1]
            if (row, col) in used_hints:
                continue
            if self.get_value(row, col) == 'C':
                self.num_submarines -= 1
                self.hints.remove(hint)
                used_hints.append((row, col))
            if self.get_value(row, col) == 'T':
                if self.get_value(row + 1, col) == 'B':
                    self.num_destroyers -= 1
                    self.hints.remove(hint)
                    self.hints.remove((row + 1, col, self.get_value(row + 1, col)))
                    used_hints.append((row, col))
                elif self.get_value(row + 1, col) == 'M':
                    if self.get_value(row + 2, col) == 'B':
                        self.num_cruisers -= 1
                        self.hints.remove(hint)
                        self.hints.remove((row + 1, col, self.get_value(row + 1, col)))
                        self.hints.remove((row + 2, col, self.get_value(row + 2, col)))
                        used_hints.append((row, col))
                    elif self.get_value(row + 2, col) == 'M':
                        if self.get_value(row + 3, col) == 'B':
                            self.num_battleships -= 1
                            self.hints.remove(hint)
                            self.hints.remove((row + 1, col, self.get_value(row + 1, col)))
                            self.hints.remove((row + 2, col, self.get_value(row + 2, col)))
                            self.hints.remove((row + 3, col, self.get_value(row + 3, col)))
                            used_hints.append((row, col))
            elif self.get_value(row, col) == 'L':
                if self.get_value(row, col + 1) == 'R':
                    self.num_destroyers -= 1
                    self.hints.remove(hint)
                    self.hints.remove((row, col + 1, self.get_value(row, col + 1)))
                    used_hints.append((row, col))
                elif self.get_value(row, col + 1) == 'M':
                    if self.get_value(row, col + 2) == 'R':
                        self.num_cruisers -= 1
                        self.hints.remove(hint)
                        self.hints.remove((row, col + 1, self.get_value(row, col + 1)))
                        self.hints.remove((row, col + 2, self.get_value(row, col + 2)))
                        used_hints.append((row, col))
                    elif self.get_value(row, col + 2) == 'M':
                        if self.get_value(row, col + 3) == 'R':
                            self.num_battleships -= 1
                            self.hints.remove(hint)
                            self.hints.remove((row, col + 1, self.get_value(row, col + 1)))
                            self.hints.remove((row, col + 2, self.get_value(row, col + 2)))
                            self.hints.remove((row, col + 3, self.get_value(row, col + 3)))
                            used_hints.append((row, col))

    def print_board(self):
        """Imprime o tabuleiro no standard output (stdout)."""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.get_value(row, col) is None:
                    print('!', end='') #DEBUG
                else:
                    print(self.get_value(row, col), end='')
            print()

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
            row = hint[0]
            col = hint[1]
            value = hint[2]
            if value == 'T':
                if board.get_value(row + 1, col) is None:
                    if board.get_value(row + 2, col) in EMPTY_SPACE:
                        if board.get_value(row + 3, col) != 'B':
                            valid_actions.insert(0, (row, col, ' b', 'v'))
                        if row < board.rows - 2 and board.get_value(row + 2, col) is None:
                            if board.get_value(row + 3, col) in EMPTY_SPACE:
                                if board.get_col_total(col) > 1:
                                    valid_actions.insert(0, (row, col, ' mb', 'v'))
                                if row < board.rows - 3 and board.get_value(row + 3, col) is None and board.get_col_total(col) > 2:
                                    valid_actions.insert(0, (row, col, ' mmb', 'v'))
                            elif board.get_value(row + 3, col) == 'B':
                                valid_actions.insert(0, (row, col, ' mm ', 'v'))
                    elif board.get_value(row + 2, col) == 'M':
                        if board.get_value(row + 3, col) is None:
                            valid_actions.insert(0, (row, col, ' m b', 'v'))
                        elif board.get_value(row + 3, col) == 'B':
                            valid_actions.insert(0, (row, col, ' m  ', 'v'))
                    elif board.get_value(row + 2, col) == 'B':
                        valid_actions.insert(0, (row, col, ' m ', 'v'))
                elif board.get_value(row + 1, col) == 'M':
                    if board.get_value(row + 2, col) is None:
                        if board.get_value(row + 3, col) in EMPTY_SPACE:
                            valid_actions.insert(0, (row, col, '  b', 'v'))
                            if row < board.rows - 3 and board.get_value(row + 3, col) is None and board.get_col_total(col) > 1:
                                valid_actions.insert(0, (row, col, '  mb', 'v'))
                        elif board.get_value(row + 3, col) == 'B':
                            valid_actions.insert(0, (row, col, '  m ', 'v'))
                    elif board.get_value(row + 2, col) == 'M' and board.get_value(row + 3, col) in EMPTY_SPACE:
                        valid_actions.insert(0, (row, col, '   b', 'v'))
            
            elif value == 'L':
                if board.get_value(row, col + 1) is None:
                    if board.get_value(row, col + 2) in EMPTY_SPACE:
                        if board.get_value(row, col + 3) != 'R':
                            valid_actions.insert(-1, (row, col, ' r', 'h'))
                        if col < board.cols - 2 and board.get_value(row, col + 2) is None:
                            if board.get_value(row, col + 3) in EMPTY_SPACE:
                                if board.get_row_total(row) > 1:
                                    valid_actions.insert(-1, (row, col, ' mr', 'h'))
                                if col < board.cols - 3 and board.get_value(row, col + 3) is None and board.get_row_total(row) > 2:
                                    valid_actions.insert(0, (row, col, ' mmr', 'h'))
                            elif board.get_value(row, col + 3) == 'R':
                                valid_actions.insert(0, (row, col, ' mm ', 'h'))
                    elif board.get_value(row, col + 2) == 'M':
                        if board.get_value(row, col + 3) is None:
                            valid_actions.insert(0, (row, col, ' m r', 'h'))
                        elif board.get_value(row, col + 3) == 'R':
                            valid_actions.insert(0, (row, col, ' m  ', 'h'))
                    elif board.get_value(row, col + 2) == 'R':
                        valid_actions.insert(-1, (row, col, ' m ', 'h'))
                elif board.get_value(row, col + 1) == 'M':
                    if board.get_value(row, col + 2) is None:
                        if board.get_value(row, col + 3) in EMPTY_SPACE:
                            valid_actions.insert(-1, (row, col, '  r', 'h'))
                            if col < board.cols - 3 and board.get_value(row, col + 3) is None and board.get_row_total(row) > 1:
                                valid_actions.insert(0, (row, col, '  mr', 'h'))
                        elif board.get_value(row, col + 3) == 'R':
                            valid_actions.insert(0, (row, col, '  m ', 'h'))
                    elif board.get_value(row, col + 2) == 'M' and board.get_value(row, col + 3) in EMPTY_SPACE:
                        valid_actions.insert(0, (row, col, '   r', 'h'))

            elif value == 'B' and not board.get_value(row - 1, col) in ('T', 'M') \
            and not board.get_value(row - 2, col) in ['T', 'M'] and board.get_value(row - 3, col) != 'T':
                if board.get_value(row - 1, col) is None:
                    if board.get_value(row - 2, col) in EMPTY_SPACE:
                        valid_actions.insert(-1, (row - 1, col, 't ', 'v'))
                    if row > 1 and board.get_value(row - 2, col) is None:
                        if board.get_value(row - 3, col) in EMPTY_SPACE:
                            if board.get_col_total(col) > 1:
                                valid_actions.insert(-1, (row - 2, col, 'tm ', 'v'))
                            if row > 2 and board.get_value(row - 3, col) is None and board.get_col_total(col) > 2:
                                valid_actions.insert(0, (row - 3, col, 'tmm ', 'v'))

            elif value == 'R' and not board.get_value(row, col - 1) in ('L', 'M') \
            and not board.get_value(row, col - 2) in ['L', 'M'] and board.get_value(row, col - 3) != 'L':
                if board.get_value(row, col - 1) is None:
                    if board.get_value(row, col - 2) in EMPTY_SPACE:
                        valid_actions.insert(-1, (row, col - 1, 'l ', 'h'))
                    if col > 1 and board.get_value(row, col - 2) is None:
                        if board.get_value(row, col - 3) in EMPTY_SPACE:
                            if board.get_row_total(row) > 1:
                                valid_actions.insert(-1, (row, col - 2, 'lm ', 'h'))
                            if col > 2 and board.get_value(row, col - 3) is None and board.get_row_total(row) > 2:
                                valid_actions.insert(0, (row, col - 3, 'lmm ', 'h'))
                    
            elif value == 'M':
                # Vertical
                if row > 0 and row < board.rows - 1:
                    if board.get_value(row - 1, col) is None and board.get_value(row - 2, col) in EMPTY_SPACE:
                        if board.get_value(row + 1, col) == 'B':
                            valid_actions.insert(-1, (row - 1, col, 't  ', 'v'))
                            if row > 1 and board.get_col_total(col) > 1 and board.get_value(row - 2, col) is None and board.get_value(row - 3, col) in EMPTY_SPACE:
                                valid_actions.insert(0, (row - 2, col, 'tm  ', 'v'))
                        elif board.get_value(row + 1, col) == 'M' and board.get_value(row + 2, col) == 'B':
                            valid_actions.insert(0, (row - 1, col, 't   ', 'v'))
                        if board.get_col_total(col) > 1:
                            if board.get_value(row + 1, col) is None:
                                if board.get_value(row + 2, col) in EMPTY_SPACE:
                                    valid_actions.insert(-1, (row - 1, col, 't b', 'v'))
                                    if board.get_col_total(col) > 2:
                                        if row > 1 and board.get_value(row - 2, col) is None and board.get_value(row - 3, col) in EMPTY_SPACE:
                                            valid_actions.insert(0, (row - 2, col, 'tm b', 'v'))
                                        if row < board.rows - 2 and board.get_value(row + 2, col) is None and board.get_value(row + 3, col) in EMPTY_SPACE:
                                            valid_actions.insert(0, (row - 1, col, 't mb', 'v'))
                                elif board.get_value(row + 2, col) == 'B':
                                    valid_actions.insert(0, (row - 1, col, 't m ', 'v'))
                            elif board.get_value(row + 1, col) == 'M' and board.get_value(row + 2, col) is None:
                                valid_actions.insert(0, (row - 1, col, 't  b', 'v'))

                # Horizontal
                if col > 0 and col < board.cols - 1:
                    if board.get_value(row, col - 1) is None and board.get_value(row, col - 2) in EMPTY_SPACE:
                        if board.get_value(row, col + 1) == 'R':
                            valid_actions.insert(-1, (row, col - 1, 'l  ', 'h'))
                            if col > 1 and board.get_row_total(row) > 1 and board.get_value(row, col - 2) is None and board.get_value(row, col - 3) in EMPTY_SPACE:
                                valid_actions.insert(0, (row, col - 2, 'lm  ', 'h'))
                        elif board.get_value(row, col + 1) == 'M' and board.get_value(row, col + 2) == 'R':
                            valid_actions.insert(0, (row, col - 1, 'l   ', 'h'))
                        if board.get_row_total(row) > 1:
                            if board.get_value(row, col + 1) is None:
                                if board.get_value(row, col + 2) in EMPTY_SPACE:
                                    valid_actions.insert(-1, (row, col - 1, 'l r', 'h'))
                                    if board.get_row_total(row) > 2:
                                        if col > 1 and board.get_value(row, col - 2) is None and board.get_value(row, col - 3) in EMPTY_SPACE:
                                            valid_actions.insert(0, (row, col - 2, 'lm r', 'h'))
                                        if col < board.cols - 2 and board.get_value(row, col + 2) is None and board.get_value(row, col + 3) in EMPTY_SPACE:
                                            valid_actions.insert(0, (row, col - 1, 'l mr', 'h'))
                                elif board.get_value(row, col + 2) == 'R':
                                    valid_actions.insert(0, (row, col - 1, 'l m ', 'h'))
                            elif board.get_value(row, col + 1) == 'M' and board.get_value(row, col + 2) is None:
                                valid_actions.insert(0, (row, col - 1, 'l  r', 'h'))
        return valid_actions

    def complete_ships(self, state: BimaruState):
        board: Board = state.get_board()
        valid_actions = []
        for row in range(board.rows):
            for col in range(board.cols):
                if board.num_battleships > 0:
                    if row < board.rows - 3 and board.get_col_total(col) > 3 and board.get_value(row, col) is None \
                    and board.get_value(row + 1, col) is None and board.get_value(row + 2, col) is None and board.get_value(row + 3, col) is None:
                        valid_actions.append((row, col, 'tmmb', 'v'))
                    if col < board.cols - 3 and board.get_row_total(row) > 3 and board.get_value(row, col) is None \
                        and board.get_value(row, col + 1) is None and board.get_value(row, col + 2) is None and board.get_value(row, col + 3) is None:
                        valid_actions.append((row, col, 'lmmr', 'h'))
                elif board.num_cruisers > 0:
                    if row < board.rows - 2 and board.get_col_total(col) > 2 and board.get_value(row, col) is None \
                    and board.get_value(row + 1, col) is None and board.get_value(row + 2, col) is None:
                        valid_actions.append((row, col, 'tmb', 'v'))
                    if col < board.cols - 2 and board.get_row_total(row) > 2 and board.get_value(row, col) is None \
                        and board.get_value(row, col + 1) is None and board.get_value(row, col + 2) is None:
                        valid_actions.append((row, col, 'lmr', 'h'))
                elif board.num_destroyers > 0:
                    if row < board.rows - 1 and board.get_col_total(col) > 1 and board.get_value(row, col) is None \
                    and board.get_value(row + 1, col) is None:
                        valid_actions.append((row, col, 'tb', 'v'))
                    if col < board.cols - 1 and board.get_row_total(row) > 1 and board.get_value(row, col) is None \
                        and board.get_value(row, col + 1) is None:
                        valid_actions.append((row, col, 'lr', 'h'))
                elif board.num_submarines > 0:
                    if board.get_value(row, col) is None and board.get_col_total(col) > 0 and board.get_row_total(row) > 0:
                        valid_actions.append((row, col, 'c', ''))
        return valid_actions

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        board: Board = state.get_board()
        actions = self.incomplete_ships(state)
        if actions == [] and (board.num_battleships + board.num_cruisers + board.num_destroyers + board.num_submarines) > 0:
            actions = self.complete_ships(state)
        print(actions) # DEBUG
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
        child_state.board.fill_board_water()
        child_state.board.print_board() # DEBUG
        return child_state           

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        board: Board = state.get_board()
        if board.num_submarines != 0 or board.num_destroyers != 0 or \
        board.num_cruisers != 0 or board.num_battleships != 0:
            return False
        return True

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        return -node.depth*2

if __name__ == "__main__":
    board: Board = Board.parse_instance()

    problem = Bimaru(board)

    goal_node: Node = depth_first_tree_search(problem)

    goal_node.state.get_board().print_board()
