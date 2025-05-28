import os
import sys
import time
from datetime import datetime
import tornado.ioloop
import tornado.web
import tornado.websocket
import inspect    # getsourcefile
import os.path
import mimetypes # For guessing file types
import platform  # For OS-specific path handling in webbrowser
import random

sys.path.append(os.getenv('PEPPER_TOOLS_HOME')+'/cmd_server')

import pepper_cmd
from pepper_cmd import *

import threading
import webbrowser
try:
    # Python 2 uses Queue module
    from Queue import Queue, Empty
except ImportError:
    # Python 3 uses queue module
    # Corrected import for Python 3:
    import queue # Import the module directly
    Queue = queue.Queue # Assign the Queue class from the module to a variable named Queue
    Empty = queue.Empty # Assign Empty exception similarly


motion_service = None

# Corrected Queue initialization
game_result_queue = Queue()
robot_action_queue = Queue()
selected_passion = None
selected_name = None

# --- Tornado Server Code ---
class WebSocketServer(tornado.websocket.WebSocketHandler):
    clients = set() # Keep track of all connected clients

    # broadcast to all clients
    @classmethod
    def send_to_all_clients(cls, message):

        #print("[WebSocket] Broadcasting to {} client(s): {}".format(len(cls.clients), message))
        for client in cls.clients:
            try:
                client.write_message(message)
            except tornado.websocket.WebSocketClosedError:
                print("[WebSocket] Error broadcasting: A connection was closed.")
                cls.clients.discard(client)
            except Exception as e:
                print("[WebSocket] Error broadcasting message to a client: {}".format(e))


    def open(self):
        print("[WebSocket] New client connected.")
        WebSocketServer.clients.add(self)

        global selected_passion, selected_name
        if selected_passion:
            theme_message = "theme {}".format(selected_passion)
            print("[WebSocket] Sending initial theme to new client: '{theme_message}'".format(theme_message=theme_message))
            try:
                self.write_message(theme_message)
            except Exception as e:
                print("[WebSocket] Error sending initial theme: {}".format(e))

        if selected_name:
            name_message = "name {}".format(selected_name)
            print("[WebSocket] Sending initial name to new client: '{name_message}'".format(name_message=name_message))
            try:
                self.write_message(name_message)
            except Exception as e:
                print("[WebSocket] Error sending initial name: {}".format(e))

    def on_message(self, message):
        global game_result_queue, robot_action_queue # Ensure robot_action_queue is global here
        command = message.strip().lower()
        if command in ["win", "lose", "tie"]:
            print("[WebSocket] Received game outcome signal: '{command}'".format(command=command))
            try: game_result_queue.put(command)
            except Exception: pass
        elif command == "endgame": # NEW: Handle endgame signal from frontend
            print("[WebSocket] Received 'endgame' signal from client. Adding to robot action queue.")
            try:
                robot_action_queue.put("return_to_start")
            except Exception as e:
                print("[WebSocket] Error putting 'return_to_start' into queue: {}".format(e))


    def on_close(self):
        print("[WebSocket] Client disconnected.")
        if self in WebSocketServer.clients:
            WebSocketServer.clients.remove(self)

    def check_origin(self, origin):
        return True

class FileHandler(tornado.web.RequestHandler):
    def get(self, requested_path):
        try:
            source_dir = os.path.dirname(os.path.abspath(inspect.getsourcefile(lambda:0)))
            abs_path = os.path.normpath(os.path.join(source_dir, requested_path))
            if not abs_path.startswith(source_dir): raise tornado.web.HTTPError(403, "Access denied")
            if not os.path.isfile(abs_path): raise tornado.web.HTTPError(404, "File not found")
            content_type, encoding = mimetypes.guess_type(abs_path)
            self.set_header("Content-Type", content_type if content_type else "application/octet-stream")
            with open(abs_path, "rb") as f: self.write(f.read())
            self.finish()
        except tornado.web.HTTPError as e: self.send_error(e.status_code)
        except Exception: self.send_error(500)

# def make_app():
#     return tornado.web.Application([
#         (r'/ws', WebSocketServer), (r"/(index\.html)", FileHandler),
#         (r"/(script\.js)", FileHandler), (r"/(style\.css)", FileHandler),
#         (r"/(.*\.(?:js|css|jpg|jpeg|png|gif|ico|woff|woff2|ttf|eot|svg|map))", FileHandler),
#         (r"/", tornado.web.RedirectHandler, {"url": "/index.html"}),
#     ])

