# import json
# import os
# import sys
# import time
# import qi # Assuming qi library is Python 2 compatible for your setup
# from datetime import datetime
# #from game_functions import * # Your commented-out import
# sys.path.append(os.getenv('PEPPER_TOOLS_HOME')+'/cmd_server')

# import pepper_cmd
# from pepper_cmd import *

# # --- Tornado and Standard Lib Imports ---
# import threading
# import webbrowser
# try:
#     # Python 2 uses Queue module
#     from Queue import Queue, Empty
# except ImportError:
#     # Python 3 uses queue module
#     import queue as Queue
#     from queue import Empty # Fallback just in case

# import tornado.ioloop
# import tornado.web
# import tornado.websocket
# import inspect    # getsourcefile
# import os.path
# import mimetypes # For guessing file types

# # -------------------

# motion_service = None

# # Queue for communication between web server thread and main thread
# game_result_queue = Queue()

# # Global variable to hold the passion identified during interaction
# # Needs to be accessible by the WebSocket handler when a connection opens
# selected_passion = None # Initialize as None

# # --- Tornado Server Code (Minimal Logging) ---

# # Websocket server handler
# class WebSocketServer(tornado.websocket.WebSocketHandler):
#     # Store clients if needed for broadcasting, but not strictly necessary for this theme setup
#     clients = set()

#     def open(self):
#         print ('WebSocket connection opened') # Minimal log
#         WebSocketServer.clients.add(self)
#         global selected_passion # Access the global variable

#         # --- SEND THEME IMMEDIATELY ON CONNECTION ---
#         if selected_passion: # Only send if passion has been determined
#             theme_message = "theme {}".format(selected_passion)
#             print("Sending theme to client: {}".format(theme_message))
#             try:
#                 self.write_message(theme_message)
#             except Exception as e:
#                 print("Error sending theme message: {}".format(e))
#         else:
#             print("Warning: WebSocket opened, but selected_passion is not yet set.")
#             # Optionally send a default or wait message?
#             # self.write_message("theme default") # Or similar if you have default images
#         # --- END SEND THEME ---

#     def send(self, string): # Kept for potential future use
#         # Check ws_connection attribute if you intend to use this send method
#         # For now, using self.write_message directly in open/on_message is fine
#         try:
#             self.write_message(string)
#         except tornado.websocket.WebSocketClosedError:
#              pass # Ignore if closed
#         except AttributeError:
#              print("Warning: Tried to send via send() but connection might not be ready.")


#     def on_message(self, message):
#         global game_result_queue # Access the global queue
#         # print ("Received from WS:", message) # Optional: uncomment for debugging WS messages
#         tokens = message.split()
#         if not tokens: return

#         command = tokens[0].lower()

#         # --- Check only for the 'win' command ---
#         if command == "win":
#             print ("Received 'win' signal from game!")# Important feedback
#             game_result_queue.put('win') # Signal the main thread
#         # Ignore other commands from the example (click, age, etc.)

#     def on_close(self):
#         print ('WebSocket connection closed')# Minimal log
#         WebSocketServer.clients.remove(self)


#     def check_origin(self, origin):
#         # Allow connections from any origin for local development
#         return True

# # Generic File Handler (Minimal Logging)
# class FileHandler(tornado.web.RequestHandler):
#     def get(self, fname):
#         try:
#             source_path = os.path.abspath(inspect.getsourcefile(lambda:0))
#             source_dir = os.path.dirname(source_path)
#             # Construct path relative to the script directory
#             fname_path = os.path.abspath(os.path.join(source_dir, fname)) # Use abspath for safety

#             # Security check: Ensure the requested path is within the source directory
#             if not fname_path.startswith(source_dir):
#                 raise tornado.web.HTTPError(403, "Access denied: {}".format(fname))

#             if not os.path.isfile(fname_path):
#                  # Try adding 'images/' prefix if not found directly (for image paths)
#                  img_path = os.path.abspath(os.path.join(source_dir, 'images', fname))
#                  if fname.startswith('images/') and os.path.isfile(img_path):
#                       fname_path = img_path
#                  elif os.path.isfile(os.path.join(source_dir, 'images/fruit_images', fname.split('/')[-1])): # Quick check for fruits subdir
#                      fname_path = os.path.join(source_dir, 'images/fruit_images', fname.split('/')[-1])
#                  elif os.path.isfile(os.path.join(source_dir, 'images/music_images', fname.split('/')[-1])): # Quick check for music subdir
#                      fname_path = os.path.join(source_dir, 'images/music_images', fname.split('/')[-1])
#                  elif os.path.isfile(os.path.join(source_dir, 'images/gardening_images', fname.split('/')[-1])): # Quick check for gardening subdir
#                      fname_path = os.path.join(source_dir, 'images/gardening_images', fname.split('/')[-1])
#                  else:
#                      raise tornado.web.HTTPError(404, "File not found: {}".format(fname))


#             content_type, encoding = mimetypes.guess_type(fname_path)
#             if content_type: self.set_header("Content-Type", content_type)
#             else: self.set_header("Content-Type", "application/octet-stream") # Default if type unknown

#             with open(fname_path, "rb") as f:
#                 data = f.read()
#                 self.write(data)
#             self.finish()
#         except tornado.web.HTTPError as e:
#              self.send_error(e.status_code)
#              print("HTTP Error {} serving file {}: {}".format(e.status_code, fname, e.log_message))
#         except Exception as e:
#              print "Error serving file {}: {}".format(fname, e) # Log file serving errors
#              self.send_error(500)

# def make_app():
#     # Define routes - ensure image paths are handled
#     # The (.*) captures the full path requested by the browser
#     return tornado.web.Application([
#         (r'/ws', WebSocketServer),
#         (r"/(index\.html)", FileHandler, {'path': '.'}), # Serve index.html from root
#         (r"/(script\.js)", FileHandler, {'path': '.'}),   # Serve script.js from root
#         (r"/(style\.css)", FileHandler, {'path': '.'}),   # Serve style.css from root
#         # Catch-all for other files, including those in subdirectories like 'images'
#         (r"/(.*\.(?:js|css|jpg|jpeg|png|gif|ico))", FileHandler, {'path': '.'}),
#     ],
#     # Optional: define static path if files are organized differently
#     # static_path=os.path.join(os.path.dirname(__file__), 'static'),
#     # debug=True # Useful for development
#     )


# # --- Function to run the Tornado server (Minimal Logging) ---
# def run_tornado_server():
#     """Starts the Tornado IOLoop."""
#     try:
#         # Ensure we're serving from the script's directory for relative paths
#         script_dir = os.path.dirname(os.path.abspath(__file__))
#         os.chdir(script_dir)
#         print("Starting web server for game on http://localhost:8888") # Essential info
#         print("Serving files from: {}".format(script_dir))
#         app = make_app()
#         app.listen(8888)
#         tornado.ioloop.IOLoop.current().start()
#         # This print is usually not reached until shutdown
#         # print "Tornado IOLoop stopped."
#     except Exception as e:
#         print "[Server Error] Failed to start web server: {}".format(e)


