from string import ascii_uppercase
import random

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from my_constants import *

class BattleshipGame:

    def __init__(self):
        # Number of random ships to place for testing purposes
        self.num_ships = NUM_SHIPS

        # Define values for ships, misses, and hits
        self.empty_sea = 0
        self.ship_int = range(3, self.num_ships + 3)
        self.miss_int = 1
        self.hit_int = 2

        '''
        This only works for ships = 2, need to wrap up into for statement to append additionally required 'grey's.
        '''
        init_cmap = ['cornflowerblue', 'snow', 'red']
        player_cmap = init_cmap.copy()
        for i in range(0, self.num_ships):
            player_cmap.append('grey')
        self.player_cmap = ListedColormap(player_cmap)
        self.opponent_cmap = ListedColormap(init_cmap)

        self.num_ship_hits = [2, 3, 3, 4, 5]
        self.ship_names = ["Patrol Boat", "Submarine", "Destroyer", "Battleship", "Carrier"]

        # Define size of board
        self.board_size = BOARD_SIZE

        # Define player count
        self.player_count = PLAYER_COUNT

        # Create dictionary of board letter mappings, this is just a list
        # [a, b, c, .., x] to map outputs to (real battleship)
        self.board_letter_mappings = self.create_letter_mappings()

        # Create gameboards for the number of players
        # At the moment, these gameboards randomly place five ships
        self.player_gameboards = {}
        for player in range(self.player_count):
            self.player_gameboards['p{player}_gameboard'.format(player=player)] = self.create_gameboard()

    def get_num_ships(self):
        return self.num_ships

    def get_num_ship_hits(self):
        return self.num_ship_hits

    def create_gameboard(self):
        # Create a gameboard of all zeroes (numpy matrix)
        gameboard_obj = np.zeros(shape=[self.board_size, self.board_size])

        # Below is for placing randomly for testing
        # Define list to hold ship coords in
        # ships = []
        # for i in self.ship_int:
        #    ship_length = self.num_ship_hits[i - SHIP_OFFSET]
        #    direction = random.choice(['horizontal', 'vertical'])
        #    ship_coords = self.place_ship(gameboard_obj, ship_length, direction, i)
        #    ships.append(ship_coords)

        return gameboard_obj

    def place_ship(self, gameboard, length, direction, ship_number):
        # Random placement for now, this should still handle borders as we're
        # only working in the confines of board_size
        while True:
            row = random.randint(0, self.board_size - 1)
            col = random.randint(0, self.board_size - 1)
            if direction == 'horizontal' and col + length <= self.board_size:
                coords = [(row, i) for i in range(col, col + length)]
            elif direction == 'vertical' and row + length <= self.board_size:
                coords = [(i, col) for i in range(row, row + length)]
            else:
                continue
            if all(gameboard[r][c] == 0 for r, c in coords):
                for r, c in coords:
                    gameboard[r][c] = ship_number
                return coords

    def place_single_ship(self, player, ship_number, direction, coord_tuple):
        # Checks placement of ship. If valid, places ship and returns true. If not, return false.

        gameboard = player.get_user_gameboard()

        row = coord_tuple[0]
        col = coord_tuple[1]

        if direction in ['h', 'H'] and col + self.num_ship_hits[ship_number] - 1 <= self.board_size:
            coords = [(row, i) for i in range(col, col + self.num_ship_hits[ship_number])]
        elif direction in ['v', 'V'] and row + self.num_ship_hits[ship_number] - 1 <= self.board_size:
            coords = [(i, col) for i in range(row, row + self.num_ship_hits[ship_number])]
        else:
            print("Your ship must lie entirely within A1 to J10.")
            return False

        if all(gameboard[r - 1][c - 1] == 0 for r, c in coords):
            for r, c in coords:
                gameboard[r - 1][c - 1] = ship_number + SHIP_OFFSET

            #print(self.display_heatmap(gameboard, version='self'))
            print(player.user_gameboard)
            return True
        else:
            print("You cannot place a ship over another one of your ships.")
            return False

    def create_letter_mappings(self):
        # ascii_uppercase generates a list of ascending letters
        list_letters = list(ascii_uppercase)[0:self.board_size]

        # Map int keys to letter values
        letter_mappings = {}
        for num, letter in zip(range(self.board_size), list_letters):
            letter_mappings[num] = letter

        return letter_mappings

    def check_shot(self, player, coord_tuple):
        # Load current player's board
        p_gameboard = player.get_user_gameboard()

        # Get the table entry at the coordinates
        cell_id = int(p_gameboard[coord_tuple[0]][coord_tuple[1]])

        # If the shot has already been attempted
        if cell_id == 1 or cell_id == 2:
            print("You've already attempted that shot.")
            return INVALID

        # If guessed coord_tuple matches a ship number, return True and change value
        elif cell_id in range(SHIP_OFFSET, self.num_ships + SHIP_OFFSET):
            p_gameboard[coord_tuple[0]][coord_tuple[1]] = self.hit_int
            player.decrease_hits_remaining(cell_id - SHIP_OFFSET)

            letter = self.board_letter_mappings.get(coord_tuple[0])
            number = coord_tuple[1] + 1

            print(f"Fired shot at {letter}{number}! " + "HIT!!!")

            if (player.hits_remaining[cell_id - SHIP_OFFSET] == 0):
                print("You sunk my " + self.ship_names[cell_id - SHIP_OFFSET] + "!\n")
                player.decrease_ships_remaining()
            return HIT

        # Else if guessed coord_tuple does not match ship_int, return False and change value
        else:
            p_gameboard[coord_tuple[0]][coord_tuple[1]] = self.miss_int
            letter = self.board_letter_mappings.get(coord_tuple[0])
            number = coord_tuple[1] + 1
            print(f"Fired shot at {letter}{number}! " + "MISS!!!")
            return MISSED

    def fire_shot(self, player, coord_tuple):
        # Decrement tuple by one to make ints be less inty
        coord_tuple = tuple(map(lambda i, j: i - j, coord_tuple, (1, 1)))

        # Load gameboard for given player
        # p_gameboard = self.player_gameboards.get('p{player}_gameboard'.format(player=player))
        p_gameboard = player.get_user_gameboard()

        result = self.check_shot(player, coord_tuple)

        # Update player gamebaord
        # self.player_gameboards.update({'p{player}_gameboard'.format(player=player):p_gameboard})
        player.set_user_gameboard(p_gameboard)

        return result

    def display_both_heatmaps(self, player_gameboard, opponent_gameboard, player_username, opponent_username, end_ind):
        """Displays the player's gameboard as a heatmap on the left and 
        the opponent's gameboard as a heatmap on the right"""
        plt.rcParams["figure.figsize"] = [7.50, 3.50]
        plt.rcParams["figure.autolayout"] = True

        # Mask opponent gameboard
        opponent_gameboard_copy = opponent_gameboard.copy()
        opponent_gameboard_copy[opponent_gameboard_copy > 2] = 0
        print("Opponent masked gameboard", opponent_gameboard_copy)

        plt.close('all')
        if end_ind:
            plt.close('all')
            self.display_heatmap(player_gameboard, 'WINNER: Player {} Gameboard'.format(player_username), 
                                100, 200, 500, 500, type='player', player_username=player_username,
                                opponent_username=opponent_username)
        else: 
            self.display_heatmap(player_gameboard, 'Player {} Gameboard'.format(player_username), 
                             100, 200, 500, 500, type='player', player_username=player_username,
                             opponent_username=opponent_username)
            self.display_heatmap(opponent_gameboard_copy, 'Opponent Gameboard', 600, 200, 500, 500, type='opponent', 
                                player_username=player_username, opponent_username=opponent_username)

    def display_heatmap(self, gameboard, title, x, y, w, h, type, player_username, opponent_username):
        if type == 'player':
            plt.matshow(gameboard, cmap=self.player_cmap)
        if type == 'opponent':
            plt.matshow(gameboard, cmap=self.opponent_cmap)


        plt.title(title)
        list_letters_xaxis = list(ascii_uppercase)[0:self.board_size]

        loc_y = range(len(list_letters_xaxis))
        labels_y = list_letters_xaxis
        plt.yticks(loc_y, labels_y)

        loc_x = range(self.board_size)

        labels_x = [1,2,3,4,5,6,7,8,9,10]

        if player_username > opponent_username:
            y = y + 500
            
            plt.get_current_fig_manager().window.setGeometry(x, y, w, h)
            plt.xticks(loc_x, labels_x)
            plt.ion()
            plt.show()
        else:
            plt.get_current_fig_manager().window.setGeometry(x, y, w, h)
            plt.xticks(loc_x, labels_x)
            plt.ion()
            plt.show()
