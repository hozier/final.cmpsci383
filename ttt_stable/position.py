import sys


class Position:
    def __init__(self):
        self.board = []
        self.macroboard = []

    def parse_field(self, fstr):
        flist = fstr.replace(';', ',').split(',')
        self.board = [int(f) for f in flist]

    def parse_macroboard(self, mbstr):
        mblist = mbstr.replace(';', ',').split(',')
        self.macroboard = [int(f) for f in mblist]

    def next_legal(self, index, pos, bot):
        # overview: if the position of the macroboard ie [xxxxxxxxx] contain a
        # number greater than 0, it is a WON board.
        if pos.macroboard[3*index[1]+index[0]] > 0:
            # overview: build out a (9x9) full coordinate grid
            # assign it to the variable move.
            moves = [(x, y) for x in range(9) for y in range(9)]

        # overview: is it a drqw game?
        elif pos.is_draw(index[0], index[1]):
            # overview: build out a (9x9) full coordinate grid
            # assign it to the variable move.
            moves = [(x, y) for x in range(9) for y in range(9)]
        else:
            # overview: use the index to build a (3x3) board
            # given the current position.
            microboard = self.next_microboard(index, pos)
            moves = flatten(microboard)

        # overview: check
        # 1) if the board ie [xxxxxx..n] contains any 0's (for position not played), we add the (x,y) coordinate to the list
        # 2) if the macroboard ie [xxxxxxxxx] contains any 0's (for draw) or -1's (for square not won/lost/drawn as yet)
        # 2) if the macroboard contains neither, we add the (x,y) coordinate to the list

        legal_moves = [m for m in moves if self.board[9*m[1] + m[0]] == 0 and self.macroboard[3*(m[1]//3)+m[0]//3] < 1]
        return legal_moves



    def is_legal(self, x, y):
        mbx, mby = x//3, y//3
        return self.macroboard[3*mby+mbx] == -1 and self.board[9*y+x] == 0

    def legal_moves(self):
        return [(x, y) for x in range(9) for y in range(9) if self.is_legal(x, y)]

    # overview: moves the X / O piece through the duration of the game.
    # @pid: the current player's ID (either 1 or 2)
    def make_move(self, x, y, pid):
        # overview: compute integer divison on x and y coordinate.
        mbx, mby = x//3, y//3

        # overview: marks the current player's TURN on the board.
        self.board[9*y+x] = pid

        # overview: marks 0 on the macroboard, means the square is a draw
        if self.is_draw(x, y):
            self.macroboard[3*mby+mbx] = 0

        # overview: marks the current player's ID macroboard,
        # means the square HAS BEEN WON by player PID
        if self.is_winner((x, y), pid):
            self.macroboard[3*mby+mbx] = pid


    def decide_fittest(self, scores, bot):
        for move in scores.keys():
            index = (move[0]/3, move[1]/3)
            macroboard = zip(*[self.macroboard[0:3], self.macroboard[3:6], self.macroboard[6:9]])
            # Setup potential macro win
            opts = list(self.row_col_diag(index, macroboard))
            for opt in opts:
                if bot.myid in opt and bot.oppid not in opt:
                    scores[move] += 1
            # Corner
            if self.is_center(index):
                scores[move] += 0.1
            # Edge
            if self.is_edge(index):
                scores[move] -= 0.1
        return scores


    def get_board(self):
        return ''.join(self.board, ',')

    def get_macroboard(self):
        return ''.join(self.macroboard, ',')

    def get_microboard(self, x, y):

        # overview: divides rows and colums of the 9x9 grid into
        # THREE major subsets
        mini_squares = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        for mini in mini_squares:
            if x in mini:

                # overview: mini is a subset of mini_squares, ie [3, 4, 5] or [0, 1, 2]
                xs = mini

                # overview: returns the position of x within the little mini array
                x_index = mini.index(x)
            if y in mini:
                ys = mini
                y_index = mini.index(y)
        microboard = []

        # overview: xs is a subset of mini_squares, ie [3, 4, 5] or [0, 1, 2]
        # for each element inside the little subset array:
        # create a tuple of that ith element (x) the y subset list.
        for xx in xs:
            microboard.append([(xx, yy) for yy in ys])
        return microboard, (x_index, y_index)

    # overview: returns a generator.
    # generator returns one "option" for a next available move
    def row_col_diag(self, index, microboard):
        # overview: index is a tuple
        # hence, index[0] is equiv to (x), given (x, y)
        indices = [0, 1, 2]
        row = [(x, index[1]) for x in indices if x != index[0]]
        col = [(index[0], y) for y in indices if y != index[1]]
        diag1 = [(x, x) for x in indices]
        diag2 = [(2-x, x) for x in indices]

        opts = [row, col]
        if index in diag1:
            # overview: append to the opts list all values held within the diag1
            # list excluding the tuple named index
            opts.append([i for i in diag1 if i != index])

        if index in diag2:
            # overview: append to the opts list all values held within the diag2
            # list excluding the tuple named index
            opts.append([i for i in diag2 if i != index])

        sys.stderr.write('\nwithin def row_col_diag: observing opts: {0}\n'.format(opts))
        sys.stderr.write('within def row_col_diag: observing initial microboard: {0}\n'.format(microboard))

        # overview: waits, and yields each item out of the expression, one by one
        # instead of returning an entire list
        # note: the FUNCTION RETURNS a generator.
        for opt in opts:
            sys.stderr.write('within def row_col_diag: observing opt: {0}\n'.format(opt))
            for x, y in opt:
                sys.stderr.write('within def row_col_diag: observing for x, y in opt: x={0}, y={1}\n'.format(x, y))
                sys.stderr.write('within def row_col_diag: observing applied microboard[x][y]: {0}\n'.format(microboard[x][y]))
            yield [microboard[x][y] for x, y in opt]

    # overview: observe, record and return a boolean for whether the (3x3) microboard
    # that the game is currently being played in will result in a draw.
    def is_draw(self, x, y):
        microboard, index = self.get_microboard(x, y)

        # overview: flatten the microboard's list of lists into just
        # ONE list of tuples.
        ''' the microboard reflects the current grid (the 3 x 3 board)
            in which the (x, y) position resides.
        '''
        sys.stderr.write('within def is_draw: observing self.board: {0}\n'.format(self.board))
        values = [self.board[9*y+x] for x, y in flatten(microboard)]
        sys.stderr.write('within def is_draw: observing values: {0}\n'.format(values))

        # overview: if all positive values:
        # the (3 x 3) microboard is a draw
        if all(value > 0 for value in values):
            return True
        return False

    def is_center(self, index):
        if index == (1, 1):
            return True
        return False

    def is_edge(self, index):
        if index in [(0, 1), (1, 0), (2, 1), (1, 2)]:
            return True
        return False

    def next_microboard(self, index, pos):
        microboard, _ = pos.get_microboard(index[0]*3, index[1]*3)
        return microboard

    def is_macro_winner(self, move, id):
        if self.is_winner(move, id):
            index = (move[0]/3, move[1]/3)
            macroboard = zip(*[self.macroboard[0:3], self.macroboard[3:6], self.macroboard[6:9]])
            # sys.stderr.write('MACROBOARD: {}\n'.format(macroboard))
            opts = list(self.row_col_diag(index, macroboard))
            # sys.stderr.write('{}\n'.format(opts))
            # sys.stderr.write('\n')
            for opt in opts:
                if all(v == id for v in opt):
                    return True
        return False

    def is_winner(self, move,  pid):
        x = move[0]
        y = move[1]
        microboard, index = self.get_microboard(x, y)
        opts = list(self.row_col_diag(index, microboard))
        opts = [[self.board[9*y+x] for x, y in opt] for opt in opts]
        for opt in opts:
            if all(v == pid for v in opt):
                return True
        return False



def flatten(l):
    return [item for sublist in l for item in sublist]