# # --- Your Original Pepper Code (Functions restored to original form) ---

# TRUST_THRESHOLD = 3

# VOCABULARY = {
#     "yes_no": ["yes", "no", "not sure"],
#     "feelings": ["fine", "good", "bad", "not great", "you too"],
#     "locations": ["garden", "my room", "corridor"],
#     "game_difficulty": ["very easy", "easy", "medium", "hard", "very hard"],
#     "names" : ["giovanni","carlo", "paolo"]
# }

# USER_DATABASE = {
#     "giovanni": {
#         "passion": "fruits",
#         "greeting": "Ah, Giovanni! I remember you love fruits. Let's play a fruit memory game!"
#     },
#     "carlo": {
#         "passion": "music",
#         "greeting": "Hello Carlo! The music lover. We have a music memory game for you today!" # Updated greeting
#     },
#     "paolo": {
#         "passion": "gardening",
#         "greeting": "Paolo! The gardening enthusiast. How about a gardening matching game?" # Updated greeting
#     }
# }


# class ProxemicsSimulator:
#     # ... (ProxemicsSimulator code remains the same) ...
#     ZONES = {
#         'intimate': (0, 0.45),
#         'personal': (0.45, 1.2),
#         'social': (1.2, 3.6),
#         'public': (3.6, float('inf'))
#     }

#     def __init__(self):
#         self.current_distance = 4.0
#         self.trust_level = 0

#     def set_distance(self, distance):
#         self.current_distance = distance

#     def get_zone(self):
#         for zone, (min_dist, max_dist) in self.ZONES.items():
#             if float(min_dist) <= float(self.current_distance) < float(max_dist):
#                 return zone
#         return 'public'

#     def is_too_close(self):
#         return float(self.current_distance) < float(self.ZONES['personal'][0])

# def move_forward(distance):
#     # ... (move_forward code remains the same) ...
#     try:
#         motion_service = pepper_cmd.robot.session.service("ALMotion")
#         motion_service.moveTo(distance, 0, 0)
#         time.sleep(1)
#     except Exception as e:
#         print("Error during move_forward: {}".format(e))


# def move_to_zone(target_zone, current_zone):
#     # ... (move_to_zone code remains the same) ...
#     zone_distances = {'public': 3.6, 'social': 1.5, 'personal': 0.8, 'intimate': 0.3}
#     target_distance = zone_distances.get(target_zone)
#     current_dist = zone_distances.get(current_zone)
#     if target_distance is None or current_dist is None:
#         print("Error: Invalid zone provided for move_to_zone.")
#         return
#     movement = float(current_dist) - float(target_distance)
#     if abs(movement) > 0.05:
#         move_forward(movement)

# def get_user_input(categories=None):
#     # ... (get_user_input code remains the same) ...
#     while True:
#         try:
#             response = raw_input("Your response: ").strip().lower()
#             if not response:
#                 print("I didn't catch that. Please try again.")
#                 continue
#             if categories:
#                 matched = False
#                 for category in categories:
#                     for keyword in VOCABULARY.get(category, []):
#                         if keyword in response:
#                             return keyword
#                 if not matched:
#                     print("I didn't understand that. Could you please rephrase? (Expected: {})".format(', '.join(c for c in categories)))
#             else:
#                 return response
#         except (EOFError, KeyboardInterrupt):
#             print("\nExiting...")
#             sys.exit(0)
#         except Exception as e:
#             print("An error occurred reading input: {}".format(e))
#             sys.exit(1)

# def wave_hello():
#     # ... (wave_hello code remains the same) ...
#     try:
#         motion_service = pepper_cmd.robot.session.service("ALMotion")
#         motion_service.wakeUp()
#         motion_service.setStiffnesses("RArm", 1.0)
#         names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]
#         angles = [0.0, -0.2, 1.0, 1.0, 0.0]
#         times = [1.0, 1.0, 1.0, 1.0, 1.0]
#         motion_service.angleInterpolation(names, angles, times, True)
#     except Exception as e:
#         print("Error during wave_hello: {}".format(e))

# def reset_arm():
#     # ... (reset_arm code remains the same) ...
#     try:
#         motion_service = pepper_cmd.robot.session.service("ALMotion")
#         motion_service.setStiffnesses("RArm", 1.0)
#         names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]
#         angles = [1.5, -0.2, 1.0, 0.5, 0.0]
#         times = [1.0, 1.0, 1.0, 1.0, 1.0]
#         motion_service.angleInterpolation(names, angles, times, True)
#         motion_service.setStiffnesses("RArm", 0.0)
#     except Exception as e:
#         print("Error during reset_arm: {}".format(e))


# def say(text):
#     # ... (say code remains the same) ...
#     print("Pepper says: {}".format(text))
#     try:
#         pepper_cmd.robot.say(text)
#     except Exception as e:
#         print("Error during pepper_cmd.robot.say: {}".format(e))


# def assess_confusion():
#     # ... (assess_confusion code remains the same) ...
#     questions = [
#         "Do you know what day it is today?",
#         "Can you tell me where we are right now?",
#         "Do you remember my name?"
#     ]
#     confusion_score = 0
#     for q in questions:
#         say(q)
#         response = get_user_input(["locations", "yes_no"])
#         if "not sure" in response or "no" in response:
#             confusion_score += 1
#         time.sleep(1)
#     return confusion_score > 1

# def build_trust():
#     # ... (build_trust code remains the same) ...
#     trust_points = 0
#     greetings = [
#         "Is it a good day?",
#         "It's nice to meet you today.",
#         "How are you feeling right now?"
#     ]
#     for greeting in greetings:
#         say(greeting)
#         response = get_user_input(["feelings", "yes_no"])
#         if response in VOCABULARY["feelings"] or response in VOCABULARY["yes_no"]:
#              trust_points += 1
#         if response in ["bad", "not great"]:
#             say("I'm sorry to hear that. I hope I can help!")
#         elif response in ["fine", "good", "you too"]:
#              say("Happy to hear that!")
#         time.sleep(1)
#     return trust_points >= TRUST_THRESHOLD

# # --- Main Interaction Flow (Minimal Prints, uses original functions) ---
# def interaction_flow():
#     # Start the Tornado server thread
#     server_thread = threading.Thread(target=run_tornado_server)
#     server_thread.daemon = True
#     server_thread.start()
#     time.sleep(2) # Allow server to start

