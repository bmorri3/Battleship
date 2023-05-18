from battleship_sockets.ClientConnection import ClientConnection
from battleship_sockets.ClientState import ClientState
from battleship_sockets.messagecodes import *
import json
import time
import socket

class ClientMessenger():

	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.connection = ClientConnection(host, port)
		self.state = ClientState()

	def get_state(self):
		return self.state

	def create_account(self, username, password):
		if self.connection.sock:
			data = json.dumps({'code':SIGNUP,'username':username,'password':password})
			self.connection.send_data(data)

	def login(self, username, password):
		if self.connection.sock:
			self.state.username = username
			data = json.dumps({'code':LOGIN,'username':username,'password':password})
			self.connection.send_data(data)

	def logout(self, username):
		data = json.dumps({'code':LOGOUT,'username':username})
		self.connection.send_data(data)

	def connect_with_opponent(self, opponent):
		data = json.dumps({'code':CONNECT_WITH_OPPONENT,'username':self.state.username,'opponent':opponent})
		self.connection.send_data(data)
		self.state.opponent = opponent

	def disconnect_with_opponent(self, opponent):
		data = json.dumps({'code':DISCONNECT_WITH_OPPONENT,'username':self.state.username,'opponent':opponent})
		self.connection.send_data(data)
		self.state.opponent = ""

	def send_ship_placement(self, ships):
		data = json.dumps({'code':SHIP_PLACEMENT_UPDATE,'username':self.state.username,'ships':ships})
		self.connection.send_data(data)

	def send_shot(self, shot):
		data = json.dumps({'code':SHOT_FIRED,'username':self.state.username,'shot':shot})
		self.connection.send_data(data)
		self.state.switch_turns()

	def reconnect(self, opponent):
		data = json.dumps({'code':RECONNECT_WITH_OPPONENT,'username':self.state.username,'opponent':opponent})
		self.connection.send_data(data)

	def rec_data(self):
		data = self.connection.rec_data()

		if isinstance(data, socket.error):
			pass
		elif data==b'':
			self.close_connection()
		else:
			data = json.loads(data.decode("utf-8"))

			switch_code = data['code']
			if switch_code==CONNECTED:
				self.state.logged_in = data['message']
			elif switch_code==DISCONNECTED:
				if data['message']:
					self.state.reset_state()
			elif switch_code==ACCOUNT_CREATED:
				self.state.account_created = data['message']
			elif switch_code==OPPONENT_CONNECTED:
				if data['message']:
					self.state.opponent_connected = True
			elif switch_code==OPPONENT_DISCONNECTED:
				if data['message']:
					self.state.opponent_connected = False
			elif switch_code==USER_SHIP_PLACEMENT:
				self.state.user_ships = data['message']
			elif switch_code==OPPONENT_SHIP_PLACEMENT:
				self.state.opponent_ships = data['message']
			elif switch_code==SHOTS_FIRED_BY_USER:
				self.state.user_shots = data['message']
			elif switch_code==SHOTS_FIRED_BY_OPPONENT:
				self.state.opponent_shots = data['message']
			elif switch_code==SHOT_FIRED_BY_OPPONENT:
				self.state.opponent_last_shot = data['message']
				self.state.switch_turns()
			elif switch_code==TURN:
				self.state.game_turn = data['message']
			elif switch_code==RECONNECTION:
				self.state.game_turn = data['current_turn']
				self.state.user_ships = data['user_ships']
				self.state.opponent_ships = data['opponent_ships']
				self.state.user_shots = data['user_shots']
				self.state.opponent_shots = data['opponent_shots']

			return True
		return False

	def connect(self):
		if self.connection.sock:
			self.close_connection()
		self.connection.secure_connect()

	def close_connection(self):
		self.connection.close_connection()


