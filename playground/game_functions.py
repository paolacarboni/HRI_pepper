def pepper_turn():
    pepper_cmd.robot.say(random.choice((
    "Thinking ...",
    "Let's see...",
    "What to do...?"
    )))
    #QUI DOMANDA, MA NON POTREMO FAR DIRE QUALCOSA A PEPPER TRA LA SCELTA DELLA PRIMA CARTA 
    #E LA SCELTA DELLA SECONDA CARTA?
    pair1, pair2 = game.select_random_pair()
    game.check_pairs(pair1, pair2, "computer")

def elder_turn():

    pepper_cmd.robot.say(random.choice(('Your move :)', 'Your turn', 'Go', "What will you do?")))
 
    pair1, pair2 = game.player_choose_pair()
    game.check_pairs(pair1, pair2, "player")
    
    impatience_responses = [
    "Hey, it's your turn",
    "Please, make a move",
    "Come on",
    "Don't think too hard",
    "Just pick a tile",
    "Entering sleep mode... Just kidding."
    ]

def game_interaction():      
       # Choose difficulty
       pepper_cmd.robot.say("Please choose the difficulty: very easy, easy, medium, hard, or very hard.")
       
       response = get_user_input(["game_difficulty"])
       difficulty_levels = VOCABULARY["game_difficulty"]
       
       if response:
          difficulty_index = difficulty_levels.index(response)
          game.level =  difficulty_index
          pepper_cmd.robot.say("you chose...")

       game.initialize_board()
       
       # Who starts?
       pepper_cmd.robot.say("Let's decide who starts. Say even or odd.")
       response = get_user_input("Say even or odd", ["even", "odd"])
       if response:
           player_starts = random.choice([True, False])
           if player_starts:
               pepper_cmd.robot.say("You start!")
           else:
               pepper_cmd.robot.say("I start!")
        
        # Game loop
       while np.any(game.board != 0):
            if player_starts:
                player_turn()
                player_starts = False
            else:
                pepper_turn()
                player_starts = True        
        
        # End of game
       if game.user_score >  game.robot_score:
          pepper_cmd.robot.say("You win! Congratulations!")
       elif game.user_score < game.robot_score:
           pepper_cmd.robot.say("I win! Better luck next time.")
       else:
           pepper_cmd.robot.say("It's a tie! Good game.")   
