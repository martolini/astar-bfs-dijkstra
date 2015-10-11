"""
Run with python astar.py <board filename> <algorithm>
"""

import os
import sys
import time

ANIMATION_STEP_TIME = 0.2
EXPLORED_CELL = 'X'
RETRACED_PATH_CELL = 'O'
OPENED_CELL = '*'


class BaseNode(object):
    board = None
    goal = None
    openset = {}
    closedset = []

    def __init__(self, x, y, parent=None):
        self.x = x
        self.y = y
        self.val = self.board[self.y][self.x]
        self.parent = parent

    def open(self):
        self.openset[self] = self.f_value

    def close(self):
        del self.openset[self]
        self.closedset.append(self)

    @classmethod
    def get_similar(cls, node):
        for elem in cls.openset:
            if elem == node:
                return elem
        for elem in cls.closedset:
            if elem == node:
                return elem
        return None

    @classmethod
    def show_opens(cls):
        for node in cls.openset:
            cls.board[node.y][node.x] = OPENED_CELL

    @property
    def heuristic(self):
        return abs(self.goal.x - self.x) + abs(self.goal.y - self.y)

    @property
    def f_value(self):
        return self.heuristic + self.g_value

    @property
    def move_cost(self):
        raise NotImplementedError("Move cost not implemented")

    @property
    def g_value(self):
        if self.parent is not None:
            return self.move_cost + self.parent.g_value
        return self.move_cost

    def validate_node(self, x, y):
        return 0 <= y < len(self.board) and \
            0 <= x < len(self.board[0])

    @classmethod
    def get_next_node(cls):
        return min(cls.openset, key=cls.openset.get)

    @property
    def children(self):
        output = [(self.x + 1, self.y), (self.x - 1, self.y),
                  (self.x, self.y + 1), (self.x, self.y - 1)]
        for pair in [p for p in output if self.validate_node(*p)]:
            node = self.__class__(*pair, parent=self)
            if not node.is_blocked:
                yield node

    def animate_path(self):
        parent = self.parent
        while parent is not None:
            self.board[parent.y][parent.x] = RETRACED_PATH_CELL
            print_board(self.board)
            time.sleep(ANIMATION_STEP_TIME)
            parent = parent.parent

    def __str__(self):
        return '({}, {})'.format(self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    @property
    def is_blocked(self):
        return self.val == '#'

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return self.x * 100 + self.y


class UnknownCellException(Exception):
    pass


class StandardNode(BaseNode):
    """ Standard A star without movement costs """
    @property
    def move_cost(self):
        return 0


class CellCostNode(BaseNode):
    """ Standard A star with movement cost """
    @property
    def move_cost(self):
        if self.val == 'w':
            return 100
        elif self.val == 'm':
            return 50
        elif self.val == 'f':
            return 10
        elif self.val == 'g':
            return 5
        elif self.val == 'r':
            return 1
        elif self.val in ('A', 'B'):
            return 0
        raise UnknownCellException("Can't handle cell with value {}"
                                   .format(self.val))


class StandardDijkstraNode(BaseNode):
    """ Dijkstra without movement cost """

    @property
    def move_cost(self):
        return 1

    @property
    def f_value(self):
        return self.g_value


class StandardBFSNode(BaseNode):
    """ BFS without movement cost """
    openset = []

    @property
    def move_cost(self):
        return 1

    @classmethod
    def get_next_node(cls):
        return cls.openset[0]

    def open(self):
        self.openset.append(self)

    def close(self):
        self.openset.remove(self)
        self.closedset.append(self)


class CellCostBFSNode(CellCostNode):
    """ BFS with cell cost """
    openset = []

    @classmethod
    def get_next_node(cls):
        return cls.openset[0]

    def open(self):
        self.openset.append(self)

    def close(self):
        self.openset.remove(self)
        self.closedset.append(self)


class CellCostDijkstraNode(CellCostNode):
    """ Dijkstra with cell cost """
    @property
    def f_value(self):
        return self.g_value


def build_board(fname):
    board = []
    with open(fname) as infile:
        for line in infile.readlines():
            row = []
            for c in line.rstrip():
                row.append(c)
            board.append(row)
    return board


def print_board(board):
    os.system('clear')
    for row in board:
        for node in row:
            print node,
        print


def find_node(board, val, Node):
    for y, row in enumerate(board):
        for x, node in enumerate(row):
            if node == val:
                return Node(x, y)
    return -1, -1


def astar(board, Node):
    Node.goal = find_node(board, 'B', Node)
    start = find_node(board, 'A', Node)
    start.open()
    while True:
        print_board(board)
        current = Node.get_next_node()
        if current == Node.goal:
            current.close()
            current.animate_path()
            return
        for child in current.children:
            if child not in Node.closedset:
                if child not in Node.openset:
                    child.open()
                else:
                    other = Node.get_similar(child)
                    if current.g_value + child.move_cost < other.g_value:
                        other.parent = current

        current.close()
        board[current.y][current.x] = EXPLORED_CELL
        time.sleep(ANIMATION_STEP_TIME)


def main(fname, Node):
    board = build_board(fname)
    Node.board = board
    astar(board, Node)
    Node.show_opens()
    print_board(board)


if __name__ == '__main__':
    """
    Based on arguments, decidede what board and algorithm to use
    """
    fname, alg = sys.argv[1:]
    if fname.split('-')[1] == '1':
        if alg == 'dijkstra':
            Node = StandardDijkstraNode
        elif alg == 'bfs':
            Node = StandardBFSNode
        else:
            Node = StandardNode
    elif fname.split('-')[1] == '2':
        if alg == 'bfs':
            Node = CellCostBFSNode
        elif alg == 'astar':
            Node = CellCostNode
        elif alg == 'dijkstra':
            Node = CellCostDijkstraNode
    else:
        raise Exception("Don't recognize board type.")
    main(fname, Node)
