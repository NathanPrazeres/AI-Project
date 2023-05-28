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


TOP = ['T', 't']
BOTTOM = ['B', 'b']
LEFT = ['L', 'l']
RIGHT = ['R', 'r']
MIDDLE = ['M', 'm']
CIRCLE = ['C', 'c']
EMPTY_SPACE = [None, '.', 'W']
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
    impossible = False
    
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
    
    def fill_pos_water(self, row: int, col: int, value: str) -> bool:
        made_changes = False
        if not value in EMPTY_SPACE:
            if row > 0:
                if col > 0 and self.board[row-1][col-1] is None:
                    self.board[row-1][col-1] = '.'
                    made_changes = True
                if col < self.cols-1 and self.board[row-1][col+1] is None:
                    self.board[row-1][col+1] = '.'
                    made_changes = True
            if row < self.rows-1:
                if col > 0 and self.board[row+1][col-1] is None:
                    self.board[row+1][col-1] = '.'
                    made_changes = True
                if col < self.cols-1 and self.board[row+1][col+1] is None:
                    self.board[row+1][col+1] = '.'
                    made_changes = True
        if value in TOP:
            if self.board[row+1][col] is None:
                self.board[row+1][col] = 'x'
                self.lower_total(row+1, col)
                made_changes = True
            if row > 0 and self.board[row-1][col] is None:
                self.board[row-1][col] = '.'
                made_changes = True
        elif value in BOTTOM:
            if self.board[row-1][col] is None:
                self.board[row-1][col] = 'x'
                self.lower_total(row-1, col)
                made_changes = True
            if row < self.rows-1 and self.board[row+1][col] is None:
                self.board[row+1][col] = '.'
                made_changes = True
        elif value in LEFT:
            if self.board[row][col+1] is None:
                self.board[row][col+1] = 'x'
                self.lower_total(row, col+1)
                made_changes = True
            if col > 0 and self.board[row][col-1] is None:
                self.board[row][col-1] = '.'
                made_changes = True
        elif value in RIGHT:
            if self.board[row][col-1] is None:
                self.board[row][col-1] = 'x'
                self.lower_total(row, col-1)
                made_changes = True
            if col < self.cols-1 and self.board[row][col+1] is None:
                self.board[row][col+1] = '.'
                made_changes = True
        elif value in MIDDLE:
            # Horizontal
            if row == 0 or row == self.rows-1 or self.board[row-1][col] in ('.', 'W') or self.board[row+1][col] in ('.', 'W'):
                if self.board[row][col-1] is None:
                    self.board[row][col-1] = 'x'
                    self.lower_total(row, col-1)
                    made_changes = True
                if self.board[row][col+1] is None:
                    self.board[row][col+1] = 'x'
                    self.lower_total(row, col+1)
                    made_changes = True
            # Vertical
            elif col == 0 or col == self.cols-1 or self.board[row][col-1] in ('.', 'W') or self.board[row][col+1] in ('.', 'W'):
                if self.board[row-1][col] is None:
                    self.board[row-1][col] = 'x'
                    self.lower_total(row-1, col)
                    made_changes = True
                if self.board[row+1][col] is None:
                    self.board[row+1][col] = 'x'
                    self.lower_total(row+1, col)
                    made_changes = True
        elif value in CIRCLE:
            if row > 0 and self.board[row-1][col] is None:
                self.board[row-1][col] = '.'
                made_changes = True
            if row < self.rows-1 and self.board[row+1][col] is None:
                self.board[row+1][col] = '.'
                made_changes = True
            if col > 0 and self.board[row][col-1] is None:
                self.board[row][col-1] = '.'
                made_changes = True
            if col < self.cols-1 and self.board[row][col+1] is None:
                self.board[row][col+1] = '.'
                made_changes = True
        return made_changes


    def fill_board_water(self):
        made_changes = True
        while (made_changes):
            made_changes = False
            for row in range(self.rows):
                for col in range(self.cols):
                    if (self.get_row_total(row) == 0 or self.get_col_total(col) == 0) and self.get_value(row, col) is None:
                        self.set_value(row, col, '.')
                        made_changes = True
                    elif self.get_value(row, col) not in EMPTY_SPACE:
                        made_changes = made_changes or self.fill_pos_water(row, col, self.get_value(row, col))

            for row in range(self.rows):
                empty_cols = 0
                for col in range(self.cols):
                    if self.get_value(row, col) is None:
                        empty_cols += 1
                if empty_cols == self.get_col_total(col):
                    for col in range(self.cols):
                        if self.get_value(row, col) is None:
                            self.set_value(row, col, 'x')
                            self.lower_total(row, col)
                            self.fill_pos_water(row, col, 'x')
                            made_changes = True
            for col in range(self.cols):
                empty_rows = 0
                for row in range(self.rows):
                    if self.get_value(row, col) is None:
                        empty_rows += 1
                if empty_rows == self.get_row_total(row):
                    for row in range(self.rows):
                        if self.get_value(row, col) is None:
                            self.set_value(row, col, 'x')
                            self.lower_total(row, col)
                            self.fill_pos_water(row, col, 'x')
                            made_changes = True

    def complete_unknown(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.get_value(row, col) == 'x':
                    # Horizontal
                    if row == 0 or row == self.rows-1 or self.get_value(row-1, col) in ('.', 'W') or self.get_value(row+1, col) in ('.', 'W'):
                        if col == 0 or self.get_value(row, col-1) in ('.', 'W'):
                            self.set_value(row, col, 'l')
                        elif col == self.cols-1 or self.get_value(row, col+1) in ('.', 'W'):
                            self.set_value(row, col, 'r')
                        elif self.get_value(row, col-1) != None and self.get_value(row, col+1) != None:
                            self.set_value(row, col, 'm')
                    # Vertical
                    elif col == 0 or col == self.cols-1 or self.get_value(row, col-1) in ('.', 'W') or self.get_value(row, col+1) in ('.', 'W'):
                        if row == 0 or self.get_value(row-1, col) in ('.', 'W'):
                            self.set_value(row, col, 't')
                        elif row == self.rows-1 or self.get_value(row+1, col) in ('.', 'W'):
                            self.set_value(row, col, 'b')
                        elif self.get_value(row-1, col) != None and self.get_value(row+1, col) != None:
                            self.set_value(row, col, 'm')

    def possible_actions(self) -> list:
        """Devolve uma lista de ações possíveis."""
        actions = []
        for row in range(self.rows):
            for col in range(self.cols):
                # Try to place a horizontal battleship
                if self.get_row_total(row) > 0:
                    if (self.get_value(row, col) in [None] + TOP) and self.get_value(row, col+1) in (['x', None] + MIDDLE) \
                    and self.get_value(row, col+2) in (['x', None] + MIDDLE) and self.get_value(row, col+3) in (['x', None] + BOTTOM):
                        if self.get_value(row, col) is None:
                            actions.append((row, col, 'l'))
        return actions


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
                board.hints.append((int(hint[0]), int(hint[1])))
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
            elif self.get_value(row, col) == 'T':
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
                    print('◻', end='') #DEBUG
                else:
                    print(self.get_value(row, col), end='')
            print()

####################################################################################################

class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        self.state = BimaruState(board)
        super().__init__(self.state)

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        board: Board = state.get_board()
        actions = []
        # TODO
        return actions


    def result(self, state: BimaruState, action) -> BimaruState:
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        old_board: Board = state.get_board()
        copy: Board = old_board.copy_board()
        child_state: BimaruState = BimaruState(copy)
        # TODO
        return child_state           

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        board: Board = state.get_board()
        # TODO
        return True

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        return -node.depth*2

if __name__ == "__main__":
    board: Board = Board.parse_instance()

    problem = Bimaru(board)

    goal_node: Node = depth_first_tree_search(problem)

    goal_node.state.get_board().print_board()