def make_app():
    # Get the directory where main.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print("[Server] Serving static files from: {}".format(current_dir)) # Added for debugging

    # Define the handlers for the Tornado web application
    return tornado.web.Application([
        # WebSocket endpoint
        (r'/ws', WebSocketServer),

        # Handler for index.html (served directly from the script's directory)
        (r"/(index\.html)", tornado.web.StaticFileHandler, {"path": current_dir}),

        # Handler for script.js (served directly from the script's directory)
        (r"/(script\.js)", tornado.web.StaticFileHandler, {"path": current_dir}),

        # Handler for style.css (served directly from the script's directory)
        (r"/(style\.css)", tornado.web.StaticFileHandler, {"path": current_dir}),

        # Handler for files within the 'images' subdirectory
        # This regex matches any path starting with /images/ and captures the rest (.*)
        # The path parameter then tells StaticFileHandler to look inside the 'images' folder
        (r"/images/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(current_dir, "images")}),

        # Generic handler for other common static files (like fonts, manifest, etc.)
        # Assumes these files are also directly in the script's directory (e.g., /favicon.ico)
        (r"/(.*\.(?:js|css|jpg|jpeg|png|gif|ico|woff|woff2|ttf|eot|svg|map|json|webmanifest))",
         tornado.web.StaticFileHandler, {"path": current_dir}),

        # Redirect root URL to index.html
        (r"/", tornado.web.RedirectHandler, {"url": "/index.html"}),
    ])
def run_tornado_server():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir); app = make_app(); app.listen(8889)
        tornado.ioloop.IOLoop.current().start()
    except Exception as e: print("[Server] FATAL ERROR: Failed to start web server: {}".format(e))

TRUST_THRESHOLD = 3
VOCABULARY = {
    "yes_no": ["yes", "no", "not sure", "maybe", "i don't know"],
    "feelings": ["fine", "good", "great", "okay", "bad", "not great", "terrible", "you too"],
    "locations": ["garden", "my room", "the corridor", "here", "activity room", "living room"],
    "names" : ["giovanni","paola", "paolo"],
    "pepper_name": ["pepper"]
}
USER_DATABASE = {
    "giovanni": {"name" : "Giovanni",
                "passion": "fruits",
                "greeting": "Ah, Giovanni! Welcome back!"},
    "paola": {"name" : "paola",
              "passion": "music",
              "greeting": "Hello paola! Great to see you again!"},
    "paolo": {"name" : "Paolo",
              "passion": "gardening",
              "greeting": "Paolo, good to see you! "},
}



class ProxemicsSimulator:
    ZONES = {'intimate': (0, 0.45), 'personal': (0.45, 1.2), 'social': (1.2, 3.6), 'public': (3.6, float('inf'))}
    def __init__(self): self.current_distance = 4.0; self.trust_level = 0
    def set_distance(self, distance): self.current_distance = max(0, distance)
    def get_zone(self):
        for zone, (min_dist, max_dist) in self.ZONES.items():
            if float(min_dist) <= float(self.current_distance) < float(max_dist): return zone
        return 'public'

def move_forward(distance_meters):
    global motion_service
    if not motion_service:
        print("Pepper (sim) moves by {:.2f}m".format(distance_meters))
        return
    try:
        motion_service.moveTo(distance_meters, 0, 0)
        time.sleep(0.5)
    except Exception: pass

def move_to_zone(target_zone, current_zone):
    zone_target_distances = {'public': 3.0, 'social': 1.5, 'personal': 0.8, 'intimate': 0.3}
    target_distance = zone_target_distances.get(target_zone)
    current_typical_dist = zone_target_distances.get(current_zone)
    if target_distance is None or current_typical_dist is None: return
    movement = float(current_typical_dist) - float(target_distance)
    if abs(movement) > 0.1: move_forward(movement)

