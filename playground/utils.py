# -*- coding: utf-8 -*-
import sys,os
import tornado.ioloop, tornado.websocket, tornado.httpserver
import threading, time
from threading import Timer 
import select
import random, re

############################################# SHARED CONSTANTS #####################################################
# Set the Server IP as the local host (of my PC)
IPAddress = "0.0.0.0" # ACCEPT ALL CONNECTIONS 
server_port = "8888"
websocket_address = "ws://"+IPAddress+":"+ server_port + "/websocket"
print("The server has address: " + websocket_address)

# Pepper robot simulation connection 
session = None
tts_service = None

#import socket
# SERVER IP
# Get the external IP address
#s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#s.connect(("0.0.0.0", 80))  
#IPAddress = s.getsockname()[0]
#IPAddress = "10.0.2.2" # STANDARD FOR ANDROID STUDIO
#print('Your Computer IP Address is: ' + IPAddress)

############################################ PLANNING CONSTANTS ####################################################
algorithm_name= "ehs"
heuristic_name= "landmark"

############################################ TIMED INPUT FUNCTION #################################################
timeout = 10 # global timeout set to 10 seconds
# Function that returns None if no input is received 
def input_with_timeout(prompt, timeout):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        return sys.stdin.readline().strip()
    else:
        return None

########################################### UTILITY SHOWS ACTIVE THREADS ##########################################
def print_active_threads():
    print("Active threads:", threading.active_count())
    print("Thread IDs:", threading.enumerate())

############################################# PEPPER  SENTENCES ####################################################
def sentences(index):
    sentence = [
        "I am here to help you",
        # EASY QUESTIONS
        "Hi! Do you need any assistance from me?",
        "Was your day a good one so far?",

        # MEDIUM QUESTIONS
        "What did you have for breakfast?",
        "Where would you like to go?",
        "How old are you?",
        "What is your family name?",
        "In what year are we in?",

        # HARD QUESTIONS
        "In what year were you born?",
        "Where were you born?",
        "In what city are we in?",
        "In what country are we in?",
        "Did you use to practice any sport?",
        "Do you have any siblings?",
        "Do you have any children?"
    ]
    return sentence[index]

####################################### RETURN CONFUSION STRING ###############################################
def confusion_states(index):
    confusion = [
            "easy",
            "medium",
            "hard" 
        ]
    return confusion[index]

######################################## POSITIVE SENTENCES ############################################
def good_sentences():
    good_sentences = [
        "That's right!",
        "Well said!",
        "Well done!"
    ]
    return random.choice(good_sentences)

######################################## BAD SENTENCES ############################################
def bad_sentences():
    bad_sentences = [
        "Hmm, that does not seem right...",
        "I see...",
        "Hmm, that’s something to think about."
    ]
    return random.choice(bad_sentences)

