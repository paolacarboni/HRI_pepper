# -*- coding: utf-8 -*-
"""memory_game.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1dqnCR_KitZR05mYiXP0SSqXYCQAm7zkg
"""

import numpy as np
import random
import time
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from google.colab import drive
drive.mount('/content/drive')

dictionary_fruits = {
               0: 'card_back',
               1 : 'apple',
               2 : 'banana',
               3 : 'orange',
               4 : 'pear',
               5 : 'kiwi',
               6 : 'peach',
               7 : 'cherry',
               8 : 'strawberry',
               9 : 'blueberry',
               10 : 'watermelon',
               11 : 'raspberry',
               12 : 'apricot',
               13 : 'coconut',
               14 : 'lemon',
               15 : 'grapes',
               16 : 'mango',
               17 : 'papaya',
               18 : 'plum',
               19 : 'pomegranate',
               20: 'pineapple',
              }

image_path = "/content/drive/MyDrive/HRI/project/memory_game/images/"
empty_card_path = image_path + "empty_card.jpg"
card_back_path = image_path + "card_back.jpg"

image_paths_fruits = {
    1: image_path + "apple.jpg",
    2: image_path + "banana.jpg",
    3: image_path + "orange.jpg",
    4: image_path + "pear.jpg",
    5: image_path + "kiwi.jpg",
    6: image_path + "peach.jpg",
    7: image_path + "cherry.jpg",
    8: image_path + "strawberry.jpg",
    9: image_path + "blueberry.jpg",
    10: image_path + "watermelon.jpg",
    11: image_path + "raspberry.jpg",
    12: image_path + "apricot.jpg",
    13: image_path + "coconut.jpg",
    14: image_path + "lemon.jpg",
    15: image_path + "grapes.jpg",
    16: image_path + "mango.jpg",
    17: image_path + "papaya.jpg",
    18: image_path + "plum.jpg",
    19: image_path + "pomegranate.jpg",
    20: image_path + "pineapple.jpg"
}

