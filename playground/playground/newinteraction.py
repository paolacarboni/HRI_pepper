import os
import sys
import time
import qi # Assuming qi library is Python 2 compatible for your setup
from datetime import datetime
#from game_functions import * # Your commented-out import
sys.path.append(os.getenv('PEPPER_TOOLS_HOME')+'/cmd_server')

import pepper_cmd
from pepper_cmd import *

# --- Tornado and Standard Lib Imports ---
import threading
import webbrowser
try:
    # Python 2 uses Queue module
    from Queue import Queue, Empty
except ImportError:
    # Python 3 uses queue module
    import queue as Queue
    from queue import Empty # Fallback just in case

import tornado.ioloop
import tornado.web
import tornado.websocket
import inspect    # getsourcefile
import os.path
import mimetypes # For guessing file types

# -------------------

motion_service = None

# Queue for communication between web server thread and main thread
# This is necessary for the game communication
game_result_queue = Queue()

# --- Tornado Server Code (Minimal Logging) ---

# Websocket server handler
class WebSocketServer(tornado.websocket.WebSocketHandler):
    clients = set()  # Track connected clients

    def open(self):
        print ('WebSocket connection opened') # Minimal log
        self.clients.add(self)

    def send(self, string): # Kept for potential future use
        if not self.ws_connection: return
        try:
            self.write_message(string)
        except tornado.websocket.WebSocketClosedError:
             pass # Ignore if closed

    def on_message(self, message):
        global game_result_queue # Access the global queue
        # print ("Received from WS:", message) # Optional: uncomment for debugging WS messages
        tokens = message.split()
        if not tokens: return

        command = tokens[0].lower()

        # --- Check only for the 'win' command ---
        if command == "win":
            print ("Received 'win' signal from game!")# Important feedback
            game_result_queue.put('win') # Signal the main thread
        # Ignore other commands from the example (click, age, etc.)

    def on_close(self):
        print ('WebSocket connection closed')# Minimal log
        self.clients.remove(self)

    def check_origin(self, origin):
        # Allow connections from any origin for local development
        return True

# Generic File Handler (Minimal Logging)
class FileHandler(tornado.web.RequestHandler):
    def get(self, fname):
        try:
            source_path = os.path.abspath(inspect.getsourcefile(lambda:0))
            source_dir = os.path.dirname(source_path)
            fname_path = os.path.join(source_dir, fname)

            if not os.path.abspath(fname_path).startswith(source_dir):
                raise tornado.web.HTTPError(403, "Access denied: {}".format(fname))
            if not os.path.isfile(fname_path):
                 raise tornado.web.HTTPError(404, "File not found: {}".format(fname))

            content_type, encoding = mimetypes.guess_type(fname_path)
            if content_type: self.set_header("Content-Type", content_type)
            else: self.set_header("Content-Type", "application/octet-stream")

            with open(fname_path, "rb") as f:
                data = f.read()
                self.write(data)
            self.finish()
        except tornado.web.HTTPError as e:
             self.send_error(e.status_code)
        except Exception as e:
             print "Error serving file {}: {}".format(fname, e) # Log file serving errors
             self.send_error(500)

def make_app():
    return tornado.web.Application([
        (r'/ws', WebSocketServer),
        (r"/(index\.html)", FileHandler),
        (r"/(.*\.(?:html|js|css|jpg|jpeg|png|gif|ico))", FileHandler),
        (r"/images/(.*\.(?:html|js|css|jpg|jpeg|png|gif|ico))", FileHandler),
    ])

# --- Function to run the Tornado server (Minimal Logging) ---
def run_tornado_server():
    """Starts the Tornado IOLoop."""
    try:
        print("Starting web server for game on http://localhost:8888") # Essential info
        app = make_app()
        app.listen(8888)
        tornado.ioloop.IOLoop.current().start()
        # This print is usually not reached until shutdown
        # print "Tornado IOLoop stopped."
    except Exception as e:
        print "[Server Error] Failed to start web server: {}".format(e)


# --- Your Original Pepper Code (Functions restored to original form) ---

TRUST_THRESHOLD = 3

VOCABULARY = {
    "yes_no": ["yes", "no", "not sure"],
    "feelings": ["fine", "good", "bad", "not great", "you too"],
    "locations": ["garden", "my room", "corridor"],
    "game_difficulty": ["very easy", "easy", "medium", "hard", "very hard"],
    "names" : ["giovanni","carlo", "paolo"]
}

