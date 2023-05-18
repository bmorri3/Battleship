"""
Main file for the battleship program.

python terminal_battleship.py
"""

# Working on 4/2/23
# TODO: Todos are not up to date
# TODO: Label heatmaps with titles (players and opponents)
# TODO: customize the different cell_ids of the heatmap (misses, hits, and boats always the same color instead of changing as hits happen)
# TODO: display a heatmap without opponent's boats during actual gameplay
# TODO: show heatmaps WITH boats at end of the game
# TODO: show both heatmaps at the beginning of every turn? Yes. Need to see where you are hit and status of your shots on opponents board

import time

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

from my_constants import *
from battleship_game import BattleshipGame
from player import Player
from battleship_sockets.ClientMessenger import ClientMessenger


def show_menu():
    # Show the opening menu
    print("You may choose from the following options:\n")
    print("1. Play Game")
    print("2. Top Scores")
    print("3. Settings")


class Battleship:
    """Main class to run Battleship application"""

    def __init__(self):
        # Initialize board size, player count, and an array of size player_count of Players
        self.board_size = BOARD_SIZE
        self.player_count = PLAYER_COUNT
        self.current_player = -1

        # Create a BattleshipGame object
        self.battleship_game = BattleshipGame()

        # Create an empty array of size player_count of Players
        self.player_array = np.empty(self.player_count, dtype=Player)

        # Fill the array with Player stubs
        for player in range(self.player_count):
            # Create a Player instance
            self.player_array[player] = Player(str(player), self.battleship_game)

    def get_player(self, idx):
        return self.player_array[idx]

    def run_application(self):
        # Code to execute the application

        # Show opening menu, get choice, and handle the choice
        show_menu()
        choice = self.get_choice()
        self.handle_choice(choice)

    def get_usernames(self, player_number):
        # This will be replaced with the user sign-in later.
        # For now, user will input their name.

        # To make testing faster
        username = "Player " + str(player_number + 1)

        """while self.player_array[player_number].username is "":
            print("Player " + str(player_number) + ", what is your user id? ")
            # Might have to assign input() to a variable and then update
            self.player_array[player_number].update_user_id(input())"""

        return username

    def get_choice(self):
        # Get user choice from the opening menu.
        choice = -1

        # To make testing faster
        choice = 1

        """while choice not in range(1,4):
            choice = int(input("\nPlease enter your selection: "))"""

        return choice

    def handle_choice(self, choice):
        # Call function according to user choice
        if choice == 1:
            self.play_game()
        elif choice == 2:
            print("You chose \"Top Scores\".")
        elif choice == 3:
            print("You chose \"Settings\".")

    def show_gameboards(self):
        # Would need to change for more than two players
        plt.rcParams["figure.figsize"] = [7.50, 3.50]
        plt.rcParams["figure.autolayout"] = True

        df1 = pd.DataFrame(np.random.rand(10, 10))
        df2 = pd.DataFrame(np.random.rand(10, 10))

        fig, (ax1, ax2) = plt.subplots(ncols=2)
        fig.subplots_adjust(wspace=0.01)

        ax2.yaxis.tick_right()

        sns.heatmap(self.player_array[0].user_gameboard, cmap="coolwarm",
                    ax=ax1, cbar=False)
        sns.heatmap(self.player_array[1].user_gameboard, cmap="coolwarm",
                    ax=ax2, cbar=False)

        fig.subplots_adjust(wspace=0.001)
        plt.ion()
        plt.show(block=False)

    def show_preround_gameboard(self, player_gameboard, opponent_gameboard):

        return

    def create_masked_heatmap(self, gameboard):
        gameboard_masked = gameboard
        gameboard_masked[gameboard_masked > 2] = 0

        return gameboard_masked

    def get_coord(self):
        valid_entry = False
        while not valid_entry:
            # Obtain coordinates and make sure they are between A1 and J10
            coord = input()

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
                print("Please enter a valid shot location.")

        return first_coord, second_coord

    def execute_players_turn(self):
        if self.current_player == 0:
            player_idx = 0
            opponent_idx = 1
        else:
            player_idx = 1
            opponent_idx = 0

        player = self.get_player(player_idx)
        opponent = self.get_player(opponent_idx)

        # Show for testing purposes
        print("\n\nPlayer " + str(player_idx + 1) + "\'s turn")
        print("Ships left: ", opponent.get_ships_remaining())

        player_no = str(player_idx + 1)
        # TODO: Needs to show both heatmaps at the same time. Also needs to allow for user input and refresh
        # automatically, if possible
        self.battleship_game.display_both_heatmaps(player.user_gameboard, opponent.user_gameboard, player_no)
        print("Player", str(player_idx + 1), "ships remaining: ", player.get_ships_remaining())
        print("Player", str(opponent_idx + 1), "ships remaining: ", opponent.get_ships_remaining())
        
        print("player_gameboard", player.user_gameboard)
        print("opponent_gameboard", opponent.user_gameboard)

        shot = INVALID
        while shot is INVALID:
            # Get shot
            print("Where would you like to shoot? (A1 through J10)")
            first_coord, second_coord = self.get_coord()
            # Fire shot
            # TODO: put this in a while(shot is not valid)
            shot = self.battleship_game.fire_shot(opponent, (first_coord, second_coord))

        return opponent.get_ships_remaining()

    def play_game(self):
        # Runs the Battleship game with the random ship positions for now
        print("You chose \"Play Game\".\n")

        # Get userIDs and Player gameboards
        # This needs to just do one player, based on Player.my_number
        for player in range(self.player_count):
            self.player_array[player].update_username(self.get_usernames(player))
            self.player_array[player].user_gameboard = self.battleship_game.player_gameboards.get('p{player}_gameboard'.format(player=player))

        for player_idx in range(self.player_count):
            # TODO: Move this to its own function: get_user_ships(player_idx) or something
            player = self.player_array[player_idx]
            player.update_username(self.get_usernames(player_idx))
            for ship in range(self.battleship_game.num_ships):
                # Initialize ship_placed to false. This will become true is the ship is placed in a valid location.
                ship_placed = False
                print("placing user ships")
                while ship_placed is False:
                    print("Please enter the top-left coordinates of your " + self.battleship_game.ship_names[ship] + ".")
                    first_coord, second_coord = self.get_coord()

                    direction = ''
                    while direction not in ['h', 'H', 'v', 'V']:
                        print("Please enter the direction of your boat placement.")
                        print("(H)orizontal or (V)ertical")
                        direction = input()

                    # Check validity of placement
                    ship_placed = self.battleship_game.place_single_ship(player, ship, direction, (first_coord, second_coord))

        """# All ships have been placed at this point. Send an affirmative message to the server.
        # TODO: Not working, also, this needs to be implemented for individual users
        old_state = self.c1.get_state().user_ships
        self.c1.send_ship_placement("Placed")
        while self.c1.get_state().user_ships != "Placed":
            print("user_ships:", self.c1.get_state().user_ships())
            self.c1.rec_data()"""

        # Get shots until user quits for now
        # TODO: Maybe change someone_won to winner = 0 and later set it to player number
        # TODO: put this in its own function: execute_shot()
        someone_won = False

        while someone_won is False:
            print("current_player", self.current_player)
            opponent_ships_remaining = self.execute_players_turn()

            # If no ships remain, someone won
            # TODO: Maybe set this to a new function like get_ships_remaining(player_num)
            if opponent_ships_remaining == 0:
                someone_won = True
                winning_player = player_idx

            # Change current_player
            if self.current_player == 0:
                self.current_player = 1
            else:
                self.current_player = 0

        # TODO: Need to define variable: opponent
        #self.battleship_game.display_both_heatmaps(player.user_gameboard, opponent.user_gameboard)

        # Make an end_game() function
        print("Player", winning_player + 1, "wins!!!")
        print("Press enter to continue.")
        input()

        start_game()

