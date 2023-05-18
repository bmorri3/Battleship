import json
from messagecodes import *
import os
from hashlib import pbkdf2_hmac

from ServerState import ServerState

class ServerMessageProcessor():

	def __init__(self):
		self.state = ServerState()

	def process_message(self, message, sock_data):
		message = json.loads(message.decode("utf-8"))
		switch_code = message['code']
		if switch_code==LOGIN:
			self.login(sock_data, message['username'], message['password'])
		elif switch_code==LOGOUT:
			self.logout(sock_data, message['username'])
		elif switch_code==SIGNUP:
			self.signup(sock_data, message['username'], message['password'])
		elif switch_code==CONNECT_WITH_OPPONENT:
			self.connect_with_opponent(message['username'], message['opponent'])
		elif switch_code==DISCONNECT_WITH_OPPONENT:
			self.disconnect_with_opponent(message['username'], message['opponent'])
		elif switch_code==RECONNECT_WITH_OPPONENT:
			self.reconnect_with_opponent(message['username'], message['opponent'])
		elif switch_code==SHIP_PLACEMENT_UPDATE:
			self.user_ship_placement(message['username'], message['ships'])
		elif switch_code==SHOT_FIRED:
			self.user_shot_fired(message['username'], message['shot'])

	def login(self, sock_data, username, password):
		success = self.state.login(sock_data, username, password)
		message = json.dumps({'code':CONNECTED, 'message':success}).encode('utf-8')
		#SEND USER CONFIRMATION
		if success:
			self.state.get_sock_data(username).outb.append(message)
			sock_data.username=username
		else:
			sock_data.outb.append(message)

	def logout(self, sock_data, username, reply=True):
		success = self.state.logout(sock_data, username)
		#SEND USER CONFIRMATION
		if reply:
			if success:
				sock_data.username=""
			message = json.dumps({'code':DISCONNECTED, 'message':success}).encode('utf-8')
			sock_data.outb.append(message)

	def signup(self, sock_data, username, password):
		success = self.state.add_account(username, password)
		#SEND USER CONFIRMATION
		message = json.dumps({'code':ACCOUNT_CREATED, 'message':success}).encode('utf-8')
		sock_data.outb.append(message)

	def connect_with_opponent(self, username, opponent):
		success = self.state.connect_with_opponent(username, opponent)
		#SEND USER CONFIRMATION
		if success:
			message = json.dumps({'code':OPPONENT_CONNECTED, 'message':success}).encode('utf-8')
			self.state.get_sock_data(username).outb.append(message)
			self.state.get_sock_data(opponent).outb.append(message)

	def disconnect_with_opponent(self, username, opponent):
		success = self.state.disconnect_with_opponent(username, opponent)
		#SEND USER CONFIRMATION
		if success:
			message = json.dumps({'code':OPPONENT_DISCONNECTED, 'message':success}).encode('utf-8')
			self.state.get_sock_data(username).outb.append(message)
			self.state.get_sock_data(opponent).outb.append(message)

	def reconnect_with_opponent(self, username, opponent):
		game_state = self.state.reconnect_with_opponent(username, opponent)
		#SEND USER CONFIRMATION
		if game_state:
			message = json.dumps( { 'code':RECONNECTION,
									'current_turn':game_state.current_turn_player,
									'user_ships':game_state.ships_placement[username],
									'opponent_ships':game_state.ships_placement[opponent],
									'user_shots':game_state.shots_fired[username],
									'opponent_shots':game_state.shots_fired[opponent] } ).encode('utf-8')
			self.state.get_sock_data(username).outb.append(message)

	def user_ship_placement(self, username, ships):
		success = self.state.user_ship_placement(username, ships)
		opponent = self.state.get_opponent(username)
		game_state = self.state.get_game_state(username, opponent)
		turn = game_state.current_turn_player
		#SEND USER CONFIRMATION (also check if game is ready, if so send first player turn->clients will wait on this)
		if success:
			message = json.dumps({'code':OPPONENT_SHIP_PLACEMENT, 'message':ships}).encode('utf-8')
			self.state.get_sock_data(opponent).outb.append(message)
			message = json.dumps({'code':USER_SHIP_PLACEMENT, 'message':ships}).encode('utf-8')
			self.state.get_sock_data(username).outb.append(message)
		if turn:
			message = json.dumps({'code':TURN, 'message':turn}).encode('utf-8')
			self.state.get_sock_data(username).outb.append(message)
			self.state.get_sock_data(opponent).outb.append(message)

	def user_shot_fired(self, username, shot):
		success = self.state.user_shot_fired(username, shot)
		opponent = self.state.get_opponent(username)
		#SEND USER CONFIRMATION
		if success and self.state.get_sock_data(opponent):
			message = json.dumps({'code':SHOTS_FIRED_BY_USER, 'message': shot}).encode('utf-8')
			self.state.get_sock_data(username).outb.append(message)
			message = json.dumps({'code':SHOT_FIRED_BY_OPPONENT, 'message':shot}).encode('utf-8')
			self.state.get_sock_data(opponent).outb.append(message)

	def print_server_state(self):
		self.state.print_state()

if __name__ == "__main__":

	message = json.dumps({'code':42, 'message':(0,0)}).encode('utf-8')
	self.state.get_sock_data(username).outb.append(message)
	print(data)
	print(type(data))











#