class PlayMemoryGame_1:
    def __init__(self, dictionary, image_paths):
        self.height = 0
        self.width = 0
        self.level = 0
        self.user_score = 0
        self.robot_score = 0
        self.dictionary = dictionary
        self.image_paths = image_paths

    def choose_difficulty(self):
      while True:
          try:
              self.level = int(input('Please choose the difficulty: very easy (0), easy (1), medium (2), hard (3), very hard (4)? '))
              if self.level in [0, 1, 2, 3, 4]:
                  break
              else:
                  print("Invalid choice. Enter 0, 1, 2, 3 or 4.")
          except ValueError:
              print("Invalid input! Enter 0, 1, 2, 3 or 4.")

      # Corrected the print statement with proper ternary logic
      print(f'You chose {"very easy" if self.level == 0 else "easy" if self.level == 1 else "medium" if self.level == 2 else "hard" if self.level == 3 else "very hard"}!')
      #return self.level

    def initialize_board(self):
        '''
        This function initializes the board with random pairs of cards.
        '''
        if self.level == 0:
            self.height = 2
            self.width = 3
        elif self.level == 1:
            self.height = 3
            self.width = 4
        elif self.level == 2:
            self.height = 4
            self.width = 5
        elif self.level == 3:
            self.height = 5
            self.width = 6
        else:
            self.height = 5
            self.width = 8

        self.board = np.zeros((self.height, self.width)) # this is the gt of the board
        self.face_up = np.zeros((self.height, self.width)) # this tells if the cards are facing up
        self.visible_board = np.zeros((self.height, self.width))
        num_cards = self.height * self.width
        if num_cards % 2 != 0:
            print('Number of cards must be even')
            return

        num_types = num_cards // 2
        card_list = list(range(1, num_types + 1)) * 2  # Create game deck of cards
        random.shuffle(card_list) # shuffle deck

        count = 0
        for i in range(self.height):
            for j in range(self.width):
                self.board[i, j] = card_list[count]
                count += 1
        #print(type(self.board))
        ###
        self.board = np.array(card_list).reshape(self.height, self.width)  # Create board

        # Replace numbers with dictionary values
        self.board_strings = np.vectorize(self.dictionary.get)(self.board)
        #print(self.board_strings)

    def select_random_pair(self):
        '''
        This function selects two random cards from the board when it's the computer's turn.
        '''
        while True:
            row1, col1 = random.randint(0, self.height - 1), random.randint(0, self.width - 1)
            if self.board[row1, col1] != 0:
                break
        self.face_up[row1, col1] = 1
        self.display_board()

        time.sleep(4)

        while True:
            row2, col2 = random.randint(0, self.height - 1), random.randint(0, self.width - 1)
            if self.board[row2, col2] != 0 and (row1, col1) != (row2, col2):
                break

        self.face_up[row2, col2] = 1
        self.display_board()

        print(f"Computer chooses ({row1}, {col1}) and ({row2}, {col2})")
        # self.face_up[row1, col1] = 1
        # self.face_up[row2, col2] = 1

        return (row1, col1), (row2, col2)

    def check_pairs(self, pair1, pair2, player):
        '''
        This function checks if the selected cards match and updates the score.
        '''
        row1, col1 = pair1
        row2, col2 = pair2

        if self.board[row1, col1] == self.board[row2, col2]:
            print("Match found!")
            self.board[row1, col1] = 0
            self.board[row2, col2] = 0

            if player == "player":
                self.user_score += 1
            else:
                self.robot_score += 1
        else:
            print("No match!")
            self.face_up[row1, col1] = 0
            self.face_up[row2, col2] = 0
        self.display_board()

    def player_choose_pair(self):
        '''
        This function allows the player to choose two cards.
        '''
        while True:
            try:
                row1 = int(input(f"Enter row for first card (0 to {self.height - 1}): "))
                col1 = int(input(f"Enter column for first card (0 to {self.width - 1}): "))
                if self.board[row1, col1] == 0:
                    print("Card no longer on the table. Choose again.")
                    continue
                break
            except (ValueError, IndexError):
                print("Invalid input! Try again.")

        self.face_up[row1, col1] = 1
        self.display_board()

        while True:
            try:
                row2 = int(input(f"Enter row for second card (0 to {self.height - 1}): "))
                col2 = int(input(f"Enter column for second card (0 to {self.width - 1}): "))
                if self.board[row2, col2] == 0 or (row1, col1) == (row2, col2):
                    print("Invalid selection. Try again.")
                    continue
                break
            except (ValueError, IndexError):
                print("Invalid input! Try again.")

        self.face_up[row2, col2] = 1
        self.display_board()
        return (row1, col1), (row2, col2)

    def play_even_or_odd(self):
        '''
        This function plays the game even or odd.
        '''
        while True:
            try:
                choice = int(input('Your choice: even (0) or odd (1)? '))
                if choice in [0, 1]:
                    break
                else:
                    print("Invalid choice. Enter 0 or 1.")
            except ValueError:
                print("Invalid input! Enter 0 or 1.")

        print(f'You chose {"even" if choice == 0 else "odd"}!')
        random_num = random.randint(0, 1)
        print(f"Random number: {random_num}")

        return 1 if random_num == choice else 0

    def display_board(self):
      '''
      This function displays the board graphically using images.
      '''
      fig, ax = plt.subplots(self.height, self.width, figsize=(self.width, self.height))

      for i in range(self.height):
          for j in range(self.width):
              ax[i, j].axis("off")  # Hide axes
              if self.face_up[i, j] == 1 and self.board[i,j]!=0:  # Show image if face-up
                  img_path = self.image_paths[self.board[i, j]]
                  img = mpimg.imread(img_path)
                  ax[i, j].imshow(img)
              elif self.board[i,j]==0:
                  ax[i, j].imshow(mpimg.imread(empty_card_path))

              else:  # Show card back
                  ax[i, j].imshow(mpimg.imread(card_back_path))

      plt.show()

    def play_game(self):
        '''
        This function plays the complete memory game.
        '''
        self.choose_difficulty()
        self.initialize_board()
        #print("Initial GT Board:")
        #print(self.board_strings)
        #print("Visible Board:")
        #self.visible_board = self.board*self.face_up
        #print(self.visible_board)

        player_turn = self.play_even_or_odd()
        print("You start!" if player_turn else "Computer starts!")

        while np.any(self.board != 0):  # Continue while there are cards on the board
            if player_turn:
                print("\nYour turn!")
                pair1, pair2 = self.player_choose_pair()
                user_points_temp = self.user_score
                #print('visible board:')
                #self.visible_board = self.board*self.face_up
                #print(self.visible_board)
                #self.visible_board_strings = np.vectorize(self.dictionary.get)(self.visible_board)
                #print(self.visible_board_strings)
                #self.display_board()
                self.check_pairs(pair1, pair2, "player")
                if self.user_score == user_points_temp:
                    player_turn = not player_turn
            else:
                print("\nComputer's turn!")
                pair1, pair2 = self.select_random_pair()
                robot_points_temp = self.robot_score
                #print('visible board:')
                #self.visible_board = self.board*self.face_up
                #print(self.visible_board)
                #self.visible_board_strings = np.vectorize(self.dictionary.get)(self.visible_board)
                #print(self.visible_board_strings)
                # self.display_board()
                time.sleep(5)
                self.check_pairs(pair1, pair2, "computer")
                if self.robot_score == robot_points_temp:
                    player_turn = not player_turn

            print(f"Score - Player: {self.user_score}, Computer: {self.robot_score}")
            #player_turn = not player_turn  # Switch turn


        print("\nGame Over!")
        if self.user_score > self.robot_score:
            print("You win!")
        elif self.user_score < self.robot_score:
            print("Computer wins!")
        else:
            print("It's a tie!")

game = PlayMemoryGame_1(dictionary=dictionary_fruits, image_paths=image_paths_fruits)

# Start the game
game.play_game()