def get_user_input(categories=None):
    user_input_prompt = "You: "
    while True:
        try:
            response = raw_input(user_input_prompt).strip().lower()
            if not response:
                pepper_cmd.robot.say("Sorry, I didn't catch that. Could you please say it again?")
                continue
            if categories:
                for category_name in categories:
                    for keyword in VOCABULARY.get(category_name, []):
                        if keyword in response: return keyword
                unrecognized_msg = "I'm sorry, I didn't quite understand that."
                if 'yes_no' in categories: unrecognized_msg += " Please try saying 'yes' or 'no'."
                elif 'names' in categories: unrecognized_msg += " Could you please tell me your name again?"
                pepper_cmd.robot.say(unrecognized_msg)
            else: return response
        except (EOFError, KeyboardInterrupt): print("\nUser interrupted. Exiting..."); sys.exit(0)
        except AttributeError:
            print("Pepper (sim) says: \"{}\"".format("Sorry, I didn't catch that. Could you please say it again?"))
        except Exception as e: print("\nError reading input: {}".format(e)); sys.exit(1)

#def get_user_input(categories=None):
    # This part was for debugging with raw_input/input in terminal
    # user_input_prompt = "You: "
    # while True:
    #     try:
    #         response = input(user_input_prompt).strip().lower() # Assuming Python 3
    #         # ... (rest of old input logic)
    #     except Exception: pass

    # while True:
    #     try:
    #         print("Pepper (robot) is now listening...") # For your terminal to know
    #         # Use Pepper's listen function.
    #         # You might want to pass a vocabulary list for better recognition.
    #         # `listen()` returns the recognized text.
    #         recognized_text = ""
    #         if pepper_cmd.robot: # Check if connected to actual robot
    #             # Use a specific vocabulary if categories are provided
    #             if categories:
    #                 # Collect all relevant words from specified categories
    #                 vocab_list = []
    #                 for category_name in categories:
    #                     vocab_list.extend(VOCABULARY.get(category_name, []))
    #                 # Remove duplicates and convert to a set for faster lookup, then back to list
    #                 vocab_list = list(set(vocab_list))
    #                 print("Listening with vocabulary: {vocab_list}") # For debugging
    #                 recognized_text = pepper_cmd.robot.listen(vocabulary=vocab_list)
    #             else:
    #                 # Listen without a specific vocabulary (more general)
    #                 recognized_text = pepper_cmd.robot.listen()
    #         else:
    #             # Fallback for simulation mode (if robot not connected)
    #             print("Pepper (sim) says: (Simulating listening. Please type your response)")
    #             recognized_text = input("You (simulated): ").strip().lower()

    #         response = recognized_text.strip().lower()

    #         if not response:
    #             try:
    #                 if pepper_cmd.robot: pepper_cmd.robot.say("Sorry, I didn't catch that. Could you please say it again?")
    #                 else: print("Pepper (sim) says: \"Sorry, I didn't catch that. Could you please say it again?\"")
    #             except Exception as e_say:
    #                 print("Error in say (no response): {e_say}")
    #             continue # Ask again

    #         if categories:
    #             found_keyword = None
    #             for category_name in categories:
    #                 for keyword in VOCABULARY.get(category_name, []):
    #                     # Use a more robust check for presence, or exact match if preferred
    #                     if keyword in response: # simple substring match
    #                     # if response == keyword: # exact match
    #                         found_keyword = keyword
    #                         break
    #                 if found_keyword:
    #                     break

    #             if found_keyword:
    #                 return found_keyword
    #             else:
    #                 unrecognized_msg = "I'm sorry, I didn't quite understand that."
    #                 if 'yes_no' in categories: unrecognized_msg += " Please try saying 'yes' or 'no'."
    #                 elif 'names' in categories: unrecognized_msg += " Could you please tell me your name again?"
    #                 try:
    #                     if pepper_cmd.robot: pepper_cmd.robot.say(unrecognized_msg)
    #                     else: print("Pepper (sim) says: \"{unrecognized_msg}\"")
    #                 except Exception as e_say:
    #                     print("Error in say (unrecognized): {e_say}")
    #         else:
    #             # If no categories, return the full recognized text
    #             return response

    #     except (EOFError, KeyboardInterrupt):
    #         print("\nUser interrupted. Exiting...")
    #         sys.exit(0)
    #     except AttributeError:
    #         print("Pepper (sim) says: (Simulation mode: No robot connection for listen command)")
    #         print("Please type your response in the terminal.")
    #         # Fallback to direct input if listen fails due to no robot
    #         recognized_text = input("You (simulated): ").strip().lower()
    #         return recognized_text
    #     except Exception as e:
    #         print("\nError during listening or input: {e}")
    #         import traceback
    #         traceback.print_exc()
    #         sys.exit(1)
