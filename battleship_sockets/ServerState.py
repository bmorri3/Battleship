
import os
from hashlib import pbkdf2_hmac

from GameState import GameState

class ServerState():

	def __init__(self):

		self.accounts = {}
		self.logged_in_users = {}
		self.pending_games_list = set()
		self.current_games_opponents = {}
		self.current_games_state = {}


	def add_account(self, username, password):
		if username in self.accounts.keys():
			return False
		else:
			salt = os.urandom(16)
			pw_hash = pbkdf2_hmac('sha256', bytes(password, "utf-8"), salt, 1000).hex()
			self.accounts[username] = (salt, pw_hash)
			return True

	def login(self, sock_data, username, password):
		if username in self.accounts.keys() and username not in self.logged_in_users.keys():
			salt, pw_hash = self.accounts[username]
			pw_attempt_hash = pbkdf2_hmac('sha256', bytes(password, "utf-8"), salt, 1000).hex()
			if pw_attempt_hash==pw_hash:
				self.logged_in_users[username] = sock_data
				return True
			else:
				return False
		elif username in self.logged_in_users.keys() and sock_data.username==username:
			return True
		elif sock_data.username and sock_data.username!=username:
			self.logout(sock_data, sock_data.username)
			return False
		else:
			return False

	def logout(self, sock_data, username):
		if username in self.logged_in_users.keys() and sock_data.username==username:
			del self.logged_in_users[username]
			for user1, user2 in self.pending_games_list:
				if username==user1:
					self.pending_games_list.remove((user1, user2))
			for user1, user2 in self.current_games_opponents.items():
				if user1==username or user2==username:
					del self.current_games_opponents[user1]
			for players, game in self.current_games_state.items():
				if username==players[0] or username==players[1]:
					del self.current_games_state[players]
			return True
		return False

	def connect_with_opponent(self, username, opponent):
		if username not in self.logged_in_users.keys():
			return False
		elif (opponent, username) in self.pending_games_list:
			self.pending_games_list.remove((opponent, username))
			self.current_games_opponents[username] = opponent
			self.current_games_opponents[opponent] = username
			self.current_games_state[(username,opponent)] = GameState(username, opponent)
			return True
		else: #should check that opponent is in accounts; if so, need three diff return values?
			self.pending_games_list.add((username, opponent))
			return False

	def disconnect_with_opponent(self, username, opponent):
		if (username, opponent) in self.pending_games_list:
			self.pending_games_list.remove((username, opponent))
		if username in self.current_games_opponents.keys():
			del self.current_games_opponents[username]
		if opponent in self.current_games_opponents.keys():
			del self.current_games_opponents[opponent]
		if (username, opponent) in self.current_games_state.keys():
			del self.current_games_state[(username,opponent)]
		if (opponent, username) in self.current_games_state.keys():
			del self.current_games_state[(opponent, username)]
		return True

	def reconnect_with_opponent(self, username, opponent):
		return self.get_game_state(username, opponent)

	def user_ship_placement(self, username, ships):
		opponent = self.get_opponent(username)
		if (username, opponent) in self.current_games_state.keys():
			self.current_games_state[(username, opponent)].place_ships(username, ships)
		elif (opponent, username) in self.current_games_state.keys():
			self.current_games_state[(opponent, username)].place_ships(username, ships)
		else:
			return False
		return True

	def user_shot_fired(self, username, shot):
		opponent = self.get_opponent(username)
		if (username, opponent) in self.current_games_state.keys():
			self.current_games_state[(username, opponent)].add_shot_fired(username, shot)
		elif (opponent, username) in self.current_games_state.keys():
			self.current_games_state[(opponent, username)].add_shot_fired(username, shot)
		else:
			return False
		return True

	def get_sock_data(self, username):
		if username in self.logged_in_users.keys():
			return self.logged_in_users[username]
		return None

	def get_opponent(self, username):
		if username in self.current_games_opponents.keys():
			return self.current_games_opponents[username]
		return None

	def get_game_state(self, username, opponent):
		if (username, opponent) in self.current_games_state.keys():
			return self.current_games_state[(username, opponent)]
		elif (opponent, username) in self.current_games_state.keys():
			return self.current_games_state[(opponent, username)]
		return None

	def print_state(self):
		print("\tAccounts:\t", self.accounts)
		print("\tLogged-in Users:", self.logged_in_users)
		print("\tPending Games:", self.pending_games_list)
		print("\tCurrent Opponents:", self.current_games_opponents)
		print("\tCurrent Games: ", self.current_games_state)
		print()

if __name__ == "__main__":
	pass








#
