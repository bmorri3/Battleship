import sys
import os
import socket
import selectors
import types
import time
import json
from base64 import b64encode
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad

from messagecodes import *
from ServerMessageProcessor import ServerMessageProcessor


class Server():

	def __init__(self):
		self.listen_ip_address = "127.0.0.1"
		self.port = 9999
		self.message_processor = ServerMessageProcessor()
		self.sel = selectors.DefaultSelector()
		self.g = 2
		self.p = 0x00cc81ea8157352a9e9a318aac4e33ffba80fc8da3373fb44895109e4c3ff6cedcc55c02228fccbd551a504feb4346d2aef4

	def valid_ipv4(self, address):
		try:
			socket.inet_aton(address) # check for valid IPv4 address
		except:
			return False
		return True

	def accept_connection(self, sock):
		conn, addr = sock.accept()  # Should be ready to read
		print(f"Accepted connection from {addr}")
		conn.setblocking(False)
		private_key, public_key = self.create_keys()
		data = types.SimpleNamespace(
			public_key=public_key,
			private_key=private_key,
			sym_key="",
			public_key_sent=False,
			addr=addr,
			inb=[],
			outb=[],
			username=""
		)
		events = selectors.EVENT_READ | selectors.EVENT_WRITE
		self.sel.register(conn, events, data=data)

	def create_keys(self):
		private_key = int.from_bytes(os.urandom(32),"big")
		public_key = pow(self.g,private_key,self.p)
		str_public_key = str(public_key)
		if (len(str_public_key)<384):
			str_public_key = str_public_key.zfill(384)
		return private_key, str_public_key

	# public key in bytes, private key in int
	def compute_sym_key(self, public_key,private_key):
		public_key_int = int(public_key.decode("utf-8"))
		int_key = pow(public_key_int,private_key,self.p)
		hex_key = hex(int_key)
		byte_key = bytes(hex_key, 'utf-8')
		hash_object = SHA256.new(data=byte_key)
		return hash_object.digest()

	def service_connection(self, key, mask):
		sock = key.fileobj
		data = key.data
		if mask & selectors.EVENT_WRITE:
			if data.sym_key and data.public_key_sent:
				if data.outb:
					# send encrypted data
					cipher = AES.new(data.sym_key, AES.MODE_GCM)
					ciphertext, tag = cipher.encrypt_and_digest(pad(data.outb.pop(0),16))
					packet = cipher.nonce + tag + ciphertext
					packet = len(packet).to_bytes(2, byteorder='big') + packet
					sock.sendall(packet)
			if not data.public_key_sent:
				sock.sendall(data.public_key.encode("utf-8"))
				data.public_key_sent = True
		if mask & selectors.EVENT_READ:
			if data.sym_key:
				try:
					packet_bytes = int.from_bytes(sock.recv(2), "big")
					packet = sock.recv(packet_bytes)
					if not packet:
						print(f"1. Closing connection to {data.addr}")
						self.message_processor.logout(data, data.username, reply=False)
						self.sel.unregister(sock)
						sock.close()
						self.message_processor.print_server_state()
					else:
						packet_nonce = packet[0:16]
						packet_tag = packet[16:32]
						packet_ciphertext = packet[32:]
						cipher = AES.new(data.sym_key, AES.MODE_GCM, packet_nonce)
						try:
							message = unpad(cipher.decrypt_and_verify(packet_ciphertext, packet_tag), 16) # message in bytes
							self.message_processor.process_message(message, data)
							self.message_processor.print_server_state()
						except (ValueError):
							sys.stderr.buffer.write("Error: integrity check failed.")
				except ConnectionResetError as e:
					print(f"2. Closing connection to {data.addr}")
					self.message_processor.logout(data, data.username, reply=False)
					self.sel.unregister(sock)
					sock.close()
					self.message_processor.print_server_state()
			else:
				public_key = sock.recv(384)
				if public_key:
					data.sym_key = self.compute_sym_key(public_key, data.private_key)
				else:
					self.sel.unregister(sock)
					sock.close()

	def start_server(self):
		server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_sock.bind((self.listen_ip_address, self.port))
		server_sock.listen()
		print(f"Server listening on {(self.listen_ip_address, self.port)}")
		server_sock.setblocking(False)
		self.sel.register(server_sock, selectors.EVENT_READ, data=None)

		# manage connections
		try:
			while True:
				events = self.sel.select(timeout=None)
				for key, mask in events:
					if key.data is None:
						self.accept_connection(key.fileobj)
					else:
						self.service_connection(key, mask)
		finally:
			events = self.sel.select(timeout=-1)
			for key, mask in events:
				key.fileobj.close()
			self.sel.close()



if __name__ == "__main__":
	s = Server()
	s.start_server()







#