def wave_hello():
    try:
        motion_service = pepper_cmd.robot.session.service("ALMotion")
        motion_service.wakeUp()
        motion_service.setStiffnesses("RArm", 1.0)

        names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]
        angles = [0.0, -0.2, 1.0, 1.0, 0.0]
        times = [1.0, 1.0, 1.0, 1.0, 1.0]
        motion_service.angleInterpolation(names, angles, times, True)

        motion_service.setStiffnesses("RArm", 0.0)

    except Exception as e:
        print(e)


def reset_arm():
    try:
        motion_service = pepper_cmd.robot.session.service("ALMotion")

        motion_service.setStiffnesses("RArm", 1.0)

        names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]
        angles = [1.5, -0.2, 1.0, 0.5, 0.0]
        times = [1.0, 1.0, 1.0, 1.0, 1.0]
        motion_service.angleInterpolation(names, angles, times, True)

        motion_service.setStiffnesses("RArm", 0.0)

    except Exception as e:
        print(e)

def assess_confusion():
    questions = [("Do you know what day it is today?", ["yes_no"]),
                 ("Can you tell me where we are right now?", ["locations", "yes_no"]),
                 ("Just checking, do you remember my name?", ["yes_no", "pepper_name"])]
    confusion_score = 0; positive_responses = ["yes", "i know"]
    for q_text, q_categories in questions:
        try:
            pepper_cmd.robot.say(q_text)
        except AttributeError: print("Pepper (sim) says: \"{}\"".format(q_text))
        except Exception as e_say: print("Error in assess_confusion (say): {}".format(e_say))

        response = get_user_input(q_categories)
        if response not in positive_responses and response not in VOCABULARY.get("locations", []): confusion_score += 1
        time.sleep(0.5)
    return confusion_score >= 2

def build_trust():
    trust_points = 0
    greetings = [("It's nice to interact with you today. Is it a good day for you?", ["feelings", "yes_no"]),
                 ("How are you feeling right now?", ["feelings"])]
    positive_feelings = ["fine", "good", "great", "okay", "yes"]; negative_feelings = ["bad", "not great", "terrible", "no"]
    for g_text, q_categories in greetings:
        try:
            pepper_cmd.robot.say(g_text)
        except AttributeError: print("Pepper (sim) says: \"{}\"".format(g_text))
        except Exception as e_say: print("Error in build_trust (say): {}".format(e_say))

        response = get_user_input(q_categories)

        feedback_say = ""
        if response in positive_feelings: trust_points += 1; feedback_say = random.choice((
"I'm happy to hear that",
"Lovely !",
"Very good!",
"Sounds great!"
))
        elif response in negative_feelings: feedback_say = random.choice((
"Oh, I'm sorry to hear that. I hope I can bring a little brightness.",
"I hope you'll feel better soon !",
"Oh no!"
)) 
        elif response == "you too": trust_points += 1; feedback_say = "Thank you for asking! I'm feeling operational and ready to play!"
        else: feedback_say = "Okay."

        try:
            pepper_cmd.robot.say(feedback_say)
        except AttributeError: print("Pepper (sim) says: \"{}\"".format(feedback_say))
        except Exception as e_say_fb: print("Error in build_trust (feedback_say): {}".format(e_say_fb))
        time.sleep(0.5)
    return trust_points >= 1


