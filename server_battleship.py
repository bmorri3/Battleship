"""
Main file for the battleship program over a server.

python server_battleship.py
"""

import time

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import sys
import random

from my_constants import *
from battleship_game import BattleshipGame
from player import Player
from battleship_sockets.ClientMessenger import ClientMessenger


def get_choice():
    # Get user choice from the opening menu.
    choice = -1

    while choice not in range(1, 5):
        choice = input("\nPlease enter your selection: ")
        if choice.isdigit():
            choice = int(choice)
        else:
            choice = -1
    print()

    return choice


def connect_to_server():
    c1 = ClientMessenger("127.0.0.1", 9999)
    c1.connect()
    print()
    return c1


def change_to_tuple(coord):
    # Detect uppercase and convert from ASCII to 1-10 for A-J or a-j
    # Change capital letters to the numbers 1-26
    if coord[0].isupper():
        first_coord = ord(coord[0]) - 64
    # Change lowercase letters to the numbers 1-26
    else:
        first_coord = ord(coord[0]) - 96

    # If the number part is 1-9
    if len(coord) == 2:
        # Change the integer characters into integers
        second_coord = ord(coord[1]) - 48
        # If the letter is between A and J and the number is between 1 and 9
        if 1 <= first_coord <= 10 and 1 <= second_coord <= 9:
            valid_entry = True
    # Else if the number part is 2 digits
    elif len(coord) == 3:
        # Get the tens digit
        second_coord = ord(coord[1]) - 48
        # Get the ones digit
        third_coord = ord(coord[2]) - 48
        # Combine the second and third entries into the second entry
        second_coord = 10 * second_coord + third_coord

    return first_coord, second_coord


