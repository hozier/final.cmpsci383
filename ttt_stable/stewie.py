import sys
import operator
import copy
import algorithm as a

class Bot:

    # overview: ithin the legal_moves list, assign the value 0 to it.
    def new_dict(self, legal_moves):
        x={}
        for b in legal_moves:
            x[b] = 0
        return x

    def get_move(self, pos, tleft):
        mm = a.Minimax()
        legal_moves = pos.legal_moves()

        # overview: if a list is not returned, return the empty string.
        if not legal_moves:
            return ''

        # overview: create a dictionary named payoff and for each tuples
        payoff = self.new_dict(legal_moves)


        for move in legal_moves:
            # overview: returns a newly built microboard along with the x, y pos
            # of the currently observed next "move"
            # note: the index var is of range (0 to 2), ie (0,2) or (1,1)

            ''' the microboard reflects the current grid (the 3 x 3 board)
                in which the (x, y) position resides.
            '''
            microboard, index = pos.get_microboard(move[0], move[1])
            mm.search_square(legal_moves, payoff, microboard, index, move, pos, self)

            next_pos = mm.is_opponent_playing_in_neighborhood(index, microboard, pos, payoff, move, self)
            next_pos.make_move(move[0], move[1], self.myid)

            mm.observe_next_next_moves(index, next_pos, payoff, move, pos, self)


        return mm.select( pos, payoff, self)
