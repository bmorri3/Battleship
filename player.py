"""
Definition of Player object. Defines attributes, constructor, and setters/getters.
"""

__author__ = "Thomas Henderson, Kris London, Ben Morris, Patrick Schaefer"

import numpy as np

from my_constants import *


class Player:
    def __init__(self, username, battleship_game):
        """
        Constructor for Player

        :param username: Player's user_id
        :param battleship_game: Instance of BattleshipGame in order to access battleship_game.num_ships
                                and num_ship_hits
        """
        # Player's username
        self.username = username
        # Player number in the game (1 for Player 1, 2 for Player 2)
        self.my_number = -1

        # Player's gameboard to be stored using a 10x10 matrix.
        # 0 = open water
        # 1 = missed shot
        self.user_gameboard = np.zeros((BOARD_SIZE, BOARD_SIZE))
        self.ships_remaining = battleship_game.get_num_ships()
        self.hits_remaining = battleship_game.get_num_ship_hits().copy()

    def get_my_number(self):
        """
        Getter for Player's player number

        :return: Player.my_number
        """
        return self.my_number

    def set_my_number(self, player_number):
        """
        Setter for Player's player number

        param player_number: Player's number (1 or 2)
        """
        self.my_number = player_number

    def get_ships_remaining(self):
        """
        Getter for Player's ships_remaining

        :return: Player.ships_remaining
        """
        return self.ships_remaining

    def decrease_ships_remaining(self):
        """ Decrement Player's ships_remaining when a ship is sunk. """
        self.ships_remaining -= 1

    def get_hits_remaining(self):
        """
        Getter for Player's hits_remaining

        :return: Player.hits_remaining
        """
        return self.hits_remaining

    def decrease_hits_remaining(self, ship_idx):
        """
        Decrement Player's hits_remaining for a specific ship

        param ship_idx: the index of the ship whose hits_remaining need to be decremented
        """
        self.hits_remaining[ship_idx] -= 1

    def get_user_gameboard(self):
        """
        Getter for Player's user_gameboard

        :return: Player.user_gameboard
        """
        return self.user_gameboard

    def set_user_gameboard(self, gameboard):
        """
        Setter for Player's gameboard

        param gameboard: the new gameboard for Player
        """
        self.user_gameboard = gameboard

    def get_username(self):
        """
        Getter for Player's user_id

        :return: Player.user_id
        """
        return self.username

    def update_username(self, new_username):
        """
        Setter for Player's user_id

        param new_user_id: New user_id for Player
        """
        self.username = new_username