if __name__ == '__main__':

	try:
		c = ClientMessenger("127.0.0.1", 9999)
		c.connect()

		# Test account creation
		sleep_seconds = 1
		username = input("Username: ")
		password = input("Password: ")
		opponent = input("Opponent: ")
		opponent_disconnect = input("Opponent disconnect: ")

		print("\nNew account test")
		c.create_account(username, password)
		time.sleep(sleep_seconds)
		c.rec_data()
		print("Expected: True\n  Actual:", c.state.account_created)

		print("\nExisting account test")
		c.create_account(username, password)
		time.sleep(sleep_seconds)
		c.rec_data()
		print("Expected: False\n  Actual:", c.state.account_created)

		# Test login

		print("\nIncorrect credentials login test (wrong username)")
		c.login(username+"r", password)
		time.sleep(sleep_seconds)
		c.rec_data()
		print("Expected: False\n  Actual:", c.state.logged_in)

		print("\nIncorrect credentials login test (wrong password)")
		c.login(username, password+"a")
		time.sleep(sleep_seconds)
		c.rec_data()
		print("Expected: False\n  Actual:", c.state.logged_in)

		print("\nCorrect credentials login test")
		c.login(username, password)
		time.sleep(sleep_seconds)
		c.rec_data()
		print("Expected: True\n  Actual:", c.state.logged_in)

		print("\nDuplicate login test (user already logged in and tries to log in as same user)")
		c.login(username, password)
		time.sleep(sleep_seconds)
		c.rec_data()
		print("Expected: True\n  Actual:", c.state.logged_in)

		print("\nIncorrect login test (user already logged in and tries to log in as diff user)")
		c.login(username+"123", password)
		time.sleep(sleep_seconds)
		c.rec_data()
		print("Expected: False\n  Actual:", c.state.logged_in)

		print("\nCorrect credentials login test")
		c.login(username, password)
		time.sleep(sleep_seconds)
		c.rec_data()
		print("Expected: True\n  Actual:", c.state.logged_in)

		# Test logout

		print("\nIncorrect credentials logout test (wrong username)")
		c.logout(username+"r")
		time.sleep(sleep_seconds)
		c.rec_data()
		print("Expected: True\n  Actual:", c.state.logged_in)

		print("\nCorrect credentials logout test")
		c.logout(username)
		time.sleep(sleep_seconds)
		c.rec_data()
		print("Expected: False\n  Actual:", c.state.logged_in)

		# Login for state

		print("\nREDO: Correct credentials login test")
		c.login(username, password)
		time.sleep(sleep_seconds)
		c.rec_data()
		print("Expected: True\n  Actual:", c.state.logged_in)

		# Test opponent connection

		print("\nConnect with opponent")
		c.connect_with_opponent(opponent)
		time.sleep(sleep_seconds)
		c.rec_data()
		print("Expected: False\n  Actual:", c.state.opponent_connected)

		while not c.state.opponent_connected:
			c.rec_data()
			time.sleep(sleep_seconds)

		# Test opponent disconnection
		print("\nOpponent connection: ", c.state.opponent_connected)

		if opponent_disconnect=="y":
			print("\nDisconnect with opponent")
			c.disconnect_with_opponent(opponent)
			time.sleep(sleep_seconds)
			c.rec_data()
			print("Expected: False\n  Actual:", c.state.opponent_connected)
		elif opponent_disconnect=="n":
			print("\nWaiting for disconnect with opponent")
			time.sleep(sleep_seconds)
			c.rec_data()
			print("Expected: False\n  Actual:", c.state.opponent_connected)


		# Opponent connection for state

		print("\nREDO: Connect with opponent")
		c.connect_with_opponent(opponent)
		time.sleep(sleep_seconds)
		c.rec_data()
		print("Expected: False\n  Actual:", c.state.opponent_connected)

		while not c.state.opponent_connected:
			c.rec_data()
			time.sleep(sleep_seconds)

		print("\nOpponent connection: ", c.state.opponent_connected)

		# Test ship placement
		print("\nSend ship placement")
		ships = username + " ships"
		c.send_ship_placement(ships)
		while not c.state.game_turn in [1,2]:
			c.rec_data()
			time.sleep(sleep_seconds)

		print("\nOpponent ships: ", c.state.opponent_ships)
		print("\nTurn: ", c.state.game_turn, "int?", type(c.state.game_turn))


		# Test shots
		i=0
		while i!=10:
			while int(username)!=c.state.game_turn:
				c.rec_data()
				time.sleep(sleep_seconds)
			print("Last opponent shot: ", c.state.opponent_last_shot)
			c.send_shot((username,i))
			i+=1


		# c.reconnect(opponent)

		print()

	finally:
		c.close_connection()














	#