#     # Define dummy begin/end initially
#     def begin_dummy(): pass
#     def end_dummy(): pass
#     global begin, end
#     # **** Make selected_passion global ****
#     global selected_passion
#     begin = begin_dummy
#     end = end_dummy

#     try:
#         # --- Pepper Connection (Minimal Prints) ---
#         try:
#             pepper_cmd.begin()
#             begin = pepper_cmd.begin
#             end = pepper_cmd.end
#             global motion_service
#             motion_service = pepper_cmd.robot.session.service("ALMotion")
#         except Exception as e:
#             print("Warning: Could not connect to Pepper robot/simulator: {}".format(e))
#             print("Proceeding in simulation mode without robot movement/speech.")
#             motion_service = None
#         # --- End Pepper Connection ---

#         proxemics = ProxemicsSimulator()

#         # --- Behavior Manager (No changes needed) ---
#         try:
#              if pepper_cmd.robot and pepper_cmd.robot.session:
#                  behavior_manager = pepper_cmd.robot.session.service("ALBehaviorManager")
#              else: raise Exception("Robot session not available")
#         except Exception:
#              print("Warning: Could not access ALBehaviorManager. Simulating behaviors.")
#              class DummyBehaviorManager:
#                  def isBehaviorInstalled(self, name): return True
#                  def startBehavior(self, name): pass # Do nothing, just simulate
#              behavior_manager = DummyBehaviorManager()
#         # --- End Behavior Manager ---

#         print("\n=== Starting Interaction ===")
#         proxemics.set_distance(4.0)

#         wave_hello()
#         say("Hello there! May I approach you?")
#         reset_arm()
#         response = get_user_input(["yes_no"])

#         if "yes" in response:
#             move_to_zone('social', proxemics.get_zone())
#             proxemics.set_distance(1.5)

#             say("What's your name?")
#             user_name = get_user_input(["names"]) # Store name

#             # **** Set the global selected_passion ****
#             if user_name in USER_DATABASE:
#                 selected_passion = USER_DATABASE[user_name]["passion"]
#                 selected_greeting = USER_DATABASE[user_name]["greeting"]
#                 print("Identified user: {}, Passion: {}".format(user_name, selected_passion)) # Log
#                 say(selected_greeting) # Use the specific greeting
#             else:
#                 # Handle unknown user - maybe assign a default passion or ask?
#                 selected_passion = "fruits" # Default to fruits if name not found
#                 print("User '{}' not in database. Defaulting passion to '{}'".format(user_name, selected_passion))
#                 say("Hello {}! Nice to meet you. We have a fruit memory game today.".format(user_name))

#             # **** REMOVED data.json writing ****
#             # data = {"message":selected_passion}
#             # print(data)
#             # with open('data.json', 'w') as f:
#             #     json.dump(data, f)
#             # **********************************

#             if build_trust():
#                 move_to_zone('personal', proxemics.get_zone())
#                 proxemics.set_distance(0.8)

#                 # ... (rest of the behavior starting logic remains the same) ...
#                 behavior_name = "move_head_yesno-173088/behavior_1"
#                 if behavior_manager.isBehaviorInstalled(behavior_name):
#                     try:
#                         behavior_manager.startBehavior(behavior_name)
#                     except Exception as e:
#                         print("Error starting behavior {}: {}".format(behavior_name, e))


#                 if not assess_confusion():
#                     # Ask based on the determined passion
#                     say("Since you like {}, would you like to play a {} memory game?".format(selected_passion, selected_passion))
#                     response = get_user_input(["yes_no"])

#                     if "yes" in response:
#                         wave_hello()
#                         say("Great! Let's play the {} game.".format(selected_passion))

#                         # --- Open the web browser ---
#                         # Ensure the path is correct for your system
#                         script_dir = os.path.dirname(os.path.abspath(__file__))
#                         # Use file:// URI scheme for local files
#                         game_url = 'file://' + os.path.join(script_dir, 'index.html')
#                         print("Opening game URL: {}".format(game_url))

#                         try:
#                             webbrowser.open(game_url, new=2) # new=2 opens in a new tab if possible
#                         except Exception as e:
#                             print("Error opening web browser: {}".format(e))
#                             say("I couldn't open the game automatically, sorry.")

#                         # --- Wait for game result ---
#                         print("Waiting for game result...")
#                         game_outcome = None
#                         try:
#                             game_outcome = game_result_queue.get(timeout=900) # 15 min timeout
#                         except Empty:
#                             print("Timed out waiting for game result.")
#                             say("It looks like the game finished or maybe something went wrong.")
#                         except Exception as e:
#                              print("Error waiting for game queue: {}".format(e))

#                         # --- React to game result ---
#                         if game_outcome == "win":
#                             say("Oh wow! You are very strong!")
#                         else:
#                             say("Good game!")

#                         time.sleep(3)
#                         move_to_zone('social', proxemics.get_zone())
#                         proxemics.set_distance(1.5)

#                     else: # User doesn't want to play
#                         say("Maybe another time then.")
#                         move_to_zone('social', proxemics.get_zone())
#                 else: # User appears confused
#                     say("Let me get a human assistant for you.")
#                     move_to_zone('public', proxemics.get_zone())
#             else: # Trust not built
#                 say("I'll give you some space.")
#                 move_to_zone('public', proxemics.get_zone())
#         else: # User does not want Pepper to approach
#             say("Okay, I'll stay here.")

#         reset_arm()

#     except KeyboardInterrupt:
#         print("\nInteraction interrupted by user.")
#         try: tornado.ioloop.IOLoop.current().stop()
#         except: pass
#     except Exception as e:
#         print("\nAn error occurred during interaction: {}".format(e))
#         import traceback
#         traceback.print_exc()
#     finally:
#         # Ensure Pepper connection is closed
#         try:
#             end()
#         except NameError: pass
#         except Exception as e: print("Error closing Pepper connection: {}".format(e))

#         # Stop Tornado IOLoop if it's still running
#         try:
#             if tornado.ioloop.IOLoop.current(instance=False):
#                  tornado.ioloop.IOLoop.current().stop()
#                  print("Tornado IOLoop stopped.")
#         except Exception as e:
#              print("Error stopping Tornado: {}".format(e))


#         print("=== Interaction Complete ===")


# if __name__ == "__main__":
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     os.chdir(script_dir) # Change working directory to script dir
#     print("Running script from directory: {}".format(script_dir))
#     print("Ensure game files (index.html, script.js, style.css, images/) are here.")
#     print("Starting Pepper interaction script (Python 2 / Tornado).")

