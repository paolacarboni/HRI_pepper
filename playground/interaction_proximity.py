import os
import sys
import time
import qi
from datetime import datetime
from game_functions import *
sys.path.append(os.getenv('PEPPER_TOOLS_HOME')+'/cmd_server')

import pepper_cmd
from pepper_cmd import *

motion_service = None
app = None

## Import the memory game class
from memory_game import PlayMemoryGame_1, dictionary_fruits, image_paths_fruits

# Initialize the memory game
game = PlayMemoryGame_1(dictionary=dictionary_fruits, image_paths=image_paths_fruits)

TRUST_THRESHOLD = 3
VOCABULARY = {
    "yes_no": ["yes", "no", "not sure"],
    "feelings": ["fine", "good", "bad", "not great", "you too"],
    "locations": ["garden", "my room", "corridor"],
    "game_difficulty": ["very easy", "easy", "medium", "hard", "very hard"]
}

class ProxemicsSimulator:
    ZONES = {
        'intimate': (0, 0.45),    
        'personal': (0.45, 1.2),  
        'social': (1.2, 3.6),     
        'public': (3.6, float('inf'))
    }
    
    def __init__(self):
        self.current_distance = 4.0  # Start in public zone
        self.trust_level = 0
        
    def set_distance(self, distance):
        self.current_distance = distance
        
    def get_zone(self):
        for zone, (min_dist, max_dist) in self.ZONES.items():
            if min_dist <= self.current_distance < max_dist:
                return zone
        return 'public'
    
    def is_too_close(self):
        return self.current_distance < self.ZONES['personal'][0]

def move_forward(distance):

    try:
        motion_service = pepper_cmd.robot.session.service("ALMotion")
        motion_service.moveTo(distance, 0, 0)  # (x, y, theta)
        time.sleep(1)  # Small delay for movement completion
    except Exception as e:
        print(e)
       

def move_to_zone(target_zone, current_zone):
    """Move Pepper to the specified zone using qi motion"""
    zone_distances = {
        'public': 3.6,
        'social': 1.5,
        'personal': 0.8,
        'intimate': 0.3
    }
    target_distance = zone_distances.get(target_zone)
    print(target_distance)
    current_dist = zone_distances.get(current_zone)
    print(current_dist)
    movement = current_dist - target_distance
    print(movement)
    move_forward(movement)
       
def get_user_input(categories=None):
    while True:
        try:
            response = sys.stdin.readline().strip().lower()  # Read input

            if categories:
                # Check each category's keywords
                for category in categories:
                    for keyword in VOCABULARY.get(category, []):
                        if keyword in response:  # Check if keyword is contained in response
                            return keyword  # Return the standardized response
                
                # If no keywords matched
                print("I didn't understand that. Please try again.")
            else:
                return response  # No filtering, return raw input
                
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            sys.exit(0)

def wave_hello():
    try:
        # Get motion service
        motion_service = pepper_cmd.robot.session.service("ALMotion")
        
        # Wake up the robot if it's in rest mode
        motion_service.wakeUp()
        
        # Set stiffness to make the robot ready for movement
        motion_service.setStiffnesses("RArm", 1.0)

    # Define the wave motion
        names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]
        angles = [0.0, -0.2, 1.0, 1.0, 0.0]  # Adjust these angles for the desired wave motion
        times = [1.0, 1.0, 1.0, 1.0, 1.0]
        motion_service.angleInterpolation(names, angles, times, True)

    # Reset stiffness after the motion
        motion_service.setStiffnesses("RArm", 0.0)
        
    except Exception as e:
        print(e)
        
        
def reset_arm():
    try:
        # Get motion service
        motion_service = pepper_cmd.robot.session.service("ALMotion")
        
    # Set stiffness to make the robot ready for movement
        motion_service.setStiffnesses("RArm", 1.0)

    # Define the initial pose for the arm
        names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]
        angles = [1.5, -0.2, 1.0, 0.5, 0.0]  # Default arm position
        times = [1.0, 1.0, 1.0, 1.0, 1.0]  # Time to reach the position
        motion_service.angleInterpolation(names, angles, times, True)

        motion_service.setStiffnesses("RArm", 0.0)
            
    except Exception as e:
        print(e)
    
def assess_confusion():
    questions = [
        "Do you know what day it is today?",
        "Can you tell me where we are right now?",
        "Do you remember my name?"
    ]
    
    confusion_score = 0
    for q in questions:
        pepper_cmd.robot.say(q)
        response = get_user_input(["locations", "yes_no"])
        
        if "not sure" in response or "no" in response:
            confusion_score += 1
        time.sleep(1)
    
    return confusion_score > 1
        
def build_trust():
    trust_points = 0
    greetings = [
        "It is a good day?",
        "It's nice to meet you today.",
        "How are you feeling right now?"
    ]
    
    for greeting in greetings:
        pepper_cmd.robot.say(greeting)
        response = get_user_input(["feelings"])
        if response:
            trust_points += 1
        if response in ["bad", "not great"]:
            pepper_cmd.robot.say("I'm sorry to hear that. I hope I can help!")
        else:
            pepper_cmd.robot.say("Happy to hear that!")
        time.sleep(1)
    
    return trust_points >= TRUST_THRESHOLD
    
  
def interaction_flow():
    try:
        begin()

        proxemics = ProxemicsSimulator()
        
        print("\n=== Starting Interaction ===")

        proxemics.set_distance(4.0)
        print(proxemics.current_distance)
        print(proxemics.get_zone())
        
        wave_hello()
        pepper_cmd.robot.say("Hello there! May I approach you?")
        reset_arm()
        response = get_user_input(["yes_no"])
        
        if "yes" in response:
            move_to_zone('social', proxemics.get_zone())
            proxemics.set_distance(2.5)
            print(proxemics.current_distance)
            print(proxemics.get_zone())
            
            if build_trust():
                print("Trust established!")
                move_to_zone('personal', proxemics.get_zone())
                proxemics.set_distance(1.0)
                print(proxemics.get_zone())
                
                if not assess_confusion():
                    print("User appears oriented")
                    
                    pepper_cmd.robot.say("Would you like to play a memory game?")
                    response = get_user_input(["yes_no"])
                    if "yes" in response:
                        print("\n=== STARTING GAME ===")
                        wave_hello()
                        pepper_cmd.robot.say("Great! Let's play the game.")
                        
                        game_interaction()
                    else:
                        pepper_cmd.robot.say("Maybe another time then.")
                        move_to_zone('social', proxemics.get_zone())
                else:
                    pepper_cmd.robot.say("Let me get a human assistant for you.")
                    move_to_zone('public', proxemics.get_zone())
            else:
                pepper_cmd.robot.say("I'll give you some space.")
                move_to_zone('public', proxemics.get_zone())
        else:
            pepper_cmd.robot.say("Okay, I'll stay here.")
        
        #reset_arm()
        end()
 
        print("=== Interaction Complete ===")
    except Exception as e:
        print(e)
        end()

if __name__ == "__main__":
    interaction_flow()