USER_DATABASE = {
    "giovanni": {
        "passion": "fruits",
        "greeting": "Ah, Giovanni! I remember you love fruits. Let's play a fruit memory game!"
    },
    "carlo": {
        "passion": "music",
        "greeting": "Hello Carlo! The music lover. We have a fruit memory game for you today!"
    },
    "paolo": {
        "passion": "gardening",
        "greeting": "Paolo! The gardening enthusiast. How about a fruit matching game?"
    }
}



class ProxemicsSimulator:
    ZONES = {
        'intimate': (0, 0.45),
        'personal': (0.45, 1.2),
        'social': (1.2, 3.6),
        'public': (3.6, float('inf'))
    }

    def __init__(self):
        self.current_distance = 4.0
        self.trust_level = 0

    def set_distance(self, distance):
        self.current_distance = distance

    def get_zone(self):
        for zone, (min_dist, max_dist) in self.ZONES.items():
            if float(min_dist) <= float(self.current_distance) < float(max_dist):
                return zone
        return 'public'

    def is_too_close(self):
        return float(self.current_distance) < float(self.ZONES['personal'][0])

def move_forward(distance):
    # Minimal printing - just log errors
    try:
        motion_service = pepper_cmd.robot.session.service("ALMotion")
        motion_service.moveTo(distance, 0, 0)
        time.sleep(1)
    except Exception as e:
        print("Error during move_forward: {}".format(e))


def move_to_zone(target_zone, current_zone):
    # Minimal printing - just log errors or invalid states
    zone_distances = {'public': 3.6, 'social': 1.5, 'personal': 0.8, 'intimate': 0.3}
    target_distance = zone_distances.get(target_zone)
    current_dist = zone_distances.get(current_zone)
    if target_distance is None or current_dist is None:
        print("Error: Invalid zone provided for move_to_zone.")
        return
    movement = float(current_dist) - float(target_distance)
    if abs(movement) > 0.05:
        move_forward(movement)
    # No success prints

# --- THIS IS YOUR ORIGINAL INPUT FUNCTION ---
def get_user_input(categories=None):
    """Reads input from the terminal, performs basic validation"""
    while True:
        try:
            # Use raw_input() for Python 2
            response = raw_input("Your response: ").strip().lower() # Simple prompt

            if not response: # Handle empty input
                print("I didn't catch that. Please try again.") # Use Pepper-like voice
                continue

            if categories:
                matched = False
                # Check each category's keywords
                for category in categories:
                    for keyword in VOCABULARY.get(category, []):
                        if keyword in response:
                            return keyword # Return the standardized keyword
                # If no keywords matched in specified categories
                if not matched:
                    print("I didn't understand that. Could you please rephrase? (Expected: {})".format(', '.join(c for c in categories)))
                    # Provide hint about expected categories
            else: # No filtering, return raw input
                return response

        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            sys.exit(0)
        except Exception as e:
            print("An error occurred reading input: {}".format(e))
            sys.exit(1)
# --- END OF YOUR ORIGINAL INPUT FUNCTION ---

def wave_hello():
    # Minimal printing - just log errors
    try:
        motion_service = pepper_cmd.robot.session.service("ALMotion")
        motion_service.wakeUp()
        motion_service.setStiffnesses("RArm", 1.0)
        names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]
        angles = [0.0, -0.2, 1.0, 1.0, 0.0]
        times = [1.0, 1.0, 1.0, 1.0, 1.0]
        motion_service.angleInterpolation(names, angles, times, True)
        # motion_service.setStiffnesses("RArm", 0.0) # Done in reset_arm
    except Exception as e:
        print("Error during wave_hello: {}".format(e))

def reset_arm():
    # Minimal printing - just log errors
    try:
        motion_service = pepper_cmd.robot.session.service("ALMotion")
        motion_service.setStiffnesses("RArm", 1.0)
        names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]
        angles = [1.5, -0.2, 1.0, 0.5, 0.0]
        times = [1.0, 1.0, 1.0, 1.0, 1.0]
        motion_service.angleInterpolation(names, angles, times, True)
        motion_service.setStiffnesses("RArm", 0.0)
    except Exception as e:
        print("Error during reset_arm: {}".format(e))