#     # Add common image types to mimetypes
#     mimetypes.add_type("text/css", ".css")
#     mimetypes.add_type("application/javascript", ".js")
#     mimetypes.add_type("image/jpeg", ".jpg"); mimetypes.add_type("image/jpeg", ".jpeg")
#     mimetypes.add_type("image/png", ".png"); mimetypes.add_type("image/gif", ".gif")
#     mimetypes.add_type("image/x-icon", ".ico") # Add favicon type

#     interaction_flow()


import json
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
import platform  # For OS-specific path handling in webbrowser

# -------------------

# Global variable for motion service (initialized when connected)
motion_service = None

# Queue for communication between web server thread and main thread
# Stores the outcome received from the game via WebSocket ('win', 'lose', 'tie')
game_result_queue = Queue()

# Global variable to hold the passion identified during interaction
# Needs to be accessible by the WebSocket handler when a connection opens
selected_passion = None # Initialize as None

# --- Tornado Server Code ---

# Websocket server handler
class WebSocketServer(tornado.websocket.WebSocketHandler):
    # Store clients if needed for broadcasting, but not strictly necessary here
    clients = set()

    def open(self):
        """Called when a WebSocket connection is opened."""
        print ('[WebSocket] Connection opened from: {}'.format(self.request.remote_ip))
        WebSocketServer.clients.add(self)
        global selected_passion # Access the global variable determined by interaction_flow

        # --- SEND THEME IMMEDIATELY ON CONNECTION ---
        if selected_passion: # Only send if passion has been determined
            theme_message = "theme {}".format(selected_passion)
            print("[WebSocket] Sending theme to client: '{}'".format(theme_message))
            try:
                self.write_message(theme_message)
            except tornado.websocket.WebSocketClosedError:
                print("[WebSocket] Error sending theme: Connection closed prematurely.")
            except Exception as e:
                print("[WebSocket] Error sending theme message: {}".format(e))
        else:
            # This case might happen if the browser connects *before* the passion is identified
            # Or if the script restarts and the browser reconnects quickly.
            print("[WebSocket] Warning: Connection opened, but 'selected_passion' is not yet set.")
            # Optionally send a default theme or a waiting message
            # self.write_message("theme fruits") # Example: send default
            # self.write_message("status waiting_for_theme")

    def on_message(self, message):
        """Called when a message is received from the WebSocket client."""
        global game_result_queue # Access the global queue to signal the main thread

        # print ("[WebSocket] Received message: {}".format(message)) # Uncomment for full debugging

        # We are only interested in the game outcome messages ('win', 'lose', 'tie')
        command = message.strip().lower()

        if command in ["win", "lose", "tie"]:
            print ("[WebSocket] Received game outcome signal: '{}'".format(command))
            try:
                game_result_queue.put(command) # Put the outcome string into the queue
            except Exception as e:
                print("[WebSocket] Error putting message onto queue: {}".format(e))
        else:
            print ("[WebSocket] Received unhandled message: {}".format(message))
            # Ignore other potential messages from the client for now

    def on_close(self):
        """Called when a WebSocket connection is closed."""
        print ('[WebSocket] Connection closed.')
        WebSocketServer.clients.remove(self)

    def check_origin(self, origin):
        """Allow connections from any origin for local development."""
        # In a production environment, you might want to restrict this
        # based on the 'Origin' header.
        # print("[WebSocket] check_origin: {}".format(origin)) # Debug origin
        return True

# Generic File Handler for serving HTML, CSS, JS, and Images
class FileHandler(tornado.web.RequestHandler):
    def get(self, requested_path):
        """Handles GET requests to serve files."""
        try:
            # Base directory is the directory where this script is located
            source_dir = os.path.dirname(os.path.abspath(inspect.getsourcefile(lambda:0)))

            # Construct the full path to the requested file
            # Use os.path.normpath to prevent directory traversal issues (e.g., ../..)
            abs_path = os.path.normpath(os.path.join(source_dir, requested_path))

            # --- Security Check ---
            # Ensure the requested path is still within the script's directory
            if not abs_path.startswith(source_dir):
                print("[FileHandler] Access denied (Path Traversal Attempt?): {}".format(requested_path))
                raise tornado.web.HTTPError(403, "Access denied")

            # Check if the constructed path is a valid file
            if not os.path.isfile(abs_path):
                print("[FileHandler] File not found: {} (Requested: {})".format(abs_path, requested_path))
                raise tornado.web.HTTPError(404, "File not found")

            # Guess the content type
            content_type, encoding = mimetypes.guess_type(abs_path)
            if content_type:
                self.set_header("Content-Type", content_type)
                # print("[FileHandler] Serving {} as {}".format(requested_path, content_type)) # Debug
            else:
                self.set_header("Content-Type", "application/octet-stream") # Default if unknown
                print("[FileHandler] Serving {} as application/octet-stream (Unknown type)".format(requested_path))

            # Read and send the file content
            with open(abs_path, "rb") as f:
                data = f.read()
                self.write(data)
            self.finish()

        except tornado.web.HTTPError as e:
             # If HTTPError was raised (404, 403), send the appropriate status code
             self.send_error(e.status_code)
             # print("[FileHandler] HTTP Error {} serving file {}".format(e.status_code, requested_path)) # Log error

        except Exception as e:
             # Catch any other unexpected errors during file serving
             print "[FileHandler] Unexpected error serving file {}: {}".format(requested_path, e)
             self.send_error(500) # Internal Server Error

# Function to create the Tornado application and define routes
def make_app():
    """Creates the Tornado web application instance."""
    return tornado.web.Application([
        # WebSocket handler route
        (r'/ws', WebSocketServer),

        # Specific routes for root files (important for index.html)
        (r"/(index\.html)", FileHandler),
        (r"/(script\.js)", FileHandler),
        (r"/(style\.css)", FileHandler),

        # Catch-all route for other static files (images, etc.)
        # This regex captures the path and passes it to FileHandler's get() method
        # It looks for common web asset extensions.
        (r"/(.*\.(?:js|css|jpg|jpeg|png|gif|ico|woff|woff2|ttf|eot|svg|map))", FileHandler),

        # Optional: Redirect root "/" to "index.html"
        (r"/", tornado.web.RedirectHandler, {"url": "/index.html"}),

    ],
    # debug=True # Set True for more verbose logging and auto-reloading during development
    )

# Function to run the Tornado server in a separate thread
def run_tornado_server():
    """Starts the Tornado web server on port 8888."""
    try:
        # Ensure we're serving from the script's directory for relative paths
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir) # Change current directory HERE
        print("[Server] Starting web server on http://localhost:8888")
        print("[Server] Serving files from directory: {}".format(script_dir))
        app = make_app()
        app.listen(8888)
        print("[Server] Tornado IOLoop starting...")
        tornado.ioloop.IOLoop.current().start()
        # This line is reached when the IOLoop is stopped
        print("[Server] Tornado IOLoop stopped.")
    except Exception as e:
        print "[Server] FATAL ERROR: Failed to start web server: {}".format(e)
        # Potentially signal the main thread that the server failed?
        # For now, just printing the error.

