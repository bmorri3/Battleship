

class ClientState():

	def __init__(self):
		self.reset_state()

	def reset_state(self):

		# For account creation
		self.account_created = False

		# For logging in/out
		self.username = ""
		self.logged_in = False

		self.opponent = ""
		# For opponent (dis)connection
		self.opponent_connected = False

		# For reconnection
		self.user_ships = None
		self.opponent_ships = None
		self.user_shots = None
		self.opponent_shots = None

		# For turn updates
		self.opponent_last_shot = None
		self.game_turn = -1

	def switch_turns(self):
		if self.game_turn==self.username:
			self.game_turn=self.opponent
		else:
			self.game_turn=self.username




#
