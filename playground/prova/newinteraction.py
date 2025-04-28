import json
import os
import sys
import time
import qi 
from datetime import datetime
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
game_result_queue = Queue()

# Global variable to hold the passion identified during interaction
# Needs to be accessible by the WebSocket handler when a connection opens
selected_passion = None # Initialize as None

# --- Tornado Server Code

# Websocket server handler
class WebSocketServer(tornado.websocket.WebSocketHandler):
    # Store clients if needed for broadcasting, but not strictly necessary for this theme setup
    clients = set()

    def open(self):
        print ('WebSocket connection opened') # Minimal log
        WebSocketServer.clients.add(self)
        global selected_passion # Access the global variable

        # --- SEND THEME IMMEDIATELY ON CONNECTION ---
        if selected_passion: # Only send if passion has been determined
            theme_message = "theme {}".format(selected_passion)
            print("Sending theme to client: {}".format(theme_message))
            try:
                self.write_message(theme_message)
            except Exception as e:
                print("Error sending theme message: {}".format(e))
        else:
            print("Warning: WebSocket opened, but selected_passion is not yet set.")
            # Optionally send a default or wait message?
            # self.write_message("theme default") # Or similar if you have default images
        # --- END SEND THEME ---

    def send(self, string): 

        try:
            self.write_message(string)
        except tornado.websocket.WebSocketClosedError:
             pass # Ignore if closed
        except AttributeError:
             print("Warning: Tried to send via send() but connection might not be ready.")


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
        WebSocketServer.clients.remove(self)


    def check_origin(self, origin):
        # Allow connections from any origin for local development
        return True

# Generic File Handler 
class FileHandler(tornado.web.RequestHandler):
    def get(self, fname):
        try:
            source_path = os.path.abspath(inspect.getsourcefile(lambda:0))
            source_dir = os.path.dirname(source_path)
            # Construct path relative to the script directory
            fname_path = os.path.abspath(os.path.join(source_dir, fname)) # Use abspath for safety

            # Security check: Ensure the requested path is within the source directory
            if not fname_path.startswith(source_dir):
                raise tornado.web.HTTPError(403, "Access denied: {}".format(fname))

            if not os.path.isfile(fname_path):
                 # Try adding 'images/' prefix if not found directly (for image paths)
                 img_path = os.path.abspath(os.path.join(source_dir, 'images', fname))
                 if fname.startswith('images/') and os.path.isfile(img_path):
                      fname_path = img_path
                 elif os.path.isfile(os.path.join(source_dir, 'images/fruit_images', fname.split('/')[-1])): # Quick check for fruits subdir
                     fname_path = os.path.join(source_dir, 'images/fruit_images', fname.split('/')[-1])
                 elif os.path.isfile(os.path.join(source_dir, 'images/music_images', fname.split('/')[-1])): # Quick check for music subdir
                     fname_path = os.path.join(source_dir, 'images/music_images', fname.split('/')[-1])
                 elif os.path.isfile(os.path.join(source_dir, 'images/gardening_images', fname.split('/')[-1])): # Quick check for gardening subdir
                     fname_path = os.path.join(source_dir, 'images/gardening_images', fname.split('/')[-1])
                 else:
                     raise tornado.web.HTTPError(404, "File not found: {}".format(fname))


            content_type, encoding = mimetypes.guess_type(fname_path)
            if content_type: self.set_header("Content-Type", content_type)
            else: self.set_header("Content-Type", "application/octet-stream") # Default if type unknown

            with open(fname_path, "rb") as f:
                data = f.read()
                self.write(data)
            self.finish()
        except tornado.web.HTTPError as e:
             self.send_error(e.status_code)
             print("HTTP Error {} serving file {}: {}".format(e.status_code, fname, e.log_message))
        except Exception as e:
             print "Error serving file {}: {}".format(fname, e) # Log file serving errors
             self.send_error(500)

def make_app():
    # Define routes - ensure image paths are handled
    # The (.*) captures the full path requested by the browser
    return tornado.web.Application([
        (r'/ws', WebSocketServer),
        (r"/(index\.html)", FileHandler, {'path': '.'}), # Serve index.html from root
        (r"/(script\.js)", FileHandler, {'path': '.'}),   # Serve script.js from root
        (r"/(style\.css)", FileHandler, {'path': '.'}),   # Serve style.css from root
        # Catch-all for other files, including those in subdirectories like 'images'
        (r"/(.*\.(?:js|css|jpg|jpeg|png|gif|ico))", FileHandler, {'path': '.'}),
    ],

    )


