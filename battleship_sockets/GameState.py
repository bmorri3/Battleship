
from collections import defaultdict
import random

class GameState():


	def __init__(self, user1, user2):

		self.user1 = user1
		self.user2 = user2

		self.ships_placement = {}
		self.shots_fired = defaultdict(list)

		self.first_turn_player = ''
		self.current_turn_player = ''

	def place_ships(self, username, ships):
		self.ships_placement[username] = ships
		if self.user1 in self.ships_placement.keys() and self.user2 in self.ships_placement.keys():
			i = random.randint(1,2)
			if i==1:
				self.first_turn_player = self.user1
			else:
				self.first_turn_player = self.user2
			self.current_turn_player = self.first_turn_player

	def add_shot_fired(self, username, shot):
		self.shots_fired[username].append(shot)
		if self.current_turn_player==self.user1:
			self.current_turn_player=self.user2
		else:
			self.current_turn_player=self.user1

	def print_state(self):
		pass