# --- Pepper Interaction Code ---

TRUST_THRESHOLD = 3 # Number of positive interactions needed to build trust

VOCABULARY = {
    "yes_no": ["yes", "no", "not sure", "maybe", "i don't know"],
    "feelings": ["fine", "good", "great", "okay", "bad", "not great", "terrible", "you too"],
    "locations": ["garden", "my room", "the corridor", "here", "activity room", "living room"],
    "game_difficulty": ["very easy", "easy", "medium", "hard", "very hard"],
    "names" : ["giovanni","carlo", "paolo", "maria", "anna"] # Add more names
}

# Database mapping user names to their preferred passion and a personalized greeting
USER_DATABASE = {
    "giovanni": {
        "passion": "fruits",
        "greeting": "Ah, Giovanni! Welcome back. I remember you enjoy fruits. How about a fruit memory game today?"
    },
    "carlo": {
        "passion": "music",
        "greeting": "Hello Carlo! The music enthusiast returns! Shall we challenge your memory with a music game?"
    },
    "paolo": {
        "passion": "gardening",
        "greeting": "Paolo, good to see you! Ready to test your green thumb's memory with a gardening game?"
    },
     "maria": {
        "passion": "fruits", # Example: Maria also likes fruits
        "greeting": "Hi Maria! It's lovely to see you. Let's play that fruit memory game you like!"
    }
    # Add more users as needed
}

class ProxemicsSimulator:
    """Simulates proxemic zones and trust levels."""
    ZONES = {
        'intimate': (0, 0.45),      # Meters
        'personal': (0.45, 1.2),
        'social': (1.2, 3.6),
        'public': (3.6, float('inf'))
    }

    def __init__(self):
        self.current_distance = 4.0 # Start in public zone
        self.trust_level = 0

    def set_distance(self, distance):
        self.current_distance = max(0, distance) # Distance cannot be negative
        # print("[Proxemics] Distance set to: {:.2f}m (Zone: {})".format(self.current_distance, self.get_zone())) # Debug

    def get_zone(self):
        """Determines the current proxemic zone based on distance."""
        for zone, (min_dist, max_dist) in self.ZONES.items():
            # Use float comparison carefully
            if float(min_dist) <= float(self.current_distance) < float(max_dist):
                return zone
        return 'public' # Default if somehow outside defined ranges

    def is_too_close(self):
        """Checks if the current distance is closer than the personal zone boundary."""
        return float(self.current_distance) < float(self.ZONES['personal'][0])

# --- Pepper Movement and Speech Functions ---

def move_forward(distance_meters):
    """Commands Pepper to move forward or backward."""
    global motion_service
    if not motion_service:
        print("[Move] Simulation: Move forward/backward by {:.2f}m".format(distance_meters))
        return
    try:
        print("[Move] Commanding Pepper to move by {:.2f}m...".format(distance_meters))
        # moveTo uses relative coordinates (X, Y, Theta)
        # Positive X is forward, negative X is backward
        motion_service.moveTo(distance_meters, 0, 0)
        time.sleep(0.5) # Short pause after movement command
        print("[Move] Movement command sent.")
    except Exception as e:
        print("[Move] Error during move_forward: {}".format(e))

def move_to_zone(target_zone, current_zone):
    """Calculates and executes movement to reach a target proxemic zone."""
    zone_target_distances = {'public': 3.0, 'social': 1.5, 'personal': 0.8, 'intimate': 0.3} # Mid-points/typical distances
    target_distance = zone_target_distances.get(target_zone)
    current_typical_dist = zone_target_distances.get(current_zone)

    if target_distance is None or current_typical_dist is None:
        print("[Move] Error: Invalid zone provided for move_to_zone ('{}' or '{}').".format(target_zone, current_zone))
        return

    # Calculate movement needed: current typical distance - target distance
    # Example: Moving from social (1.5) to personal (0.8) -> 1.5 - 0.8 = 0.7m forward
    # Example: Moving from personal (0.8) to social (1.5) -> 0.8 - 1.5 = -0.7m (backward)
    movement = float(current_typical_dist) - float(target_distance)

    print("[Move] Moving from {} zone (~{:.1f}m) to {} zone (~{:.1f}m). Required movement: {:.2f}m".format(
        current_zone, current_typical_dist, target_zone, target_distance, movement))

    # Only move if the required distance is significant
    if abs(movement) > 0.1: # Threshold to avoid tiny unnecessary movements
        move_forward(movement)
    else:
        print("[Move] Target zone already close enough, no significant movement needed.")

def get_user_input(categories=None):
    """Gets input from the console, mimicking speech recognition."""
    # In a real application, this would use ALSpeechRecognition
    prompt = "Your response"
    if categories:
        expected = ", ".join(cat for cat in categories)
        prompt += " (Expected: {})".format(expected)
    prompt += ": "

    while True:
        try:
            # Use raw_input() for Python 2
            response = raw_input(prompt).strip().lower()

            if not response:
                print("I didn't catch that. Could you please say it again?")
                say("Sorry, I didn't catch that. Could you please say it again?") # Pepper feedback
                continue

            # If specific categories are expected, validate against vocabulary
            if categories:
                found_match = False
                # Check keywords in the provided categories
                for category_name in categories:
                    for keyword in VOCABULARY.get(category_name, []):
                        # Simple keyword spotting
                        if keyword in response:
                            print("[Input] Matched keyword '{}' in category '{}' from response '{}'".format(keyword, category_name, response))
                            return keyword # Return the matched keyword

                # If no keyword matched across all specified categories
                if not found_match:
                    unrecognized_msg = "I'm sorry, I didn't quite understand that."
                    # Provide more specific feedback if possible
                    if 'yes_no' in categories:
                         unrecognized_msg += " Please try saying 'yes' or 'no'."
                    elif 'names' in categories:
                         unrecognized_msg += " Could you please tell me your name again?"

                    print("[Input] Response '{}' did not match expected categories: {}".format(response, categories))
                    say(unrecognized_msg)
                    # Loop continues to ask again
            else:
                # If no categories specified, return the raw (lowercase) response
                print("[Input] Received raw response: '{}'".format(response))
                return response

        except (EOFError, KeyboardInterrupt):
            print("\nUser interrupted input. Exiting...")
            # Potentially add cleanup here if needed before exiting
            sys.exit(0)
        except Exception as e:
            print("\nAn error occurred while reading input: {}".format(e))
            # Exit gracefully on unexpected input errors
            sys.exit(1)

