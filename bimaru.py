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


class BimaruState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = BimaruState.state_id
        BimaruState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    # TODO: outros metodos da classe


class Board:
    """Representação interna de um tabuleiro de Bimaru."""

    def __init__(self, rows: int, cols: int):
        """Construtor: recebe o número de linhas e colunas do tabuleiro."""
        self.rows = rows
        self.cols = cols
        self.board = [[None for _ in range(cols + 1)] for _ in range(rows + 1)] # +1 para guardar os valores totais da linha e coluna

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return None
        return self.board[row][col]
    
    def get_row_total(self, row: int) -> str:
        """Devolve o valor total da linha."""
        return self.board[row][self.cols]
    
    def get_col_total(self, col: int) -> str:
        """Devolve o valor total da coluna."""
        return self.board[self.rows][col]
    
    def set_value(self, row: int, col: int, value: str):
        """Altera o valor na respetiva posição do tabuleiro."""
        self.board[row][col] = value

    def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""
        return (self.get_value(row - 1, col), self.get_value(row + 1, col))

    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""
        return (self.get_value(row, col - 1), self.get_value(row, col + 1))

    @staticmethod
    def parse_instance(standard_input):
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.

        Por exemplo:
            $ python3 bimaru.py < input_T01

            > from sys import stdin
            > line = stdin.readline().split()
        """
        rows = standard_input.readline().split()[1:]
        cols = standard_input.readline().split()[1:]
        n_rows = len(rows)
        n_cols = len(cols)
        board = Board(n_rows, n_cols)

        for row in range(n_rows):
            board.set_value(row, n_cols, rows[row])
        for col in range(n_cols):
            board.set_value(n_rows, col, cols[col])

        n_hints = eval(standard_input.readline())
        for _ in range(n_hints):
            hint = standard_input.readline().split()[1:]
            board.set_value(int(hint[0]), int(hint[1]), hint[2])

        return board

    def print_board(self):
        """Imprime o tabuleiro no standard output (stdout)."""
        for row in range(self.rows):
            for col in range(self.cols):
                if board.get_value(row, col) is None:
                    print('.', end='')
                else:
                    print(board.get_value(row, col), end='')
            print()



class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        # TODO
        pass

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        # TODO
        pass

    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        # TODO
        pass

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        # TODO
        pass

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass

    # TODO: outros metodos da classe


if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro do standard input,
    board = Board.parse_instance(sys.stdin)
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
    board.print_board()