def say(text):
    """Wrapper for Pepper saying something, prints to console"""
    print("Pepper says: {}".format(text)) # This IS the intended output
    try:
        pepper_cmd.robot.say(text)
    except Exception as e:
        print("Error during pepper_cmd.robot.say: {}".format(e))


def assess_confusion():
    # Uses say() and get_user_input() - no extra prints needed
    questions = [
        "Do you know what day it is today?",
        "Can you tell me where we are right now?",
        "Do you remember my name?"
    ]
    confusion_score = 0
    for q in questions:
        say(q)
        response = get_user_input(["locations", "yes_no"])
        if "not sure" in response or "no" in response:
            confusion_score += 1
        time.sleep(1)
    return confusion_score > 1 # Return boolean

def build_trust():
    # Uses say() and get_user_input() - no extra prints needed
    trust_points = 0
    greetings = [
        "Is it a good day?",
        "It's nice to meet you today.",
        "How are you feeling right now?"
    ]
    for greeting in greetings:
        say(greeting)
        response = get_user_input(["feelings", "yes_no"])
        if response in VOCABULARY["feelings"] or response in VOCABULARY["yes_no"]:
             trust_points += 1
        # Keep the empathetic responses
        if response in ["bad", "not great"]:
            say("I'm sorry to hear that. I hope I can help!")
        elif response in ["fine", "good", "you too"]:
             say("Happy to hear that!")
        time.sleep(1)
    return trust_points >= TRUST_THRESHOLD # Return boolean