def wave_hello():
    """Commands Pepper to perform a waving gesture."""
    global motion_service
    if not motion_service:
        print("[Gesture] Simulation: Wave hello")
        return
    try:
        print("[Gesture] Performing wave...")
        # Ensure robot is awake and arm has stiffness
        motion_service.wakeUp()
        motion_service.setStiffnesses("RArm", 1.0)
        # Define keyframes for a simple wave
        names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]
        # Frame 1: Arm up
        angles1 = [-0.5,           -0.3,            1.0,         0.8,          0.0,         1.0] # Hand open
        # Frame 2: Wave part 1
        angles2 = [-0.5,           -0.3,            1.0,         1.2,          0.0,         1.0]
        # Frame 3: Wave part 2
        angles3 = [-0.5,           -0.3,            1.0,         0.8,          0.0,         1.0]
        times = [[1.0], [1.8], [2.6]] # Timing for each frame
        # Execute the motion sequence
        motion_service.angleInterpolation(names, [angles1, angles2, angles3], times, True) # isAbsolute=True
        print("[Gesture] Wave complete.")
        # Optional: Return arm to a neutral position afterwards using reset_arm() or another sequence
    except Exception as e:
        print("[Gesture] Error during wave_hello: {}".format(e))

def reset_arm():
    """Resets Pepper's right arm to a neutral position and removes stiffness."""
    global motion_service
    if not motion_service:
        print("[Gesture] Simulation: Reset arm")
        return
    try:
        print("[Gesture] Resetting arm to neutral position...")
        motion_service.setStiffnesses("RArm", 1.0)
        # Define a neutral resting position
        names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]
        angles = [1.5,            -0.1,            0.0,         0.2,          0.0,         0.0] # Hand closed slightly
        times = [1.5] # Time to reach the position
        motion_service.angleInterpolation(names, angles, times, True)
        # Remove stiffness to save power and allow manual movement
        motion_service.setStiffnesses("RArm", 0.0)
        print("[Gesture] Arm reset and stiffness removed.")
    except Exception as e:
        print("[Gesture] Error during reset_arm: {}".format(e))

def say(text):
    """Commands Pepper to say the given text."""
    print("Pepper says: \"{}\"".format(text)) # Console feedback
    try:
        # Use the pepper_cmd wrapper if available
        if 'pepper_cmd' in sys.modules and hasattr(pepper_cmd, 'robot') and pepper_cmd.robot:
            pepper_cmd.robot.say(text)
        else:
            # Fallback simulation if pepper_cmd isn't fully initialized
            print("[Speech] Simulation: Robot would say the text above.")
    except Exception as e:
        print("[Speech] Error during pepper_cmd.robot.say: {}".format(e))
    time.sleep(0.2) # Small pause after speaking

def assess_confusion():
    """Asks simple orientation questions to assess potential confusion."""
    print("[Assess] Assessing user confusion...")
    questions = [
        ("Do you know what day it is today?", ["yes_no"]), # Expect yes/no
        ("Can you tell me where we are right now?", ["locations", "yes_no"]), # Expect location or maybe yes/no
        ("Just checking, do you remember my name? It's Pepper.", ["yes_no"]) # Simple check
    ]
    confusion_score = 0
    positive_responses = ["yes", "i know"] # Responses indicating orientation

    for q_text, q_categories in questions:
        say(q_text)
        response = get_user_input(q_categories)
        # Increment score if response indicates uncertainty or 'no'
        if response not in positive_responses and response not in VOCABULARY.get("locations", []):
             confusion_score += 1
             print("[Assess] Response '{}' indicates potential confusion.".format(response))
        else:
             print("[Assess] Response '{}' seems oriented.".format(response))
        time.sleep(0.5) # Pause between questions

    is_confused = confusion_score >= 2 # Consider confused if 2 or more uncertain answers
    print("[Assess] Confusion assessment complete. Score: {} (Confused: {})".format(confusion_score, is_confused))
    return is_confused

def build_trust():
    """Engages in simple social interaction to build rapport."""
    print("[Trust] Attempting to build trust...")
    trust_points = 0
    greetings = [
        ("It's nice to interact with you today. Is it a good day for you?", ["feelings", "yes_no"]),
        ("How are you feeling right now?", ["feelings"])
    ]
    positive_feelings = ["fine", "good", "great", "okay", "yes"]
    negative_feelings = ["bad", "not great", "terrible", "no"]

    for g_text, g_categories in greetings:
        say(g_text)
        response = get_user_input(g_categories)

        if response in positive_feelings:
             trust_points += 1
             say("I'm happy to hear that!")
             print("[Trust] Positive response received: '{}'".format(response))
        elif response in negative_feelings:
            # Acknowledge negative feelings but don't necessarily award trust point
            say("Oh, I'm sorry to hear that. I hope our game can bring a little brightness.")
            print("[Trust] Negative response received: '{}'".format(response))
        elif response == "you too": # Handle "you too" specifically if asked "How are you?"
             trust_points += 1 # Consider it positive engagement
             say("Thank you for asking! I'm feeling operational and ready to play!")
             print("[Trust] Engaging response received: '{}'".format(response))
        else:
             # Neutral or unrecognized response
             say("Okay.")
             print("[Trust] Neutral/unrecognized response: '{}'".format(response))

        time.sleep(0.5)

    trust_built = trust_points >= 1 # Require at least one positive interaction
    print("[Trust] Trust building complete. Points: {} (Trust built: {})".format(trust_points, trust_built))
    return trust_built

