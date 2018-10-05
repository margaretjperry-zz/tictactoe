import requests

from collections import Counter
from flask import Flask
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('board')

def is_valid_board(board):
		board_array = list(board)
		counts = Counter(board_array)

		# Case 1:  the "board" is not 9 characters long
		if len(board_array) != 9:
			return False

		# Case 2:  there are characters in the board that aren't legal
		if not set(counts.keys()).issubset({'x','o',' '}):
			return False

		# Case 3:  There are too many x's or o's for it to be a valid board
		if counts['x'] - counts['o'] > 1 or counts['o'] - counts['x'] >0:
			return False
		return True

def optimal_play(board_array):

	# Not exactly optimal, but this implementation first checks if it's
	# possible for the server to win.  If so, that's the move it makes.
	# Otherwise, it checks if the opponent could win on their next turn.
	# If so, it moves to block the winning square.  If neither player
	# can win on their next turn, the server chooses an empty squre,
	# prioritizing the center, then the corners, and finally the sides.

	corner_indices = [0,2,6,8]
	side_indices = [1,3,5,7]
	opponent_can_win = winning_move(board_array, 'x')
	i_can_win = winning_move(board_array, 'o')

	if i_can_win:
		board_array[i_can_win.pop()] = 'o'
		return ''.join(board_array)
	if opponent_can_win:
		board_array[opponent_can_win.pop()] = 'o'
		return ''.join(board_array)

	if board_array[4] == ' ':
		board_array[4] = 'o'
		return ''.join(board_array)

	for i in corner_indices:
		if board_array[i] == ' ':
			board_array[i] = 'o'
			return ''.join(board_array)

	for i in side_indices:
		if board_array[i] == ' ':
			board_array[i] = 'o'
			return ''.join(board_array)

	# Board is completely filled, so return it as is		
	return ''.join(board_array)

def winning_move(board_array, x_or_o):

	# To find if a winning move is possible, we first find a square
	# that is an 'x' or 'o'.  Then, we check its neighbors to see if 
	# they are also the same value.  If this is true, we find the winning
	# move associated with the 2 indexes and check if the 3rd and final
	# index is empty.  If it's empty, it's a possible winning move and is
	# returned.  Otherwise, an empty set is returned.

	neighbors= { 0: [1,3,4],
				 1: [0,2,4],
				 2: [1,4,5],
				 3: [0,4,6],
				 4: [0,1,2,3,5,6,7,8],
				 5: [2,4,8],
				 6: [3,4,7],
				 7: [6,4,8],
				 8: [7,4,5]}
	winning_ids = [{0,1,2}, {0,3,6}, {0,4,8}, {1,4,7}, {2,5,8}, {2,4,6},{3,4,5},{6,7,8}]
	for id,val in enumerate(board_array):
		if val == x_or_o:
			for i in neighbors[id]:
				if board_array[i] == x_or_o:
					for w_ids in winning_ids:
						if {id, i}.issubset(w_ids) and board_array[w_ids.difference({id,i}).pop()] == ' ':
							return w_ids.difference({id,i})

	return {}

class Game(Resource):

	def get(self):
		args = parser.parse_args(strict=True)
		if is_valid_board(args['board']):
			board_array = list(args['board'])
			return optimal_play(board_array)
		else:
			return 'Not a valid board', 400	

api.add_resource(Game,'/')