# --- Main Interaction Flow
def interaction_flow():
    global begin, end, selected_passion, motion_service, selected_name, robot_action_queue

    # Initialize game counters
    user_wins = 0
    pepper_wins = 0
    ties = 0

    server_thread = threading.Thread(target=run_tornado_server)
    server_thread.daemon = True; server_thread.start(); time.sleep(3)

    def begin_dummy(): pass
    def end_dummy(): pass

    begin, end = begin_dummy, end_dummy
    selected_passion = None
    selected_name = None
    motion_service = None
    initial_connection_successful = False

    proxemics = ProxemicsSimulator()
    proxemics.set_distance(4.0)

    try:
        try:
            print("Attempting to connect to Pepper...")
            pepper_cmd.begin()
            begin = pepper_cmd.begin
            end = pepper_cmd.end
            if pepper_cmd.robot and pepper_cmd.robot.session:
                 
                 motion_service = pepper_cmd.robot.session.service("ALMotion")
                 #asr_service = pepper_cmd.robot.session.service("ALSpeechRecognition")
                 #pepper_cmd.robot.asr_service.setLanguage("English")
                 motion_service.wakeUp()
                 initial_connection_successful = True
                 print("Successfully connected to Pepper.")
            else:
                print("Pepper connection attempt made, but pepper_cmd.robot or session is not available.")
                print("Proceeding in simulation mode for some functions.")
        except Exception as e_connect:
            print("Simulation mode: Pepper connection failed: {}".format(e_connect))

        behavior_manager = None
        try:
             if initial_connection_successful and pepper_cmd.robot and pepper_cmd.robot.session:
                 behavior_manager = pepper_cmd.robot.session.service("ALBehaviorManager")
        except Exception:
             class DummyBehaviorManager:
                 def isBehaviorInstalled(self, name): return True
                 def startBehavior(self, name): pass
             behavior_manager = DummyBehaviorManager()

        print("\n=== Starting Interaction Sequence ===")

        # Main interaction loop, so Pepper can react to "endgame" even if not playing
        while True:
            try:
                # Check for robot actions from WebSocket
                try:
                    action = robot_action_queue.get(block=False) # Non-blocking check
                    if action == "return_to_start":
                        print("[Main] Robot action: Returning to start position and resting.")
                        goodbye_text = "Okay, I'll return to my spot. See you next time!"
                        try:
                            if initial_connection_successful and pepper_cmd.robot:
                                pepper_cmd.robot.say(goodbye_text)
                            else:
                                print("Pepper (sim) says: \"{}\"".format(goodbye_text))
                        except Exception as e_say:
                            print("Error saying goodbye: {}".format(e_say))

                        move_to_zone('public', proxemics.get_zone())
                        proxemics.set_distance(3.6)
                        if initial_connection_successful and motion_service:
                            motion_service.rest()

                        # Reset selected passion/name when returning to start
                        selected_passion = None
                        selected_name = None
                        # No need to send empty theme/name to frontend, it's already reset to pre-intro.

                        continue # Go back to the top of the while loop to wait for new interactions
                except Empty: # Use the 'Empty' exception
                    pass # No action in queue, continue with normal flow

                # Only ask for name if not already set (new session or after endgame)
                if selected_name is None:
                    wave_hello()
                    try:
                        pepper_cmd.robot.say("Hello there! I'm Pepper. What's your name?")
                    except AttributeError: print("Pepper (sim) says: \"Hello there! I'm Pepper. What's your name?\"")
                    except Exception as e_say: print("Error during initial say: {}".format(e_say))
                    reset_arm()
                    user_name_input = pepper_cmd.robot.asr(["names"], timeout=10)
                    print("[Main] User input: {}".format(user_name_input))
                    #user_name_input = get_user_input(["names"])

                    if user_name_input in USER_DATABASE:
                        user_info = USER_DATABASE[user_name_input]
                        selected_passion, selected_greeting = user_info["passion"], user_info["greeting"]
                        selected_name = user_info["name"]
                        try: pepper_cmd.robot.say(selected_greeting)
                        except AttributeError: print("Pepper (sim) says: \"{}\"".format(selected_greeting))
                    else:
                        selected_passion = "fruits" # Default passion
                        selected_name = user_name_input if user_name_input else "friend" # Use the input or a fallback
                        greeting_unknown = "Hello {}! It's a pleasure to meet you. Today, we can try a fun fruit memory game if you like.".format(selected_name)
                        try: pepper_cmd.robot.say(greeting_unknown)
                        except AttributeError: print("Pepper (sim) says: \"{}\"".format(greeting_unknown))

                    if selected_name:
                        WebSocketServer.send_to_all_clients('name {}'.format(selected_name))
                    if selected_passion:
                        WebSocketServer.send_to_all_clients('theme {}'.format(selected_passion))

                    response = get_user_input(["yes_no"])

                    if "yes" in response:
                        move_to_zone('social', proxemics.get_zone()); proxemics.set_distance(1.5)

                        if build_trust():
                            move_to_zone('personal', proxemics.get_zone()); proxemics.set_distance(0.8)
                            head_nod_behavior = "move_head_yesno-173088/behavior_1"
                            if behavior_manager:
                                try:
                                    if behavior_manager.isBehaviorInstalled(head_nod_behavior):
                                        behavior_manager.startBehavior(head_nod_behavior)
                                except Exception: pass

                            if not assess_confusion():
                                game_proposal_text = "Since you seem to enjoy {}, would you like to play a memory game about {}?".format(selected_passion, selected_passion)
                                try:
                                    pepper_cmd.robot.say(game_proposal_text)
                                except AttributeError: print("Pepper (sim) says: \"{}\"".format(game_proposal_text))

                                game_choice_response = get_user_input(["yes_no"])

                                if "yes" in game_choice_response:
                                    # --- GAME LOOP START ---
                                    wave_hello()
                                    game_start_text = "Great! Touch my face and let's play the {} game together.".format(selected_passion)
                                    try:
                                        pepper_cmd.robot.say(game_start_text)
                                    except AttributeError: print("Pepper (sim) says: \"{}\"".format(game_start_text))
                                    reset_arm()

                                    if not game_result_queue.empty():
                                        try:
                                            while not game_result_queue.empty(): game_result_queue.get_nowait()
                                        except Empty: pass

                                    script_dir = os.path.dirname(os.path.abspath(__file__))
                                    html_file_path = os.path.abspath(os.path.join(script_dir, 'index.html'))
                                    browser_opened_successfully = False
                                    print("[Main] Attempting to open game in web browser...")
                                    if not os.path.exists(html_file_path):
                                         print("[Main] CRITICAL ERROR: index.html not found: {}".format(html_file_path))
                                         try: pepper_cmd.robot.say("Oh dear, I seem to have misplaced the game file.")
                                         except AttributeError: print("Pepper (sim) says: \"Oh dear, I seem to have misplaced the game file.\"")
                                    else:
                                        try:
                                            if webbrowser.open(html_file_path, new=2):
                                                browser_opened_successfully = True
                                        except Exception: pass
                                        if not browser_opened_successfully:
                                            try:
                                                game_url_file = ('file:///' if platform.system() == "Windows" else 'file://') + html_file_path.replace('\\', '/')
                                                if webbrowser.open(game_url_file, new=2):
                                                    browser_opened_successfully = True
                                            except Exception: pass
                                        if not browser_opened_successfully:
                                            try: pepper_cmd.robot.say("Let's go!")
                                            except AttributeError: print("Pepper (sim) says: \"I couldn't open the game page automatically, sorry.\"")

                                    print("[Main] Waiting for game result via WebSocket (Timeout: 15 min)...")
                                    game_outcome = None
                                    try:
                                        game_outcome = game_result_queue.get(block=True, timeout=900)
                                        print("[Main] Received game outcome from queue: '{}'".format(game_outcome))
                                    except Empty:
                                        print("[Main] Timed out waiting for game result.")
                                        try: pepper_cmd.robot.say("It looks like the game finished, or we ran out of time. I hope you had fun!")
                                        except AttributeError: print("Pepper (sim) says: \"It looks like the game finished, or we ran out of time. I hope you had fun!\"")
                                    except Exception as e_queue:
                                         print("[Main] Error waiting for game result queue: {}".format(e_queue))
                                         try: pepper_cmd.robot.say("Something went wrong while waiting for the game result.")
                                         except AttributeError: print("Pepper (sim) says: \"Something went wrong while waiting for the game result.\"")

                                    outcome_speech = ""
                                    if game_outcome == "win":
                                        user_wins += 1
                                        outcome_speech = "Yes! You got it! That was a fantastic win for you, {}!".format(selected_name)
                                        if user_wins > pepper_wins and user_wins > 1:
                                            outcome_speech += " You're on a roll!"
                                        elif user_wins == 1 and pepper_wins == 0:
                                            outcome_speech += " What a start!"
                                    elif game_outcome == "lose":
                                        pepper_wins += 1
                                        outcome_speech = "Good try, {}. Looks like I got that one! Don't worry, you'll get the next one!".format(selected_name)
                                        if pepper_wins > user_wins and pepper_wins > 1:
                                            outcome_speech += " I'm getting quite good at this!"
                                    elif game_outcome == "tie":
                                        ties += 1
                                        outcome_speech = "Oh, it's a tie, {}! We both did great. That was a fun challenge!".format(selected_name)

                                    if outcome_speech:
                                        try:
                                            pepper_cmd.robot.say(outcome_speech)
                                        except AttributeError: print("Pepper (sim) says: \"{}\"".format(outcome_speech))

                                    WebSocketServer.send_to_all_clients('score {},{},{}'.format(user_wins, pepper_wins, ties))
                                    time.sleep(2)
                                    move_to_zone('social', proxemics.get_zone())
                                    proxemics.set_distance(1.5)

                                else: # User doesn't want to play
                                    decline_play_text = "Maybe another time then."
                                    try:
                                        pepper_cmd.robot.say(decline_play_text)
                                    except AttributeError: print("Pepper (sim) says: \"{}\"".format(decline_play_text))
                                    move_to_zone('social', proxemics.get_zone())
                                    proxemics.set_distance(1.5)
                            else: # User appears confused
                                confused_text = "Let me get a human assistant for you. I'll step back."
                                try:
                                    pepper_cmd.robot.say(confused_text)
                                except AttributeError: print("Pepper (sim) says: \"{}\"".format(confused_text))
                                move_to_zone('public', proxemics.get_zone())
                                proxemics.set_distance(3.6)
                        else: # Trust not built
                            no_trust_text = "I'll give you some space for now."
                            try:
                                pepper_cmd.robot.say(no_trust_text)
                            except AttributeError: print("Pepper (sim) says: \"{}\"".format(no_trust_text))
                            if proxemics.get_zone() != 'public':
                                move_to_zone('public', proxemics.get_zone())
                                proxemics.set_distance(3.6)
                    else: # User does not want Pepper to approach
                        decline_approach_text = "Okay, I'll stay here. Have a nice day!"
                        try:
                            pepper_cmd.robot.say(decline_approach_text)
                        except AttributeError: print("Pepper (sim) says: \"{}\"".format(decline_approach_text))

                else: # If a name is already set, Pepper is just waiting for the next interaction
                    # This is where Pepper would idle or react to other input / backend signals
                    time.sleep(0.5) # Small sleep to avoid busy-waiting

            except KeyboardInterrupt:
                print("\n[Main] Interaction interrupted by user (Ctrl+C). Shutting down...")
                break # Exit the while loop
            except Exception as e:
                print("\n--- [Main] UNEXPECTED ERROR DURING INTERACTION ---")
                print("    Error Type: {}\n    Error Details: {}".format(type(e).__name__, e))
                import traceback; traceback.print_exc()
                final_error_text = "Oops, something went wrong. I need to stop."
                try:
                    if initial_connection_successful and pepper_cmd.robot: pepper_cmd.robot.say(final_error_text)
                    else: print("Pepper (sim) says: \"{}\"".format(final_error_text))
                except: pass
                break # Exit the while loop on unexpected error

    finally:
        print("Entering cleanup phase...")
        try:
            # Attempt to stop the Tornado IOLoop gracefully
            # This needs to be done on the IOLoop's thread
            tornado.ioloop.IOLoop.current().add_callback(tornado.ioloop.IOLoop.current().stop)
            # Give it a moment to process the stop command
            time.sleep(0.1)

            if initial_connection_successful and 'end' in globals() and callable(end) and end != end_dummy:
                print("Closing Pepper connection...")
                if motion_service:
                    try: motion_service.rest()
                    except Exception as e: print("Error during final rest: {}".format(e))
                end()
        except Exception as e:
            print("Error during final cleanup: {}".format(e))
        time.sleep(1)


if __name__ == "__main__":

    script_dir = os.path.dirname(os.path.abspath(__file__))
    try: os.chdir(script_dir)
    except Exception as e: print("FATAL ERROR: Could not change dir: {}".format(e)); sys.exit(1)

    mimetypes.add_type("text/html", ".html"); mimetypes.add_type("text/css", ".css")
    mimetypes.add_type("application/javascript", ".js")
    mimetypes.add_type("image/jpeg", ".jpg"); mimetypes.add_type("image/jpeg", ".jpeg")
    mimetypes.add_type("image/png", ".png"); mimetypes.add_type("image/gif", ".gif")
    mimetypes.add_type("image/svg+xml", ".svg"); mimetypes.add_type("image/x-icon", ".ico")
    mimetypes.add_type("application/font-woff", ".woff"); mimetypes.add_type("application/font-woff2", ".woff2")
    mimetypes.add_type("application/vnd.ms-fontobject", ".eot"); mimetypes.add_type("application/x-font-ttf", ".ttf")
    mimetypes.add_type("application/json", ".json"); mimetypes.add_type("application/manifest+json", ".webmanifest")
    mimetypes.add_type("text/plain", ".map")

    interaction_flow()