# --- Main Interaction Flow ---
def interaction_flow():
    """Orchestrates the entire user interaction sequence."""
    # Start the Tornado server in a background thread
    print("[Main] Starting Tornado server thread...")
    server_thread = threading.Thread(target=run_tornado_server)
    server_thread.daemon = True # Allows main thread to exit even if server thread is running
    server_thread.start()
    time.sleep(3) # Give the server a moment to initialize

    # Placeholder for Pepper connection functions
    # These will be replaced by actual pepper_cmd functions if connection succeeds
    def begin_dummy(): print("[Pepper] Simulation: Begin connection.")
    def end_dummy(): print("[Pepper] Simulation: End connection.")
    global begin, end, selected_passion, motion_service
    begin = begin_dummy
    end = end_dummy
    selected_passion = None # Reset passion at the start of the flow
    motion_service = None   # Reset motion service

    main_thread_running = True # Flag for main loop

    try:
        # --- Attempt Pepper Connection ---
        try:
            print("[Main] Attempting to connect to Pepper...")
            pepper_cmd.begin() # Establish connection
            # If connection successful, reassign begin/end
            begin = pepper_cmd.begin
            end = pepper_cmd.end
            # Get essential services
            motion_service = pepper_cmd.robot.session.service("ALMotion")
            # tts_service = pepper_cmd.robot.session.service("ALTextToSpeech") # Already wrapped by pepper_cmd.say
            # behavior_manager = pepper_cmd.robot.session.service("ALBehaviorManager") # Get later if needed
            print("[Main] Successfully connected to Pepper.")
            motion_service.wakeUp() # Make sure robot is active
        except Exception as e:
            print("[Main] WARNING: Could not connect to Pepper robot/simulator.")
            print("       Error: {}".format(e))
            print("       Proceeding in simulation mode without robot actions.")
            # Keep motion_service as None, begin/end as dummies
        # --- End Pepper Connection Attempt ---

        proxemics = ProxemicsSimulator() # Initialize proxemics simulation

        # --- Get Behavior Manager (Safely) ---
        behavior_manager = None
        try:
             if pepper_cmd.robot and pepper_cmd.robot.session:
                 behavior_manager = pepper_cmd.robot.session.service("ALBehaviorManager")
                 print("[Main] ALBehaviorManager service acquired.")
             else:
                 raise Exception("Robot session not available for BehaviorManager.")
        except Exception as e:
             print("[Main] Warning: Could not access ALBehaviorManager. Simulating behaviors.")
             print("       Error: {}".format(e))
             # Create a dummy object that mimics the necessary methods
             class DummyBehaviorManager:
                 def isBehaviorInstalled(self, name):
                     print("[Behavior] Simulation: Checking if '{}' is installed (assuming yes).".format(name))
                     return True
                 def startBehavior(self, name):
                     print("[Behavior] Simulation: Starting behavior '{}'.".format(name))
                     pass # Do nothing, just log
             behavior_manager = DummyBehaviorManager()
        # --- End Behavior Manager ---

        print("\n=== Starting Interaction Sequence ===")
        proxemics.set_distance(4.0) # Start in public zone

        # --- Initial Greeting and Approach ---
        wave_hello()
        say("Hello there! I'm Pepper. May I come a little closer to chat?")
        reset_arm()
        response = get_user_input(["yes_no"])

        if "yes" in response:
            print("[Main] User granted permission to approach.")
            move_to_zone('social', proxemics.get_zone())
            proxemics.set_distance(1.5) # Update simulated distance to social zone

            # --- User Identification ---
            say("It's nice to meet you! What's your name?")
            user_name = get_user_input(["names"])

            # Determine passion based on name using the database
            if user_name in USER_DATABASE:
                user_info = USER_DATABASE[user_name]
                selected_passion = user_info["passion"]
                selected_greeting = user_info["greeting"]
                print("[Main] Identified user: '{}', Assigned Passion: '{}'".format(user_name, selected_passion))
                say(selected_greeting) # Use the personalized greeting
            else:
                # Handle unknown user - assign a default passion
                selected_passion = "fruits" # Default to fruits if name not recognized
                print("[Main] User name '{}' not found in database. Defaulting passion to '{}'".format(user_name, selected_passion))
                say("Hello {}! It's a pleasure to meet you. Today, we can try a fun fruit memory game if you like.".format(user_name))

            # The global 'selected_passion' is now set for the WebSocket handler

            # --- Build Trust ---
            if build_trust():
                print("[Main] Trust established. Moving closer.")
                move_to_zone('personal', proxemics.get_zone())
                proxemics.set_distance(0.8) # Update simulated distance

                # --- Start Head Nodding Behavior (if available) ---
                # Example behavior name - replace with your actual behavior if different
                head_nod_behavior = "move_head_yesno-173088/behavior_1"
                if behavior_manager:
                    try:
                        if behavior_manager.isBehaviorInstalled(head_nod_behavior):
                            print("[Main] Starting head nod behavior...")
                            behavior_manager.startBehavior(head_nod_behavior)
                            # Note: This behavior might run asynchronously.
                            # You might need ways to stop it later if necessary.
                        else:
                            print("[Main] Head nod behavior '{}' not installed.".format(head_nod_behavior))
                    except Exception as e:
                        print("[Main] Error starting behavior '{}': {}".format(head_nod_behavior, e))

                # --- Assess Confusion ---
                if not assess_confusion():
                    print("[Main] User does not appear confused. Proposing game.")
                    # Ask user if they want to play the game based on their passion
                    say("Since you seem to enjoy {}, would you like to play a memory game about {}?".format(selected_passion, selected_passion))
                    response = get_user_input(["yes_no"])

                    if "yes" in response:
                        print("[Main] User agreed to play the game.")
                        wave_hello() # Enthusiastic gesture
                        say("Fantastic! Let's play the {} game. I'll bring it up.".format(selected_passion))
                        reset_arm()

                        # --- Attempt to Open the Web Browser ---
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        html_file_path = os.path.abspath(os.path.join(script_dir, 'index.html'))
                        browser_opened_successfully = False

                        print("[Main] Attempting to open game in web browser...")
                        if not os.path.exists(html_file_path):
                             print("[Main] !!! CRITICAL ERROR: index.html not found at expected path: {}".format(html_file_path))
                             say("Oh dear, I seem to have misplaced the game file. I can't open it right now, sorry.")
                        else:
                            # Method 1: Try raw path (often more reliable)
                            print("[Main]   Trying Method 1 (Raw Path): {}".format(html_file_path))
                            try:
                                if webbrowser.open(html_file_path, new=2): # new=2 prefers new tab
                                    print("[Main]   -> Browser launch initiated (Method 1). Please check your desktop.")
                                    browser_opened_successfully = True
                                else:
                                    print("[Main]   -> webbrowser.open (Method 1) returned False. Trying Method 2...")
                            except Exception as e:
                                print("[Main]   !!! Error opening browser (Method 1): {}".format(e))

                            # Method 2: Try file:// URL (especially if Method 1 failed)
                            if not browser_opened_successfully:
                                try:
                                    if platform.system() == "Windows":
                                        game_url_file = 'file:///' + html_file_path.replace('\\', '/')
                                    else: # Linux, macOS
                                        game_url_file = 'file://' + html_file_path
                                    print("[Main]   Trying Method 2 (file:// URL): {}".format(game_url_file))

                                    if webbrowser.open(game_url_file, new=2):
                                        print("[Main]   -> Browser launch initiated (Method 2). Please check your desktop.")
                                        browser_opened_successfully = True
                                    else:
                                        print("[Main]   !!! Error: webbrowser.open (Method 2) also returned False.")
                                        print("        Possible reasons: No default browser configured, permissions issue, or running in an environment without a graphical interface (like directly on Pepper OS without display).")
                                except Exception as e:
                                    print("[Main]   !!! Error opening browser (Method 2): {}".format(e))

                            # Provide feedback if browser opening failed
                            if not browser_opened_successfully:
                                say("I couldn't open the game page automatically. You might need to open the 'index.html' file in the script's folder yourself.")

                        # --- Wait for Game Result from WebSocket ---
                        print("[Main] Waiting for game result via WebSocket (Timeout: 15 minutes)...")
                        game_outcome = None
                        try:
                            # Blocking call to wait for an item from the queue
                            game_outcome = game_result_queue.get(block=True, timeout=900) # 15 min timeout
                            print("[Main] Received game outcome from queue: '{}'".format(game_outcome))
                        except Empty:
                            # This happens if the timeout occurs before anything is put in the queue
                            print("[Main] Timed out waiting for game result.")
                            say("It seems the game took a while, or maybe it's finished now. I hope you had fun!")
                        except Exception as e:
                             print("[Main] Error occurred while waiting for game result queue: {}".format(e))
                             say("Something unexpected happened while waiting for the game result.")

                        # --- React to Game Outcome ---
                        if game_outcome == "win":
                            say("Wow! You won the game! Congratulations, you have an excellent memory!")
                            # TODO: Add celebratory animation (e.g., behavior_manager.startBehavior("clap-...") )
                        elif game_outcome == "lose":
                            say("Good game! Pepper enjoyed playing with you.")
                        elif game_outcome == "tie":
                            say("A tie! We both have good memories it seems!")
                        # No specific reaction needed if timeout occurred (handled above)

                        time.sleep(3) # Pause before moving back
                        print("[Main] Game sequence finished. Moving back.")
                        move_to_zone('social', proxemics.get_zone())
                        proxemics.set_distance(1.5)

                    else: # User declined to play
                        print("[Main] User declined the game.")
                        say("Alright, maybe another time then. It was nice chatting!")
                        move_to_zone('social', proxemics.get_zone())
                        proxemics.set_distance(1.5)
                else: # User appears confused
                    print("[Main] User seems confused. Offering assistance.")
                    say("It seems you might need some assistance. I'll step back for now and let someone know.")
                    # Move back to a non-intrusive distance
                    move_to_zone('public', proxemics.get_zone())
                    proxemics.set_distance(3.6)
            else: # Trust not built
                print("[Main] Failed to build sufficient trust. Keeping distance.")
                say("Okay, I understand. I'll give you some space for now.")
                # Stay in or move back to social/public zone
                if proxemics.get_zone() != 'public':
                    move_to_zone('public', proxemics.get_zone())
                    proxemics.set_distance(3.6)
        else: # User declined initial approach
            print("[Main] User declined approach. Respecting space.")
            say("Okay, I respect your space. I'll stay here. Have a nice day!")
            # Robot remains in the public zone

        # --- End of Interaction ---
        reset_arm() # Ensure arm is in a safe, neutral state
        say("Goodbye for now!")
        if motion_service:
            motion_service.rest() # Put robot in a resting state

    except KeyboardInterrupt:
        # User pressed Ctrl+C
        print("\n[Main] Interaction interrupted by user (Ctrl+C). Shutting down...")
        main_thread_running = False
        # Attempt to stop Tornado - may not work reliably from except block in main thread
        try: tornado.ioloop.IOLoop.current().stop()
        except: pass
    except Exception as e:
        # Catch any unexpected errors during the main interaction flow
        print("\n--- [Main] UNEXPECTED ERROR DURING INTERACTION ---")
        print("    Error Type: {}".format(type(e).__name__))
        print("    Error Details: {}".format(e))
        import traceback
        traceback.print_exc() # Print the full stack trace for debugging
        main_thread_running = False
        try: tornado.ioloop.IOLoop.current().stop()
        except: pass
        # Try to say an error message if possible
        try: say("Oops, something went wrong with my program. I need to stop now.")
        except: pass
    finally:
        # --- Cleanup ---
        print("[Main] Entering cleanup phase...")
        # Close Pepper Connection (check if 'end' was assigned)
        try:
            if 'end' in globals() and callable(end) and end != end_dummy:
                 print("[Main] Closing Pepper connection...")
                 end()
                 print("[Main] Pepper connection closed.")
            else:
                 print("[Main] Pepper connection was not established or 'end' function is unavailable.")
        except NameError: pass # Should not happen with global scope, but safe check
        except Exception as e:
            print("[Main] Error during Pepper cleanup (end()): {}".format(e))

        # Stop Tornado IOLoop (important to release the port)
        # Check if the loop instance exists and is running before stopping
        print("[Main] Attempting to stop Tornado IOLoop...")
        try:
            ioloop_instance = tornado.ioloop.IOLoop.current(instance=False)
            if ioloop_instance and ioloop_instance._running:
                 ioloop_instance.stop()
                 print("[Main] Tornado IOLoop stopped via finally block.")
            #else:
                 #print("[Main] Tornado IOLoop was not running or instance not found.")
        except Exception as e:
             print("[Main] Error stopping Tornado IOLoop in finally block: {}".format(e))

        # Wait briefly for the server thread to potentially finish closing
        time.sleep(1)

        print("=== Interaction Sequence Complete ===")