class Battleship:
    """Main class to run Battleship application"""

    def __init__(self):
        # Initialize board size, player count, and an array of size player_count of Players
        self.board_size = BOARD_SIZE
        self.player_count = PLAYER_COUNT

        # Player who has the current turn
        self.current_player = ""
        # For testing
        self.current_player = PLAYER_ONE

        # Create a BattleshipGame object
        self.battleship_game = BattleshipGame()

        # Connect to server
        self.client = connect_to_server()

        # Create an empty player
        self.player = Player("", self.battleship_game)
        # Create an empty opponent
        self.opponent = Player("", self.battleship_game)

    def show_menu(self):
            # Show the menu
            print("You may choose from the following options:")
            print("1. Register Account")
            if not self.client.get_state().logged_in:
                print("2. Log In")
                print()
            else:
                print("2. Log Out")
                print("3. Play Game")
            print("4. Exit")

    def handle_choice(self, choice):
        # Call function according to user choice.
        # Choice 1: Register Account
        # Choice 2: Log in or Log out
        # Choice 3: Play Game (if logged in)
        # Choice 4: Exit
        if choice == 1:
            print("Register Account")
            self.register_account()
        elif choice == 2:
            if not self.client.get_state().logged_in:
                print("Logging In")
                self.login()
            else:
                print("Logging Out")
                self.logout()
        elif choice == 3:
            if self.client.get_state().logged_in:
                print("Welcome to Battleship!")
                self.run_battleship()
            else:
                print("Invalid choice. Choose again.\n")
        elif choice == 4:
            self.exit()

    def get_player(self):
        """
        Getter for Battleship.player

        :return: Battleship.player
        """
        return self.player

    def get_opponent(self):
        """
        Getter for Battleship.opponent

        :return: Battleship.opponent
        """
        return self.opponent

    def get_current_player(self):
        """
        Getter for Battleship.current_player

        :return: Battleship.current_player
        """
        return self.current_player

    def register_account(self):
        print("Please enter your username:")
        username = input()
        print("Please enter your password:")
        password = input()
        # For testing
        # password = PASSWORD

        # Attempt to create the account.
        self.client.create_account(username, password)

        success = False
        start_time = time.time()
        while not success and time.time() < start_time + 5:
            self.client.rec_data()
            success = self.client.get_state().account_created

        if success:
            print("Account created.")
            print("username:", username)
            print("password:", password)
        else:
            print("Account not created. Please try again")

        print()

    def login(self):
        # Logs user into server.
        # TODO: Need to be able to check if username has been registered.
        # TODO: Need to be able to check and see if the username/password combination has logged in already
        print("Please enter your username:")
        username = input()
        print("Please enter your password:")
        password = input()
        # For testing
        # password = PASSWORD

        # Attempt to log in
        self.client.login(username, password)

        # For up to 5 seconds. attempt to log in.
        starting_time = time.time()
        success = False
        while time.time() < starting_time + 5 and not success:
            self.client.rec_data()
            success = self.client.get_state().logged_in

        if success == True:
            # Set user's username
            self.get_player().update_username(username)

            # Verify for the user that they are logged in.
            print(self.get_player().get_username() + " is logged in.\n")
        else:
            print(username + " IS NOT logged in. Please create an account or try again.\n")

    def logout(self):
        # Logs user out of server
        self.client.logout(self.get_player().get_username())

        # Wait for the state to be updated
        while self.client.get_state().logged_in:
            self.client.rec_data()

        # Verify for the user that they are logged out.
        print(self.get_player().get_username() + " is logged out.\n")

    def connect_with_opponent(self):
        # Connect with opponent
        print("Who would you like to play with?")
        opponent_username = input()
        self.client.connect_with_opponent(opponent_username)

        # Check whether opponent is connected.
        self.client.rec_data()

        # TODO: add code to assign player number based on who logged in first

        start_time = time.time()
        # If the opponent has not connected, wait for opponent.
        while not self.client.get_state().opponent_connected and time.time() < start_time + 10:
            self.client.rec_data()

        if self.client.get_state().opponent_connected:
            self.opponent.update_username(opponent_username)
        else:
            self.run_application()

    def get_coord(self):
        valid_entry = False
        while not valid_entry:
            # Obtain coordinates and make sure they are between A1 and J10
            coord = input()

            if coord != "":
                # If quit is chosen, call quit_game()
                if coord == 'q' or coord == 'Q':
                    self.quit_game()

                # Detect uppercase and convert from ASCII to 1-10 for A-J or a-j
                # Change capital letters to the numbers 1-26
                if coord[0].isupper():
                    first_coord = ord(coord[0]) - 64
                # Change lowercase letters to the numbers 1-26
                else:
                    first_coord = ord(coord[0]) - 96

                # If the number part is 1-9
                if len(coord) == 2:
                    # Change the integer characters into integers
                    second_coord = ord(coord[1]) - 48
                    # If the letter is between A and J and the number is between 1 and 9
                    if 1 <= first_coord <= 10 and 1 <= second_coord <= 9:
                        valid_entry = True
                # Else if the number part is 2 digits
                elif len(coord) == 3:
                    # Get the tens digit
                    second_coord = ord(coord[1]) - 48
                    # Get the ones digit
                    third_coord = ord(coord[2]) - 48
                    # Combine the second and third entries into the second entry
                    second_coord = 10 * second_coord + third_coord

                    # If make sure that the two-digit number part is equal to 10
                    if 1 <= first_coord <= 10 and second_coord == 10:
                        valid_entry = True

            if valid_entry is False:
                print("Please enter a valid location.")

        return first_coord, second_coord, coord

    def send_shot(self, shot):
        old_shot = self.client.get_state().user_shots

        self.client.send_shot(shot)
        while old_shot is self.client.get_state().user_shots:
            time.sleep(0.1)
            self.check_for_disconnect()

    def receive_shot(self):
        old_shot = self.client.get_state().opponent_last_shot

        while old_shot is self.client.get_state().opponent_last_shot:
            self.check_for_disconnect()

        return self.client.get_state().opponent_last_shot

    def execute_players_turn(self):
        print("It is your turn.")

        # Show for testing purposes
        print("Opponent ships remaining: ", self.get_opponent().get_ships_remaining())

        print(self.get_opponent().get_user_gameboard())

        self.battleship_game.display_both_heatmaps(self.get_player().get_user_gameboard(), 
                                                   self.get_opponent().get_user_gameboard(), 
                                                   self.get_player().get_username(),
                                                   self.get_opponent().get_username(), end_ind=False)
        shot = INVALID
        while shot is INVALID:
            # Get shot
            print("Where would you like to shoot? (A1 through J10) or (Q)uit")
            first_coord, second_coord, coord = self.get_coord()
            # Fire shot
            shot = self.battleship_game.fire_shot(self.get_opponent(), (first_coord, second_coord))

        self.send_shot(coord)

        return self.get_opponent().get_ships_remaining()

    def execute_opponents_turn(self, shot):
        first_coord, second_coord = change_to_tuple(shot)
        result = self.battleship_game.fire_shot(self.get_player(), (first_coord, second_coord))
        print("After shot:", self.get_player().get_user_gameboard())

    def wait_for_opponent(self):
        print("It is " + self.get_opponent().get_username() + "'s turn.")
        print("Waiting for opponent...")
        self.check_for_disconnect()
        shot_coord = self.receive_shot()
        return shot_coord

    def end_game(self):
        plt.close('all')
        if self.get_player().get_ships_remaining() == 0:
            winner = self.get_opponent().get_username()
        elif self.get_opponent().get_ships_remaining() == 0:
            winner = self.get_player().get_username()
        else:
            winner = "ERROR"

        print(self.get_player().get_username() + "\'s ships remaining: " + str(self.get_player().get_ships_remaining()))
        print(self.get_opponent().get_username() + "\'s ships remaining: " + str(self.get_opponent().get_ships_remaining()))

        self.battleship_game.display_both_heatmaps(self.get_player().get_user_gameboard(), 
                                                   self.get_opponent().get_user_gameboard(), 
                                                   self.get_player().get_username(),
                                                   self.get_opponent().get_username(), end_ind=True)
        
        print(winner, "wins!!!")
        print("Press enter to continue.")
        input()

        self.player = Player(self.get_player().get_username(), self.battleship_game)
        self.client.disconnect_with_opponent(self.get_opponent().get_username())

        self.run_application()

    def place_ships(self):
        # Allows user to place all of their ships.

        print("Place your ships.")
        # Repeat for each ship
        for ship in range(self.battleship_game.num_ships):
            # Initialize ship_placed to false. This will become true is the ship is placed in a valid location.
            ship_placed = False
            # Repeat until the placement is valid.
            while ship_placed is False:
                print("Please enter the top-left coordinates (A1 through J10) of your " + self.battleship_game.ship_names[ship])
                print("or press Q to quit.")
                first_coord, second_coord, coord = self.get_coord()

                direction = ''
                while direction not in ['h', 'H', 'v', 'V', 'q', 'Q']:
                    self.check_for_disconnect()
                    print("Please enter the direction of your boat placement.")
                    print("(H)orizontal or (V)ertical or (Q)uit")
                    direction = input()

                    if not direction.isalpha():
                        direction = ''

                if direction == 'q' or direction == 'Q':
                    self.quit_game()

                self.check_for_disconnect()

                # Check validity of placement
                ship_placed = self.battleship_game.place_single_ship(self.get_player(), ship, direction,
                                                                     (first_coord, second_coord))
                
            self.battleship_game.display_heatmap(self.get_player().get_user_gameboard(), 'Player {} Gameboard'.format(self.get_player().get_username()), 
                            100, 200, 500, 500, type='player', player_username=self.get_player().get_username(),
                            opponent_username=self.get_opponent().get_username())
            
        plt.close('all')

    def check_for_disconnect(self):
        self.client.rec_data()
        if not self.client.get_state().opponent_connected:
            print("Opponent disconnected")
            self.quit_game()

    def send_gameboard(self):
        # Send player's gameboard to opponent

        print("Sending your gameboard.")

        # Get the old board state to compare with new state to verify it was received.
        old_board_state = self.client.get_state().user_ships

        # Make player's gameboard a list and send it.
        l = self.get_player().get_user_gameboard().tolist()  # nested lists with same data, indices
        self.client.send_ship_placement(l)

        # Wait until the server verifies the change.
        while self.client.get_state().user_ships is old_board_state:
            self.check_for_disconnect()

    def get_opponents_gameboard(self):
        print("Waiting for opponent's ships...")

        while not self.client.get_state().opponent_ships:
            self.check_for_disconnect()

        self.current_player = self.client.get_state().game_turn
        while self.current_player == -1:
            self.check_for_disconnect()
            self.current_player = self.client.get_state().game_turn

        # Convert the list to an array and store
        a = np.array(self.client.get_state().opponent_ships)
        self.get_opponent().set_user_gameboard(a)

    def switch_turns(self):
        if self.current_player == self.get_player().get_username():
            self.current_player = self.get_opponent().get_username()
        else:
            self.current_player = self.get_player().get_username()

    def complete_turn(self):
        # If it is player's turn, execute the player's turn, otherwise wait for the opponent

        # For testing, PLAYER_ONE will always go first.
        self.check_for_disconnect()

        current_player = self.client.get_state().game_turn

        if self.current_player == self.get_player().get_username():
            self.execute_players_turn()
        else:
            opponents_shot = self.wait_for_opponent()
            self.execute_opponents_turn(opponents_shot)

        if self.get_opponent().get_ships_remaining() == 0 or self.get_player().get_ships_remaining() == 0:
            return True

        self.switch_turns()
        print()

        return False

    def run_battleship(self):
        # Begins the Battleship game logic

        start_time = time.time()
        success = False
        self.connect_with_opponent()
        self.client.rec_data()
        # Connect with chosen opponent
        while not success and time.time() < start_time + 30:
            self.client.rec_data()
            success = self.client.get_state().opponent_connected
        print("connected=", success)
        print()

        # Player places ships and sends to server
        self.place_ships()
        self.send_gameboard()
        # Wait and get opponent's ships when they are ready.
        self.get_opponents_gameboard()

        someone_won = False
        while someone_won is False:
            # Get gameboards to check when the turn is complete.
            players_old_gameboard = self.get_player().get_user_gameboard().copy()
            opponents_old_gameboard = self.get_opponent().get_user_gameboard().copy()

            # Complete either player's turn or opponent's turn
            someone_won = self.complete_turn()

            # For clarity, get the truth value of whether or not the gameboards have changed
            player_truth = self.get_player().get_user_gameboard() == players_old_gameboard
            opponent_truth = self.get_opponent().get_user_gameboard() == opponents_old_gameboard

            # Wait for both players to finish before ending turn
            while player_truth.all() and opponent_truth.all():
                time.sleep(0.5)
                player_truth = self.get_player().get_user_gameboard().all() == players_old_gameboard.all()
                opponent_truth = self.get_opponent().get_user_gameboard().all() == opponents_old_gameboard.all()

        print()

        self.end_game()

    def quit_game(self):
        print("Quitting game")
        self.player = Player(self.get_player().get_username(), self.battleship_game)
        self.client.disconnect_with_opponent(self.get_opponent().get_username())
        self.run_application()

    def exit(self):
        print("Goodbye!")
        self.client.rec_data()

        if self.client.get_state().opponent != "":
            self.client.disconnect_with_opponent(self.get_opponent().get_username())
        if self.client.get_state().logged_in:
            self.logout()
        self.client.close_connection()
        sys.exit(0)

    def run_application(self):
        # Code to execute the application

        # Initialize choice
        choice = -1
        # Show opening menu, get choice, and handle the choice
        while choice != 4:
            self.show_menu()
            choice = get_choice()
            self.handle_choice(choice)


def start_game():
    # Make a game instance
    battleship = Battleship()

    # Run the application
    battleship.run_application()


if __name__ == '__main__':
    start_game()
