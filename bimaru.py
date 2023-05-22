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
    
    def get_id(self):
        return self.id

    # TODO: outros metodos da classe

####################################################################################################

class Board:
    """Representação interna de um tabuleiro de Bimaru."""

    def __init__(self, rows: int, cols: int):
        """Construtor: recebe o número de linhas e colunas do tabuleiro."""
        self.rows = rows
        self.cols = cols
        self.board = [[None for _ in range(cols + 1)] for _ in range(rows + 1)] # +1 para guardar os valores totais da linha e coluna

    """ def get_n_rows(self):
        return self.rows
    
    def get_n_cols(self):
        return self.cols """

    def copy_board(self):
        """Devolve uma cópia do tabuleiro."""
        new_board = Board(self.rows, self.cols)
        new_board.board = [[self.board[row][col] for col in range(self.cols + 1)] for row in range(self.rows + 1)]
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
            board.lower_total(int(hint[0]), int(hint[1]))

        return board

    def print_board(self):
        """Imprime o tabuleiro no standard output (stdout)."""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.get_value(row, col) is None:   # DEBUG: remove when the program is finished
                    print('.', end='')
                else:
                    print(self.get_value(row, col), end='')
                # print(self.get_value(row, col), end='')
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
        valid_actions = []
        board: Board = state.get_board()
        board.print_board()
        for row in range(board.rows):
            if board.get_row_total(row) <= 0:
                continue
            for col in range(board.cols):
                if board.get_col_total(col) <= 0:
                    continue
                if board.adjacent_horizontal_values(row, col) not in EMPTY_ADJACENT \
                and board.adjacent_vertical_values(row, col) not in EMPTY_ADJACENT:
                    continue
                    
                if board.get_value(row, col) is None \
                and (col == 0 or board.adjacent_vertical_values(row, col - 1) in EMPTY_ADJACENT) \
                and (col == board.cols - 1 or board.adjacent_vertical_values(row, col + 1) in EMPTY_ADJACENT) \
                and board.get_value(row, col - 1) not in ['R', 'T', 'B', 'C', 'r', 't', 'b', 'c'] \
                and board.get_value(row, col + 1) not in ['L', 'T', 'B', 'C', 'l', 't', 'b', 'c'] \
                and board.get_value(row - 1, col) not in ['B', 'L', 'R', 'C', 'b', 'l', 'r', 'c'] \
                and board.get_value(row + 1, col) not in ['T', 'L', 'R', 'C', 't', 'l', 'r', 'c']:
                    
                    if board.adjacent_vertical_values(row, col) in EMPTY_ADJACENT \
                    and board.adjacent_horizontal_values(row, col) in EMPTY_ADJACENT:
                        valid_actions.append((row, col, 'c'))
                    # Trying to make a horizontal boat
                    if board.adjacent_vertical_values(row, col) in EMPTY_ADJACENT:
                        if board.get_value(row, col - 1) in EMPTY_SPACE and col != board.cols - 1:
                            valid_actions.append((row, col, 'l'))
                        if board.get_value(row, col + 1) in EMPTY_SPACE and col != 0:
                            valid_actions.append((row, col, 'r'))
                        # FIX: THE NEXT LINE MIGHT NEED TO BE REMOVED
                        # (since you can only make a middle if there is already a left or right)
                        if board.get_value(row, col - 1) in ['L', 'M', 'l', 'm'] \
                        or board.get_value(row, col + 1) in ['R', 'M', 'r', 'm']:
                            valid_actions.append((row, col, 'm'))
                    # Trying to make a vertical boat
                    if board.adjacent_horizontal_values(row, col) in EMPTY_ADJACENT:
                        if board.get_value(row - 1, col) in EMPTY_SPACE and row != board.rows - 1:
                            valid_actions.append((row, col, 't'))
                        if board.get_value(row + 1, col) in EMPTY_SPACE and row != 0:
                            valid_actions.append((row, col, 'b'))
                        # FIX: THE NEXT LINE MIGHT NEED TO BE REMOVED
                        # (since you can only make a middle if there is already a top or bottom)
                        if board.get_value(row - 1, col) in ['T', 'M', 't', 'm'] \
                        or board.get_value(row + 1, col) in ['B', 'M', 'b', 'm']:
                            valid_actions.append((row, col, 'm'))
        return valid_actions


    def result(self, state: BimaruState, action) -> BimaruState:
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        board: Board = state.get_board()
        copy: Board = board.copy_board()
        if action not in self.actions(state):
            print(action)
            state.get_board().print_board()
            raise ValueError('Invalid action')
        row = action[0]
        col = action[1]
        move = action[2]
        copy.set_value(int(row), int(col), str(move))
        copy.lower_total(row, col)
        child_state: BimaruState = BimaruState(copy)
        return child_state

            

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        board: Board = state.get_board()
        n_circles, n_middles, n_l, n_r, n_t, n_b = 0, 0, 0, 0, 0, 0
        for row in range(board.rows):
            if board.get_row_total(row) != 0:
                print("ROW TOTAL ERROR") # DEBUG
                return False
            for col in range(board.cols):
                if board.get_col_total(col) != 0:
                    print("COL TOTAL ERROR") # DEBUG
                    return False
                
                if board.get_value(row, col) is None:
                    board.set_value(row, col, '.')
                elif board.get_value(row, col) not in EMPTY_SPACE:

                    if board.get_value(row, col) in ['C', 'c']:
                        n_circles += 1
                    elif board.adjacent_vertical_values(row, col) in EMPTY_ADJACENT and \
                    board.adjacent_horizontal_values(row, col) in EMPTY_ADJACENT:
                        print("NON C EMPTY") # DEBUG
                        return False
                    elif board.get_value(row, col) in ['M', 'm']:
                        n_middles += 1
                        if board.get_value(row - 1, col) not in ['T', 't'] \
                        and board.get_value(row + 1, col) not in ['B', 'b'] \
                        and board.get_value(row, col - 1) not in ['L', 'l'] \
                        and board.get_value(row, col + 1) not in ['R', 'r']:
                            print("M ERROR") # DEBUG
                            return False
                    elif board.get_value(row, col) in ['T', 't']:
                        n_t += 1
                        if board.get_value(row + 1, col) not in ['B', 'b', 'M', 'm']:
                            print("T ERROR") # DEBUG
                            return False
                        elif board.get_value(row + 1, col) in ['M', 'm']:
                            if board.get_value(row + 2, col) not in ['B', 'b', 'M', 'm']:
                                print("T ERROR") # DEBUG
                                return False
                            if board.get_value(row + 2, col) in ['M', 'm'] and \
                            board.get_value(row + 3, col) not in ['B', 'b']:
                                print("T ERROR") # DEBUG
                                return False
                    elif board.get_value(row, col) in ['B', 'b']:
                        n_b += 1
                        if board.get_value(row - 1, col) not in ['T', 't', 'M', 'm']:
                            print("B ERROR") # DEBUG
                    elif board.get_value(row, col) in ['L', 'l']:
                        n_l += 1
                        if board.get_value(row, col + 1) not in ['R', 'r', 'M', 'm']:
                            print("L ERROR") # DEBUG
                            return False
                        elif board.get_value(row, col + 1) in ['M', 'm']:
                            if board.get_value(row, col + 2) not in ['R', 'r', 'M', 'm']:
                                print("L ERROR") # DEBUG
                                return False
                            if board.get_value(row, col + 2) in ['M', 'm'] and \
                            board.get_value(row, col + 3) not in ['R', 'r']:
                                print("L ERROR") # DEBUG
                                return False
                    elif board.get_value(row, col) in ['R', 'r']:
                        n_r += 1
                        if board.get_value(row, col - 1) not in ['L', 'l', 'M', 'm']:
                            print("R ERROR") # DEBUG

        if n_circles != NUM_CIRCLES or n_middles != NUM_MIDDLES or \
        (n_r + n_l + n_b + n_t) != NUM_EDGES or n_r != n_l or n_b != n_t:
            print("NUMBER OF SHIPS ERROR") # DEBUG
            return False
        return True

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        return 1

    # TODO: outros metodos da classe


if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro do standard input,
    board: Board = Board.parse_instance()
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.

    problem = Bimaru(board)
    print(problem.actions(problem.state))

    goal_node = depth_first_tree_search(problem)

    board.print_board()