# --- Main Execution Block ---
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # **** CRITICAL: Change working directory to script's directory ****
    # This ensures the FileHandler serves files relative to the script location.
    try:
        os.chdir(script_dir)
        print("Changed working directory to: {}".format(script_dir))
    except Exception as e:
        print("FATAL ERROR: Could not change working directory to script location: {}".format(e))
        sys.exit(1)

    print("-----------------------------------------------------")
    print(" Starting Pepper Memory Game Interaction Script")
    print(" Script location: {}".format(script_dir))
    print(" Ensure game files (index.html, script.js, style.css, images/) are present here.")
    print(" Using Python {} with Tornado".format(sys.version_info[0]))
    print("-----------------------------------------------------")

    # Add common web mime types if they might be missing
    mimetypes.add_type("text/html", ".html")
    mimetypes.add_type("text/css", ".css")
    mimetypes.add_type("application/javascript", ".js")
    mimetypes.add_type("image/jpeg", ".jpg"); mimetypes.add_type("image/jpeg", ".jpeg")
    mimetypes.add_type("image/png", ".png"); mimetypes.add_type("image/gif", ".gif")
    mimetypes.add_type("image/svg+xml", ".svg")
    mimetypes.add_type("image/x-icon", ".ico")
    mimetypes.add_type("application/font-woff", ".woff")
    mimetypes.add_type("application/font-woff2", ".woff2")
    mimetypes.add_type("application/vnd.ms-fontobject", ".eot")
    mimetypes.add_type("application/x-font-ttf", ".ttf")
    mimetypes.add_type("application/json", ".json"); mimetypes.add_type("application/manifest+json", ".webmanifest")
    mimetypes.add_type("text/plain", ".map") # For source maps

    # Start the main interaction logic
    interaction_flow()

    print("[Main] Script execution finished.")