# --- Main Interaction Flow (Minimal Prints, uses original functions) ---
def interaction_flow():
    # Start the Tornado server thread
    server_thread = threading.Thread(target=run_tornado_server)
    server_thread.daemon = True
    server_thread.start()
    time.sleep(2) # Allow server to start

    # Define dummy begin/end initially
    def begin_dummy(): pass
    def end_dummy(): pass
    global begin, end
    global selected_passion
    begin = begin_dummy
    end = end_dummy

    try:
        # --- Pepper Connection (Minimal Prints) ---
        try:
            # print("Attempting Pepper connection...") # Optional log
            pepper_cmd.begin()
            begin = pepper_cmd.begin
            end = pepper_cmd.end
            # print("Pepper connection successful.") # Optional log
            global motion_service
            motion_service = pepper_cmd.robot.session.service("ALMotion")
        except Exception as e:
            print("Warning: Could not connect to Pepper robot/simulator: {}".format(e))
            print("Proceeding in simulation mode without robot movement/speech.")
            motion_service = None
        # --- End Pepper Connection ---

        proxemics = ProxemicsSimulator() # Your simulator class

        # --- Behavior Manager (No changes needed - uses Dummy if fails) ---
        try:
             if pepper_cmd.robot and pepper_cmd.robot.session:
                 behavior_manager = pepper_cmd.robot.session.service("ALBehaviorManager")
             else: raise Exception("Robot session not available")
        except Exception:
             print("Warning: Could not access ALBehaviorManager. Simulating behaviors.")
             class DummyBehaviorManager:
                 def isBehaviorInstalled(self, name): return True
                 def startBehavior(self, name): pass # Do nothing, just simulate
             behavior_manager = DummyBehaviorManager()
        # --- End Behavior Manager ---

        print("\n=== Starting Interaction ===") # Your original start message?
        proxemics.set_distance(4.0)
        # print("Current zone:", proxemics.get_zone()) # Removed extra print

        wave_hello()
        say("Hello there! May I approach you?") # Uses say()
        reset_arm()
        response = get_user_input(["yes_no"]) # Uses get_user_input()

        if "yes" in response:
            move_to_zone('social', proxemics.get_zone())
            proxemics.set_distance(1.5)
            # print("Current zone:", proxemics.get_zone()) # Removed extra print

            say("What's your name?")
            response = get_user_input(["names"])

        if response in USER_DATABASE:
            selected_passion = USER_DATABASE[response]["passion"]
            selected_greeting = USER_DATABASE[response]["greeting"]
            print("Selected passion: {selected_passion}")

            # Send the passion via WebSocket
            try:
                for handler in WebSocketServer.clients:
                    handler.write_message(json.dumps({
                        'type': 'passion',
                        'value': selected_passion
                    }))
                print("Sent passion '{selected_passion}' to WebSocket clients")
            except Exception as e:
                print("Error sending passion via WebSocket:", e)


           # ws_handler.send(selected_passion)

            if build_trust(): # Uses build_trust()
                # print("Trust established.") # Removed extra print
                move_to_zone('personal', proxemics.get_zone())
                proxemics.set_distance(0.8)
                # print("Current zone:", proxemics.get_zone()) # Removed extra print

                behavior_name = "move_head_yesno-173088/behavior_1"
                if behavior_manager.isBehaviorInstalled(behavior_name):
                    behavior_manager.startBehavior(behavior_name)
                    # print("Game behavior started!") # Removed extra print
                #else:
                    # print("Game behavior not found!") # Removed extra print

                if not assess_confusion(): # Uses assess_confusion()
                    # print("User appears oriented") # Removed extra print
                    say("Would you like to play a memory game?") # Uses say()
                    response = get_user_input(["yes_no"]) # Uses get_user_input()

                    if "yes" in response:
                        # print("\n=== STARTING GAME ===") # Removed extra print
                        wave_hello() # Wave again before game starts
                        say("Great! Let's play the game.") # Uses say()

                        # --- Open the web browser (Tornado serves on 8888) ---
                        game_url = 'http://localhost:8888/'
                        try:
                            webbrowser.open(game_url, new=2)
                        except Exception as e:
                            print("Error opening web browser: {}".format(e))
                            say("I couldn't open the game automatically, sorry.")

                        # --- Wait for game result from WebSocket via Queue ---
                        # say("Let me know how you do! I'll be waiting.") # Optional line
                        print("Waiting for game result...") # Simple status
                        game_outcome = None
                        try:
                            game_outcome = game_result_queue.get(timeout=900) # 15 min timeout
                        except Empty:
                            print("Timed out waiting for game result.")
                            say("It looks like the game finished or maybe something went wrong.")
                        except Exception as e:
                             print("Error waiting for game queue: {}".format(e))

                        # --- React to game result ---
                        if game_outcome == "win":
                            # **** THE DESIRED REACTION ****
                            say("Oh wow! You are very strong!") # Uses say()
                            # ******************************
                        else:
                            # Optional: Add reactions for lose/tie
                            # print("Game finished.") # Removed extra print
                            say("Good game!") # Uses say()

                        time.sleep(3)
                        move_to_zone('social', proxemics.get_zone())
                        proxemics.set_distance(1.5)
                        # print("Current zone:", proxemics.get_zone()) # Removed extra print

                    else: # User doesn't want to play
                        say("Maybe another time then.") # Uses say()
                        move_to_zone('social', proxemics.get_zone())
                else: # User appears confused
                    say("Let me get a human assistant for you.") # Uses say()
                    move_to_zone('public', proxemics.get_zone())
            else: # Trust not built
                say("I'll give you some space.") # Uses say()
                move_to_zone('public', proxemics.get_zone())
        else: # User does not want Pepper to approach
            say("Okay, I'll stay here.") # Uses say()

        reset_arm() # Reset arm at the end of interaction branches

    except KeyboardInterrupt:
        print("\nInteraction interrupted by user.") # Minimal exit message
        try: tornado.ioloop.IOLoop.current().stop() # Try to stop server
        except: pass
    except Exception as e:
        print("\nAn error occurred during interaction: {}".format(e)) # Log fatal errors
        import traceback
        traceback.print_exc()
    finally:
        # Ensure Pepper connection is closed
        try:
            # print("Ending Pepper connection...") # Optional log
            end()
        except NameError: pass
        except Exception as e: print("Error closing Pepper connection: {}".format(e))

        print("=== Interaction Complete ===") # Your original end message?


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    # print("Running script from directory: {}".format(script_dir)) # Optional log
    # print("Ensure game files (index.html, etc.) are here.") # Optional log
    print("Starting Pepper interaction script (Python 2 / Tornado).")

    # Add common image types to mimetypes
    #mimetypes.add_type("text/css", ".css")
    #mimetypes.add_type("application/javascript", ".js")
    #mimetypes.add_type("image/jpeg", ".jpg"); mimetypes.add_type("image/jpeg", ".jpeg")
    #mimetypes.add_type("image/png", ".png"); mimetypes.add_type("image/gif", ".gif")
    mimetypes.add_type("text/css", ".css")
    mimetypes.add_type("application/javascript", ".js")
    mimetypes.add_type("image/jpeg", ".jpg")
    mimetypes.add_type("image/jpeg", ".jpeg") # Add .jpeg just in case

    interaction_flow()