# --- Function to run the Tornado server ---
def run_tornado_server():
    """Starts the Tornado IOLoop."""
    try:
        # Ensure we're serving from the script's directory for relative paths
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        print("Starting web server for game on http://localhost:8888") # Essential info
        print("Serving files from: {}".format(script_dir))
        app = make_app()
        app.listen(8888)
        tornado.ioloop.IOLoop.current().start()
        # This print is usually not reached until shutdown
        # print "Tornado IOLoop stopped."
    except Exception as e:
        print "[Server Error] Failed to start web server: {}".format(e)



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
        "greeting": "Hello Carlo! The music lover. We have a music memory game for you today!" # Updated greeting
    },
    "paolo": {
        "passion": "gardening",
        "greeting": "Paolo! The gardening enthusiast. How about a gardening matching game?" # Updated greeting
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
    # ... (move_forward code remains the same) ...
    try:
        motion_service = pepper_cmd.robot.session.service("ALMotion")
        motion_service.moveTo(distance, 0, 0)
        time.sleep(1)
    except Exception as e:
        print("Error during move_forward: {}".format(e))


def move_to_zone(target_zone, current_zone):
    # ... (move_to_zone code remains the same) ...
    zone_distances = {'public': 3.6, 'social': 1.5, 'personal': 0.8, 'intimate': 0.3}
    target_distance = zone_distances.get(target_zone)
    current_dist = zone_distances.get(current_zone)
    if target_distance is None or current_dist is None:
        print("Error: Invalid zone provided for move_to_zone.")
        return
    movement = float(current_dist) - float(target_distance)
    if abs(movement) > 0.05:
        move_forward(movement)

def get_user_input(categories=None):
    # ... (get_user_input code remains the same) ...
    while True:
        try:
            response = raw_input("Your response: ").strip().lower()
            if not response:
                print("I didn't catch that. Please try again.")
                continue
            if categories:
                matched = False
                for category in categories:
                    for keyword in VOCABULARY.get(category, []):
                        if keyword in response:
                            return keyword
                if not matched:
                    print("I didn't understand that. Could you please rephrase? (Expected: {})".format(', '.join(c for c in categories)))
            else:
                return response
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            sys.exit(0)
        except Exception as e:
            print("An error occurred reading input: {}".format(e))
            sys.exit(1)

def wave_hello():
    # ... (wave_hello code remains the same) ...
    try:
        motion_service = pepper_cmd.robot.session.service("ALMotion")
        motion_service.wakeUp()
        motion_service.setStiffnesses("RArm", 1.0)
        names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]
        angles = [0.0, -0.2, 1.0, 1.0, 0.0]
        times = [1.0, 1.0, 1.0, 1.0, 1.0]
        motion_service.angleInterpolation(names, angles, times, True)
    except Exception as e:
        print("Error during wave_hello: {}".format(e))

def reset_arm():
    # ... (reset_arm code remains the same) ...
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
    # ... (say code remains the same) ...
    print("Pepper says: {}".format(text))
    try:
        pepper_cmd.robot.say(text)
    except Exception as e:
        print("Error during pepper_cmd.robot.say: {}".format(e))


def assess_confusion():
    # ... (assess_confusion code remains the same) ...
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
    return confusion_score > 1

def build_trust():
    # ... (build_trust code remains the same) ...
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
        if response in ["bad", "not great"]:
            say("I'm sorry to hear that. I hope I can help!")
        elif response in ["fine", "good", "you too"]:
             say("Happy to hear that!")
        time.sleep(1)
    return trust_points >= TRUST_THRESHOLD