def client_server_test():
    print("client_server_test")
    c1 = ClientMessenger("127.0.0.1", 9999)
    c1.connect()
    c1.create_account("user1", "pswd")
    c1.login("user1", "pswd")
    c2 = ClientMessenger("127.0.0.1", 9999)
    c2.connect()
    c2.create_account("user2", "pswd")
    c2.login("user2", "pswd")
    c1.connect_with_opponent("user2")
    c2.connect_with_opponent("user1")

    """old_shot = c2.get_state().opponent_last_shot
    print("my last shot:", c1.get_state().user_shots)
    c1.send_shot("a2")
    while old_shot is c2.get_state().opponent_last_shot:
        time.sleep(0.1)
        c1.rec_data()
        c2.rec_data()
        print("waiting")"""

    old_shot = c1.get_state().user_shots
    print("my last shot:", c1.get_state().user_shots)
    c1.send_shot("a2")
    while old_shot is c1.get_state().user_shots:
        time.sleep(0.1)
        c1.rec_data()
        print("waiting")

    print("my last shot:", c1.get_state().user_shots)
    #print("shot:", c2.get_state().opponent_last_shot)


def start_game():
    # Test client_server_test()
    client_server_test()

    # Make a game instance, and run the game.
    battleship = Battleship()
    battleship.run_application()


if __name__ == '__main__':
    start_game()
