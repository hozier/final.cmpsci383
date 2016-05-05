import sys
import operator
import copy

class Minimax:



    '''overview: peek at ALL the computed tuples which are defined as "next legal moves"
       foreach each tuple, send its x,y coordinates in and
       build a microboard from it, ie:
       *the 1st out of 9 microboards*
       [(0,0), (0, 1), (0, 2)
        (1,0), (1, 1), (1, 2)
        (2,0), (2, 1), (2, 2)
       ]
    '''
    def search_square(self, legal_moves, payoff, microboard, index, move, pos, bot):

        # overview: crop the search space down to a 3x3
        # observe only the legal moves
        legal_microboard = [m for m in legal_moves if m in self.flatten(microboard)]

        # Block opponent
        # overview: check whether our OPPONENT's next move is a winning move.
        # if so, let's look at the immediate 3x3 board an find where we can block.
        if pos.is_winner(move, bot.oppid):

            # overview: search the current 3x3 for at least one position
            # that is diagonal, antidiagonal, vertical or horizantal
            # which can prevent the opponent winning
            if not any(pos.is_winner(m, bot.oppid) for m in legal_microboard if m != move):
                payoff[move] += 3

        # Win microboard
        if pos.is_winner(move, bot.myid):
            payoff[move] += 10

        # Win Game
        if pos.is_macro_winner(move, bot.myid):
            payoff[move] += 100000000000

        # overview: add to the current payoff value if the index returned from calling get_microboard()
        # is the center ie (1,1)
        # the next best move after this turn is a CORNER move
        if pos.is_center(index):
            payoff[move] += 0.5

        # Edge
        if pos.is_edge(index):
            payoff[move] -= 0.5


    ''' overview: returns a dictionary with the highest score mapped to an (x,y)
        if there exists multiple (x,y) keys with the highest score,
        include them within the dictionary and RETURN.
    '''
    def max_items(self, d):
        ''' overview: items() returns a list of key/value tuples.
            so, if the score value of the tuple is equal to the max_score
            append the key/value pair to the dictionary and finally return.
        '''
        # ie: scores[(0,3)] += 3
        # key=(0,3), value=6
        max_val = max(d.values())
        return {k: v for k, v in d.items() if v == max_val}

    def flatten(self, l):
        return [item for sublist in l for item in sublist]



    # overview: checks whether opponent is playing nearby the current "move"
    # and the current row / col / diag
    def is_opponent_playing_in_neighborhood(self, index, microboard, pos, payoff, move, bot):
        # features.
        # overview: check the current 3x3 grid for a possible win
        # check the antidiagonal / diagonals / rows and columns.
        # return a list
        opts = list(pos.row_col_diag(index, microboard))

        # overview: foreach array of tuples:
        # iterate through each tuple:
        # and use the current tuples x, y coordinates
        # to find its literal position on the board data structure
        # by applying the expression 9 * (x + y)
        # returns a list of board positions

        '''look at a subset of state space,
           for each observed position, if there exists
           a position within the subset that is currently near the "move"  being
           explored from the legal_moves list
           increase the score of that "move by" X amount
           of points.

        '''
        opts_new = []
        for opt in opts:
            some_list = []
            for x, y in opt:
                sys.stderr.write('within def get_move: observing pos.board[9*y+x] for opt: x={0}, y={1}, {2}\n'.format(x, y, pos.board[9*y+x]))
                some_list.append(pos.board[9*y+x])
            opts_new.append(some_list)

        # returns a list of 0 / 1 / 2 for the player's ID playing nearby in square.
        opts = opts_new
        for opt in opts:
            if bot.myid in opt and bot.oppid not in opt:
                payoff[move] += 1.1

        return copy.deepcopy(pos)


    def optimize_heuristics(self, best_payoff, pos, bot):
        best_payoff = pos.decide_fittest(best_payoff, bot)
        return max(best_payoff.items(), key=operator.itemgetter(1))[0]


    def select(self, pos, payoff, bot):
        sys.stderr.write('payoff:\n')
        for value in payoff.items():
            sys.stderr.write('{}\n'.format(value))
        sys.stderr.write('\n')
        best_payoff = self.max_items(payoff)

        # overview: find the best option when multiple good moves are equal
        return self.optimize_heuristics(best_payoff, pos, bot)


    def observe_next_next_moves(self, index, next_pos, payoff, move, pos, bot):
        '''
        Part 2:
        Now after making our current move,
        we check our NEXT available legal move.

        '''
        next_legal_moves = pos.next_legal(index, next_pos, bot)
        can_block = False
        '''
        Adjust weights/heuristics on next (x,y) moves accordingly
        Finally, select
        '''
        for next_move in next_legal_moves:
            ''' can the opponent win? adjust.'''
            if pos.is_winner(next_move, bot.oppid):
                payoff[move] -= 10

            if pos.is_macro_winner(next_move, bot.oppid):
                payoff[move] -= 10000

            ''' can the out player win? adjust.'''
            if pos.is_winner(next_move, bot.myid) and not can_block:
                can_block = True
                payoff[move] -= 2
            if pos.is_macro_winner(next_move, bot.myid):
                payoff[move] -= 12