# --- Main Interaction Flow  ---
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
    # **** Make selected_passion global ****
    global selected_passion
    begin = begin_dummy
    end = end_dummy

    try:
        # --- Pepper Connection ---
        try:
            pepper_cmd.begin()
            begin = pepper_cmd.begin
            end = pepper_cmd.end
            global motion_service
            motion_service = pepper_cmd.robot.session.service("ALMotion")
        except Exception as e:
            print("Warning: Could not connect to Pepper robot/simulator: {}".format(e))
            print("Proceeding in simulation mode without robot movement/speech.")
            motion_service = None
        # --- End Pepper Connection ---

        proxemics = ProxemicsSimulator()

        # --- Behavior Manager (No changes needed) ---
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

        print("\n=== Starting Interaction ===")
        proxemics.set_distance(4.0)

        wave_hello()
        say("Hello there! May I approach you?")
        reset_arm()
        response = get_user_input(["yes_no"])

        if "yes" in response:
            move_to_zone('social', proxemics.get_zone())
            proxemics.set_distance(1.5)

            say("What's your name?")
            user_name = get_user_input(["names"]) # Store name

            # **** Set the global selected_passion ****
            if user_name in USER_DATABASE:
                selected_passion = USER_DATABASE[user_name]["passion"]
                selected_greeting = USER_DATABASE[user_name]["greeting"]
                print("Identified user: {}, Passion: {}".format(user_name, selected_passion)) # Log
                say(selected_greeting) # Use the specific greeting
            else:
                # Handle unknown user - maybe assign a default passion or ask?
                selected_passion = "fruits" # Default to fruits if name not found
                print("User '{}' not in database. Defaulting passion to '{}'".format(user_name, selected_passion))
                say("Hello {}! Nice to meet you. We have a fruit memory game today.".format(user_name))

            if build_trust():
                move_to_zone('personal', proxemics.get_zone())
                proxemics.set_distance(0.8)

                # ... (rest of the behavior starting logic remains the same) ...
                behavior_name = "move_head_yesno-173088/behavior_1"
                if behavior_manager.isBehaviorInstalled(behavior_name):
                    try:
                        behavior_manager.startBehavior(behavior_name)
                    except Exception as e:
                        print("Error starting behavior {}: {}".format(behavior_name, e))


                if not assess_confusion():
                    # Ask based on the determined passion
                    say("Since you like {}, would you like to play a {} memory game?".format(selected_passion, selected_passion))
                    response = get_user_input(["yes_no"])

                    if "yes" in response:
                        wave_hello()
                        say("Great! Let's play the {} game.".format(selected_passion))

                        # --- Open the web browser ---
                        # Ensure the path is correct for your system
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        # Use file:// URI scheme for local files
                        game_url = 'file://' + os.path.join(script_dir, 'index.html')
                        print("Opening game URL: {}".format(game_url))

                        try:
                            webbrowser.open(game_url, new=2) # new=2 opens in a new tab if possible
                        except Exception as e:
                            print("Error opening web browser: {}".format(e))
                            say("I couldn't open the game automatically, sorry.")

                        # --- Wait for game result ---
                        print("Waiting for game result...")
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
                            say("Oh wow! You are very strong!")
                        else:
                            say("Good game!")

                        time.sleep(3)
                        move_to_zone('social', proxemics.get_zone())
                        proxemics.set_distance(1.5)

                    else: # User doesn't want to play
                        say("Maybe another time then.")
                        move_to_zone('social', proxemics.get_zone())
                else: # User appears confused
                    say("Let me get a human assistant for you.")
                    move_to_zone('public', proxemics.get_zone())
            else: # Trust not built
                say("I'll give you some space.")
                move_to_zone('public', proxemics.get_zone())
        else: # User does not want Pepper to approach
            say("Okay, I'll stay here.")

        reset_arm()

    except KeyboardInterrupt:
        print("\nInteraction interrupted by user.")
        try: tornado.ioloop.IOLoop.current().stop()
        except: pass
    except Exception as e:
        print("\nAn error occurred during interaction: {}".format(e))
        import traceback
        traceback.print_exc()
    finally:
        # Ensure Pepper connection is closed
        try:
            end()
        except NameError: pass
        except Exception as e: print("Error closing Pepper connection: {}".format(e))

        # Stop Tornado IOLoop if it's still running
        try:
            if tornado.ioloop.IOLoop.current(instance=False):
                 tornado.ioloop.IOLoop.current().stop()
                 print("Tornado IOLoop stopped.")
        except Exception as e:
             print("Error stopping Tornado: {}".format(e))


        print("=== Interaction Complete ===")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir) # Change working directory to script dir
    print("Running script from directory: {}".format(script_dir))
    print("Ensure game files (index.html, script.js, style.css, images/) are here.")
    print("Starting Pepper interaction script (Python 2 / Tornado).")

    # Add common image types to mimetypes
    mimetypes.add_type("text/css", ".css")
    mimetypes.add_type("application/javascript", ".js")
    mimetypes.add_type("image/jpeg", ".jpg"); mimetypes.add_type("image/jpeg", ".jpeg")
    mimetypes.add_type("image/png", ".png"); mimetypes.add_type("image/gif", ".gif")
    mimetypes.add_type("image/x-icon", ".ico") # Add favicon type

    interaction_flow()
