





import os
import sys
import time
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
import platform  # For OS-specific path handling in webbrowser

motion_service = None


game_result_queue = Queue()
selected_passion = None
selected_name = None
# --- Tornado Server Code ---
class WebSocketServer(tornado.websocket.WebSocketHandler):
    clients = set()
    def open(self):
        WebSocketServer.clients.add(self)

        global selected_passion
        global selected_name
        

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

        if selected_name:

            name_message = "name {}".format(selected_name)
            print("[WebSocket] Sending name to client: '{}'".format(name_message))
            try:
                self.write_message(name_message)
            except tornado.websocket.WebSocketClosedError:
                print("[WebSocket] Error sending name: Connection closed prematurely.")
            except Exception as e:
                print("[WebSocket] Error sending name message: {}".format(e))

        else:
            # This case might happen if the browser connects *before* the passion is identified
            # Or if the script restarts and the browser reconnects quickly.
            print("[WebSocket] Warning: Connection opened, but 'selected_name' is not yet set.")
            # Optionally send a default theme or a waiting message
            # self.write_message("theme fruits") # Example: send default
            # self.write_message("status waiting_for_theme") 

        # if selected_passion:
        #     theme_message = "theme {}".format(selected_passion)
        #     try: self.write_message(theme_message)
        #     except (tornado.websocket.WebSocketClosedError, Exception): pass

    def on_message(self, message):
        global game_result_queue
        command = message.strip().lower()
        if command in ["win", "lose", "tie"]:
            print ("[WebSocket] Received game outcome signal: '{}'".format(command))
            try: game_result_queue.put(command)
            except Exception: pass

    def on_close(self):
        if self in WebSocketServer.clients: WebSocketServer.clients.remove(self)
    def check_origin(self, origin): return True

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

def make_app():
    return tornado.web.Application([
        (r'/ws', WebSocketServer), (r"/(index\.html)", FileHandler),
        (r"/(script\.js)", FileHandler), (r"/(style\.css)", FileHandler),
        (r"/(.*\.(?:js|css|jpg|jpeg|png|gif|ico|woff|woff2|ttf|eot|svg|map))", FileHandler),
        (r"/", tornado.web.RedirectHandler, {"url": "/index.html"}),
    ])

def run_tornado_server():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir); app = make_app(); app.listen(8888)
        tornado.ioloop.IOLoop.current().start()
    except Exception as e: print("[Server] FATAL ERROR: Failed to start web server: {}".format(e))

TRUST_THRESHOLD = 3
VOCABULARY = {
    "yes_no": ["yes", "no", "not sure", "maybe", "i don't know"],
    "feelings": ["fine", "good", "great", "okay", "bad", "not great", "terrible", "you too"],
    "locations": ["garden", "my room", "the corridor", "here", "activity room", "living room"],
    "names" : ["giovanni","carlo", "paolo"] 
}
USER_DATABASE = {
    "giovanni": {"name" : "Giovanni", 
                "passion": "fruits", 
                "greeting": "Ah, Giovanni! Welcome back!"},
    "carlo": {"name" : "Carlo", 
              "passion": "music", 
              "greeting": "Hello Carlo! Great to see you again!"},
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
    except Exception: pass # Silently fail if real robot movement fails

def move_to_zone(target_zone, current_zone):
    zone_target_distances = {'public': 3.0, 'social': 1.5, 'personal': 0.8, 'intimate': 0.3}
    target_distance = zone_target_distances.get(target_zone)
    current_typical_dist = zone_target_distances.get(current_zone)
    if target_distance is None or current_typical_dist is None: return
    movement = float(current_typical_dist) - float(target_distance)
    if abs(movement) > 0.1: move_forward(movement)

def get_user_input(categories=None):
    # Prompt is simplified as per your request
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
                # No "Expected" part in the feedback as per your request
                if 'yes_no' in categories: unrecognized_msg += " Please try saying 'yes' or 'no'."
                elif 'names' in categories: unrecognized_msg += " Could you please tell me your name again?"
                pepper_cmd.robot.say(unrecognized_msg)
            else: return response
        except (EOFError, KeyboardInterrupt): print("\nUser interrupted. Exiting..."); sys.exit(0)
        except AttributeError:
            
             print("ERROR: Robot not connected. Cannot use speech for input feedback.")

             if not response: print("I didn't catch that. Please try again."); continue
             if categories: print("I didn't understand. Please try again."); continue
             else: return response # Should not happen if categories is None and response is not empty
        except Exception as e: print("\nError reading input: {}".format(e)); sys.exit(1)


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
                 ("Just checking, do you remember my name?", ["yes_no"])]
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
        if response in positive_feelings: trust_points += 1; feedback_say = "I'm happy to hear that!"
        elif response in negative_feelings: feedback_say = "Oh, I'm sorry to hear that. I hope our game can bring a little brightness."
        elif response == "you too": trust_points += 1; feedback_say = "Thank you for asking! I'm feeling operational and ready to play!"
        else: feedback_say = "Okay."
        
        try:
            pepper_cmd.robot.say(feedback_say)
        except AttributeError: print("Pepper (sim) says: \"{}\"".format(feedback_say)) # Sim fallback
        except Exception as e_say_fb: print("Error in build_trust (feedback_say): {}".format(e_say_fb))
        time.sleep(0.5)
    return trust_points >= 1

