#!/usr/bin/env python3

import sys
import os
import socket
from base64 import b64encode
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad


class ClientConnection():

	def __init__(self, host, port):
		self.g = 2
		self.p = 0x00cc81ea8157352a9e9a318aac4e33ffba80fc8da3373fb44895109e4c3ff6cedcc55c02228fccbd551a504feb4346d2aef4
		self.host = host
		self.port = port
		self.sock = None

	def valid_ipv4(self, address):
		try:
			socket.inet_aton(address) # check for valid IPv4 address
		except:
			return False
		return True

	def create_keys(self):
		private_key = int.from_bytes(os.urandom(32),"big")
		public_key = pow(self.g,private_key,self.p)
		str_public_key = str(public_key)
		if (len(str_public_key)<384):
			str_public_key = str_public_key.zfill(384)
		return private_key, str_public_key

	# public key in bytes, private key in int
	def compute_sym_key(self, public_key, private_key):
		public_key_int = int(public_key.decode("utf-8"))
		int_key = pow(public_key_int,private_key,self.p)
		hex_key = hex(int_key)
		byte_key = bytes(hex_key, 'utf-8')
		hash_object = SHA256.new(data=byte_key)
		return hash_object.digest()

	def send_data(self, data):
		if not isinstance(data, bytes):
			data = data.encode("utf-8")
		cipher = AES.new(self.key, AES.MODE_GCM)
		ciphertext, tag = cipher.encrypt_and_digest(pad(data,16))
		packet = cipher.nonce + tag + ciphertext
		packet = len(packet).to_bytes(2, byteorder='big') + packet
		self.sock.sendall(packet)

	def rec_data(self):
		try:
			packet_bytes = self.sock.recv(2)
			if not packet_bytes:
				self.close_connection()
				return packet_bytes
			packet_bytes = int.from_bytes(packet_bytes, "big")
			packet = self.sock.recv(packet_bytes)
			packet_nonce = packet[0:16]
			packet_tag = packet[16:32]
			packet_ciphertext = packet[32:]
			cipher = AES.new(self.key, AES.MODE_GCM, packet_nonce)
			message = unpad(cipher.decrypt_and_verify(packet_ciphertext, packet_tag), 16)
			return message
		except socket.error as e:
			return e

	def secure_connect(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.host, self.port))
		print("Connected to server")

		private_key, public_key = self.create_keys()
		self.sock.sendall(public_key.encode("utf-8"))
		server_public_key = self.sock.recv(384)
		self.key = self.compute_sym_key(server_public_key, private_key)
		print("Established key with server")
		self.sock.setblocking(False)

	def close_connection(self):
		if self.sock:
			self.sock.close()
			self.sock = None

def main():
	c = ClientConnection("127.0.0.1", 9999)
	c.secure_connect()
	c.send_data("Hello")
	m = c.rec_data()

	if isinstance(m, socket.error):
		print("Error")
	elif m==b'':
		print("Connection closed")
	else:
		print(m)

	c.close_connection()

if __name__ == "__main__":
	main()












	#
