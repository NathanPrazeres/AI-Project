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

    num_battleships = 1
    num_cruisers = 2
    num_destroyers = 3
    num_submarines = 4

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
        self.CORNER_COORDS = ((x, y) for x in (0, self.rows) for y in (0, self.cols))

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
            if hint[2] != 'W':
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

    def brute_force_actions(self, state: BimaruState):
        valid_actions = []
        board: Board = state.get_board()
        for row in range(board.rows):
            if board.get_row_total(row) <= 0:
                continue
            for col in range(board.cols):
                if board.get_col_total(col) <= 0:
                    continue
                # Making sure at least one of the axies is empty
                if board.adjacent_horizontal_values(row, col) not in EMPTY_ADJACENT \
                and board.adjacent_vertical_values(row, col) not in EMPTY_ADJACENT:
                    continue
                # Making sure there are no adjacent tiles that would invalidate the creation of a ship
                if board.get_value(row, col) is None \
                and (col == 0 or board.adjacent_vertical_values(row, col - 1) in EMPTY_ADJACENT) \
                and (col == board.cols - 1 or board.adjacent_vertical_values(row, col + 1) in EMPTY_ADJACENT) \
                and board.get_value(row, col - 1) not in (RIGHT + TOP + BOTTOM + CIRCLE) \
                and board.get_value(row, col + 1) not in (LEFT + TOP + BOTTOM + CIRCLE) \
                and board.get_value(row - 1, col) not in (RIGHT + LEFT + BOTTOM + CIRCLE) \
                and board.get_value(row + 1, col) not in (RIGHT + TOP + LEFT + CIRCLE):
                    
                    if board.adjacent_vertical_values(row, col) in EMPTY_ADJACENT \
                    and board.adjacent_horizontal_values(row, col) in EMPTY_ADJACENT:
                        valid_actions.append((row, col, 'c'))

                    # Trying to make a horizontal boat
                    if board.adjacent_vertical_values(row, col) in EMPTY_ADJACENT:
                        if board.get_value(row, col - 1) in EMPTY_SPACE and col != board.cols - 1 \
                        and board.get_value(row, col - 2) not in LEFT:
                            valid_actions.append((row, col, 'l'))
                        if board.get_value(row, col + 1) in EMPTY_SPACE and col != 0 \
                        and board.get_value(row, col - 1) in LEFT + MIDDLE \
                        and board.get_value(row, col + 2) not in RIGHT:
                            valid_actions.append((row, col, 'r'))
                        # FIX: THE NEXT LINE MIGHT NEED TO BE REMOVED
                        # (since you can only make a middle if there is already a left)
                        if board.get_value(row, col - 1) in LEFT + MIDDLE \
                        and ((row, col) not in board.CORNER_COORDS):
                            valid_actions.append((row, col, 'm'))

                    # Trying to make a vertical boat
                    if board.adjacent_horizontal_values(row, col) in EMPTY_ADJACENT:
                        if board.get_value(row - 1, col) in EMPTY_SPACE and row != board.rows - 1 \
                        and board.get_value(row - 2, col) not in TOP:
                            valid_actions.append((row, col, 't'))
                        if board.get_value(row + 1, col) in EMPTY_SPACE and row != 0 \
                        and board.get_value(row, col - 1) in TOP + MIDDLE \
                        and board.get_value(row + 2, col) not in BOTTOM:
                            valid_actions.append((row, col, 'b'))
                        # FIX: THE NEXT LINE MIGHT NEED TO BE REMOVED
                        # (since you can only make a middle if there is already a top)
                        if board.get_value(row - 1, col) in TOP + MIDDLE \
                        and ((row, col) not in board.CORNER_COORDS):
                            valid_actions.append((row, col, 'm'))
        return valid_actions

    def battleship_actions(self, state: BimaruState):
        valid_actions = []
        board: Board = state.get_board()
        # Try to place a horizinatal battleship
        for row in range(board.rows):
            if board.get_row_total(row) <= 3:
                continue
            for col in range(board.cols - 3):
                if board.get_col_total(col) <= 0:
                    continue
                if board.get_value(row, col) is None \
                and board.get_value(row, col + 1) is None \
                and board.get_value(row, col + 2) is None \
                and board.get_value(row, col + 3) is None \
                and (col == 0 or (board.adjacent_vertical_values(row, col - 1) in EMPTY_ADJACENT and \
                board.get_value(row, col - 1) in EMPTY_SPACE)) \
                and (col == board.cols - 4 or (board.adjacent_vertical_values(row, col + 4) in EMPTY_ADJACENT \
                and board.get_value(row, col + 4) in EMPTY_SPACE)) \
                and board.adjacent_vertical_values(row, col) in EMPTY_ADJACENT \
                and board.adjacent_vertical_values(row, col + 1) in EMPTY_ADJACENT \
                and board.adjacent_vertical_values(row, col + 2) in EMPTY_ADJACENT \
                and board.adjacent_vertical_values(row, col + 3) in EMPTY_ADJACENT:
                    valid_actions.append((row, col, 'lmmr'))
        # Try to place a vertical battleship
        for col in range(board.cols):
            if board.get_col_total(col) <= 3:
                continue
            for row in range(board.rows - 3):
                if board.get_row_total(row) <= 0:
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
                    valid_actions.append((row, col, 'tmmb'))
        return valid_actions

    def cruiser_actions(self, state: BimaruState):
        valid_actions = []
        board: Board = state.get_board()
        # Try to place a horizinatal cruiser
        for row in range(board.rows):
            if board.get_row_total(row) <= 2:
                continue
            for col in range(board.cols - 2):
                if board.get_col_total(col) <= 0:
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
                    valid_actions.append((row, col, 'lmr'))
        # Try to place a vertical cruiser
        for col in range(board.cols):
            if board.get_col_total(col) <= 2:
                continue
            for row in range(board.rows - 2):
                if board.get_row_total(row) <= 0:
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
                    valid_actions.append((row, col, 'tmb'))
        return valid_actions
    
    def destroyer_actions(self, state: BimaruState):
        valid_actions = []
        board: Board = state.get_board()
        # Try to place a horizinatal cruiser
        for row in range(board.rows):
            if board.get_row_total(row) <= 1:
                continue
            for col in range(board.cols - 1):
                if board.get_col_total(col) <= 0:
                    continue
                if board.get_value(row, col) is None \
                and board.get_value(row, col + 1) is None \
                and (col == 0 or (board.adjacent_vertical_values(row, col - 1) in EMPTY_ADJACENT \
                and board.get_value(row, col - 1) in EMPTY_SPACE)) \
                and (col == board.cols - 2 or (board.adjacent_vertical_values(row, col + 2) in EMPTY_ADJACENT \
                and board.get_value(row, col + 2) in EMPTY_SPACE)) \
                and board.adjacent_vertical_values(row, col) in EMPTY_ADJACENT \
                and board.adjacent_vertical_values(row, col + 1) in EMPTY_ADJACENT:
                    valid_actions.append((row, col, 'lr'))
        # Try to place a vertical cruiser
        for col in range(board.cols):
            if board.get_col_total(col) <= 1:
                continue
            for row in range(board.rows - 1):
                if board.get_row_total(row) <= 0:
                    continue
                if board.get_value(row, col) is None \
                and board.get_value(row + 1, col) is None \
                and (row == 0 or (board.adjacent_horizontal_values(row - 1, col) in EMPTY_ADJACENT \
                and board.get_value(row - 1, col) in EMPTY_SPACE)) \
                and (row == board.rows - 2 or (board.adjacent_horizontal_values(row + 2, col) in EMPTY_ADJACENT \
                and board.get_value(row + 2, col) in EMPTY_SPACE)) \
                and board.adjacent_horizontal_values(row, col) in EMPTY_ADJACENT \
                and board.adjacent_horizontal_values(row + 1, col) in EMPTY_ADJACENT:
                    valid_actions.append((row, col, 'tb'))
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
                    valid_actions.append((row, col, 'c'))
        return valid_actions


    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        actions = []
        actions += self.battleship_actions(state)
        actions += self.cruiser_actions(state)
        actions += self.destroyer_actions(state)
        actions += self.submarine_actions(state)
        actions += self.brute_force_actions(state)
        return actions


    def result(self, state: BimaruState, action) -> BimaruState:
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        board: Board = state.get_board()
        copy: Board = board.copy_board()
        child_state: BimaruState = BimaruState(copy)
        child_state.num_battleships = state.num_battleships
        child_state.num_cruisers = state.num_cruisers
        child_state.num_destroyers = state.num_destroyers
        child_state.num_submarines = state.num_submarines
        if action not in self.actions(state):
            print("THE STATE'S ACTIONS ARE: " + self.actions(state))
            print("THE ACTION: " + action)
            state.get_board().print_board()
            raise ValueError('Invalid action')
        row = action[0]
        col = action[1]
        move = action[2]

        if move == 'c':
            state.num_submarines -= 1
        elif len(move) == 2:
            state.num_destroyers -= 1
        elif len(move) == 3:
            state.num_cruisers -= 1
        elif len(move) == 4:
            state.num_battleships -= 1
        for x in move:
            copy.set_value(int(row), int(col), str(x))
            copy.lower_total(row, col)
            if move[0] == 'l':
                col += 1
            elif move[0] == 't':
                row += 1
        child_state.get_board().print_board()
        return child_state

            

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        if state is None:
            return False
        board: Board = state.get_board()
        num_battleships = state.num_battleships
        num_cruisers = state.num_cruisers
        num_destroyers = state.num_destroyers
        num_submarines = state.num_submarines
        for row in range(board.rows):
            if board.get_row_total(row) != 0:
                print("ROW TOTAL ERROR") # DEBUG
                return False
            for col in range(board.cols):
                if board.get_col_total(col) != 0:
                    print("COL TOTAL ERROR") # DEBUG
                    return False
                """ THIS IS NOT A GOOD PLACE FOR THIS
                if board.get_value(row, col) is None:
                    board.set_value(row, col, '.') """ # FIX

                if board.get_value(row, col) not in EMPTY_SPACE:
                    if board.get_value(row, col) in ['C', 'c']:
                        num_submarines -= 1

                    # Horizontal tests
                    elif board.get_value(row, col) in ['L', 'l']:
                        if col >= board.cols - 1 or board.get_value(row, col + 1) not in ['M', 'm', 'R', 'r']:
                            print("L ERROR")
                            return False
                        if board.get_value(row, col + 1) in ['M', 'm']:
                            if col >= board.cols - 2 or board.get_value(row, col + 2) not in ['M', 'm', 'R', 'r']:
                                print("L ERROR")
                                return False
                            if board.get_value(row, col + 2) in ['M', 'm']:
                                if col >= board.cols - 3 or board.get_value(row, col + 3) not in ['R', 'r']:
                                    print("L ERROR")
                                    return False
                                if board.get_value(row, col + 3) in ['R', 'r']:
                                    num_battleships -= 1
                            elif board.get_value(row, col + 2) in ['R', 'r']:
                                num_cruisers -= 1
                        elif board.get_value(row, col + 1) in ['R', 'r']:
                            num_destroyers -= 1
                    
                    # Vertical tests
                    elif board.get_value(row, col) in ['T', 't']:
                        if row >= board.rows - 1 or board.get_value(row + 1, col) not in ['M', 'm', 'B', 'b']:
                            print("T ERROR")
                            return False
                        if board.get_value(row + 1, col) in ['M', 'm']:
                            if row >= board.rows - 2 or board.get_value(row + 2, col) not in ['M', 'm', 'B', 'b']:
                                print("T ERROR")
                                return False
                            if board.get_value(row + 2, col) in ['M', 'm']:
                                if row >= board.rows - 3 or board.get_value(row + 3, col) not in ['B', 'b']:
                                    print("T ERROR")
                                    return False
                                if board.get_value(row + 3, col) in ['B', 'b']:
                                    num_battleships -= 1
                            elif board.get_value(row + 2, col) in ['B', 'b']:
                                num_cruisers -= 1
                        elif board.get_value(row + 1, col) in ['B', 'b']:
                            num_destroyers -= 1













                """ elif board.get_value(row, col) not in EMPTY_SPACE:

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
                            print("R ERROR") # DEBUG """

        if num_submarines != 0 or num_destroyers != 0 or \
        num_cruisers != 0 or num_battleships != 0:
            print("NUMBER OF SHIPS ERROR") # DEBUG
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
    
    print(problem.actions(problem.state))

    goal_node: Node = depth_first_tree_search(problem)

    print("Is goal?", problem.goal_test(goal_node.state))
    goal_node.state.get_board().print_board()