# --- Main Interaction Flow (Simpler, Single-Play Version) ---
def interaction_flow():
    server_thread = threading.Thread(target=run_tornado_server)
    server_thread.daemon = True; server_thread.start(); time.sleep(3)

    def begin_dummy(): pass
    def end_dummy(): pass
    global begin, end, selected_passion, motion_service, selected_name
    begin, end = begin_dummy, end_dummy
    selected_passion = None
    selected_name = None
    motion_service = None # Initialize global motion_service

    initial_connection_successful = False
    try:
        try:
            print("Attempting to connect to Pepper...")
            pepper_cmd.begin()
            begin = pepper_cmd.begin
            end = pepper_cmd.end
            if pepper_cmd.robot and pepper_cmd.robot.session:
                 motion_service = pepper_cmd.robot.session.service("ALMotion")
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
        proxemics = ProxemicsSimulator(); proxemics.set_distance(4.0)

        wave_hello()
        try:

            pepper_cmd.robot.say("Hello there! I'm Pepper. What's your name?")
        except AttributeError: print("Pepper (sim) says: \"Hello there! I'm Pepper. What's your name?\"")
            # pepper_cmd.robot.say("Hello there! I'm Pepper. May I come a little closer to chat?")
        # except AttributeError: print("Pepper (sim) says: \"Hello there! I'm Pepper. May I come a little closer to chat?\"")
        except Exception as e_say: print("Error during initial say: {}".format(e_say))
        reset_arm()

        user_name = get_user_input(["names"])
            

        if user_name in USER_DATABASE:
            user_info = USER_DATABASE[user_name]
            selected_passion, selected_greeting = user_info["passion"], user_info["greeting"]
            selected_name = user_info["name"]

            

            try: pepper_cmd.robot.say(selected_greeting)
            except AttributeError: print("Pepper (sim) says: \"{}\"".format(selected_greeting))
        else:
            selected_passion = "fruits" # Default passion
            greeting_unknown = "Hello {}! It's a pleasure to meet you. Today, we can try a fun fruit memory game if you like.".format(selected_name)
            try: pepper_cmd.robot.say(greeting_unknown)
            except AttributeError: print("Pepper (sim) says: \"{}\"".format(greeting_unknown))

        try:
            pepper_cmd.robot.say("Hello there! I'm Pepper. May I come a little closer to chat?")
        except AttributeError: print("Pepper (sim) says: \"Hello there! I'm Pepper. May I come a little closer to chat?\"")

        response = get_user_input(["yes_no"]) # get_user_input has its own sim fallbacks

        if "yes" in response:
            move_to_zone('social', proxemics.get_zone()); proxemics.set_distance(1.5)
            '''
            try:
                pepper_cmd.robot.say("It's nice to meet you! What's your name?")
            except AttributeError: print("Pepper (sim) says: \"It's nice to meet you! What's your name?\"")
            user_name = get_user_input(["names"])
            

            if user_name in USER_DATABASE:
                user_info = USER_DATABASE[user_name]
                selected_passion, selected_greeting = user_info["passion"], user_info["greeting"]
                selected_name = user_info["name"]

                

                try: pepper_cmd.robot.say(selected_greeting)
                except AttributeError: print("Pepper (sim) says: \"{}\"".format(selected_greeting))
            else:
                selected_passion = "fruits" # Default passion
                greeting_unknown = "Hello {}! It's a pleasure to meet you. Today, we can try a fun fruit memory game if you like.".format(selected_name)
                try: pepper_cmd.robot.say(greeting_unknown)
                except AttributeError: print("Pepper (sim) says: \"{}\"".format(greeting_unknown))

            '''

            if build_trust(): # build_trust has its own sim fallbacks
                move_to_zone('personal', proxemics.get_zone()); proxemics.set_distance(0.8)
                head_nod_behavior = "move_head_yesno-173088/behavior_1"
                if behavior_manager:
                    try:
                        if behavior_manager.isBehaviorInstalled(head_nod_behavior):
                            behavior_manager.startBehavior(head_nod_behavior)
                    except Exception: pass

                if not assess_confusion(): # assess_confusion has its own sim fallbacks
                    game_proposal_text = "Since you seem to enjoy {}, would you like to play a memory game about {}?".format(selected_passion, selected_passion)
                    try:
                        pepper_cmd.robot.say(game_proposal_text)
                    except AttributeError: print("Pepper (sim) says: \"{}\"".format(game_proposal_text))
                    
                    game_choice_response = get_user_input(["yes_no"])

                    if "yes" in game_choice_response:
                        wave_hello()
                        game_start_text = "Great! Let's play the {} game.".format(selected_passion)
                        try:
                            pepper_cmd.robot.say(game_start_text)
                        except AttributeError: print("Pepper (sim) says: \"{}\"".format(game_start_text))
                        reset_arm()
                        
                        # Clear queue before starting game, just in case
                        if not game_result_queue.empty():
                            try:
                                while not game_result_queue.empty(): game_result_queue.get_nowait()
                            except Empty: pass

                        # --- Open the web browser ---
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
                                    #print("Browser launch initiated."); 
                                    browser_opened_successfully = True
                            except Exception: pass
                            if not browser_opened_successfully:
                                try:
                                    game_url_file = ('file:///' if platform.system() == "Windows" else 'file://') + html_file_path.replace('\\', '/')
                                    if webbrowser.open(game_url_file, new=2):
                                      
                                        browser_opened_successfully = True
                                except Exception: pass
                            if not browser_opened_successfully:
                                try: pepper_cmd.robot.say("I couldn't open the game page automatically, sorry.")
                                except AttributeError: print("Pepper (sim) says: \"I couldn't open the game page automatically, sorry.\"")

                        # --- Wait for game result ---
                        print("[Main] Waiting for game result via WebSocket (Timeout: 15 min)...")
                        game_outcome = None # Default to None in case of timeout without result
                        try:
                            game_outcome = game_result_queue.get(block=True, timeout=900) # 15 min timeout
                            print("[Main] Received game outcome from queue: '{}'".format(game_outcome))
                        except Empty:
                            print("[Main] Timed out waiting for game result.")
                            try: pepper_cmd.robot.say("It looks like the game finished, or we ran out of time. I hope you had fun!")
                            except AttributeError: print("Pepper (sim) says: \"It looks like the game finished, or we ran out of time. I hope you had fun!\"")
                        except Exception as e_queue:
                             print("[Main] Error waiting for game result queue: {}".format(e_queue))
                             try: pepper_cmd.robot.say("Something went wrong while waiting for the game result.")
                             except AttributeError: print("Pepper (sim) says: \"Something went wrong while waiting for the game result.\"")

                        # --- React to game result ---
                        outcome_speech = ""
                        if game_outcome == "win":
                            outcome_speech = "Oh wow! You are very strong! Congratulations!"
                        elif game_outcome == "lose" or game_outcome == "tie": # Treat tie same as lose for this simple flow
                            outcome_speech = "Good game! That was fun."
                        # If game_outcome is None (e.g. timeout), no specific win/loss message, already handled.

                        if outcome_speech: # Only say if there was a defined outcome message
                            try:
                                pepper_cmd.robot.say(outcome_speech)
                            except AttributeError: print("Pepper (sim) says: \"{}\"".format(outcome_speech))
                        
                        # Regardless of outcome, move back after the game attempt.
                        time.sleep(2) # Pause after game reaction
                        move_to_zone('social', proxemics.get_zone())
                        proxemics.set_distance(1.5)

                    else: # User doesn't want to play
                        decline_play_text = "Maybe another time then."
                        try:
                            pepper_cmd.robot.say(decline_play_text)
                        except AttributeError: print("Pepper (sim) says: \"{}\"".format(decline_play_text))
                        move_to_zone('social', proxemics.get_zone()) # Also move back if they decline
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
                if proxemics.get_zone() != 'public': # Move back if not already in public
                    move_to_zone('public', proxemics.get_zone())
                    proxemics.set_distance(3.6)
        else: # User does not want Pepper to approach
            decline_approach_text = "Okay, I'll stay here. Have a nice day!"
            try:
                pepper_cmd.robot.say(decline_approach_text)
            except AttributeError: print("Pepper (sim) says: \"{}\"".format(decline_approach_text))
            # Robot remains in public zone

        reset_arm()
        goodbye_text = "Goodbye for now!"
        try:
            pepper_cmd.robot.say(goodbye_text)
        except AttributeError: print("Pepper (sim) says: \"{}\"".format(goodbye_text))

        if initial_connection_successful and motion_service:
            motion_service.rest()

    except KeyboardInterrupt:
        print("\n[Main] Interaction interrupted by user (Ctrl+C). Shutting down...")
        try: tornado.ioloop.IOLoop.current().stop()
        except: pass
    except Exception as e:
        print("\n--- [Main] UNEXPECTED ERROR DURING INTERACTION ---")
        print("    Error Type: {}\n    Error Details: {}".format(type(e).__name__, e))
        import traceback; traceback.print_exc()
        try: tornado.ioloop.IOLoop.current().stop()
        except: pass
        final_error_text = "Oops, something went wrong. I need to stop."
        try:
            if initial_connection_successful and pepper_cmd.robot: pepper_cmd.robot.say(final_error_text)
            else: print("Pepper (sim) says: \"{}\"".format(final_error_text))
        except: pass
    finally:
        print("Entering cleanup phase...")
        try:
            if initial_connection_successful and 'end' in globals() and callable(end) and end != end_dummy:
                print("Closing Pepper connection...")
                end()
        except Exception: pass
        try:
            ioloop_instance = tornado.ioloop.IOLoop.current(instance=False)
            if ioloop_instance and ioloop_instance._running: ioloop_instance.stop()
        except Exception: pass
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