import os, sys
import math
import time
import random
sys.path.append(os.getenv('PEPPER_TOOLS_HOME')+'/cmd_server')

import pepper_cmd
from pepper_cmd import *
import functools

#our imports:
#from memory_game import *

#game = None
#SIMULATION = False

begin()
motion_proxy = ALProxy("ALMotion", pepper_cmd.robot.ip, pepper_cmd.robot.port)
animated_speech_proxy = ALProxy("ALAnimatedSpeech", pepper_cmd.robot.ip, pepper_cmd.robot.port)

# Disable autonomous life mode
autonomous_life_proxy = ALProxy("ALAutonomousLife", pepper_cmd.robot.ip, pepper_cmd.robot.port)
autonomous_life_proxy.setState("disabled")

# Set Pepper to the "Stand" posture
posture_proxy = ALProxy("ALRobotPosture", pepper_cmd.robot.ip, pepper_cmd.robot.port)
posture_proxy.goToPosture("Stand", 0.5)  # 0.5 is the speed (0 to 1)

# Initialize proxies
motion_proxy = ALProxy("ALMotion", pepper_cmd.robot.ip, pepper_cmd.robot.port)
animated_speech_proxy = ALProxy("ALAnimatedSpeech", pepper_cmd.robot.ip, pepper_cmd.robot.port)


def wave_hello():
    # Wake up the robot if it's in rest mode
    #motion_proxy.wakeUp()

    # Set stiffness to make the robot ready for movement
    motion_proxy.setStiffnesses("RArm", 1.0)

    # Define the wave motion
    names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]
    angles = [0.0, -0.2, 1.0, 1.0, 0.0]  # Adjust these angles for the desired wave motion
    times = [1.0, 1.0, 1.0, 1.0, 1.0]
    motion_proxy.angleInterpolation(names, angles, times, True)

    # Reset stiffness after the motion
    motion_proxy.setStiffnesses("RArm", 0.0)

def reset_arm():
    # Set stiffness to make the robot ready for movement
    motion_proxy.setStiffnesses("RArm", 1.0)

    # Define the initial pose for the arm
    names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]
    angles = [1.5, -0.2, 1.0, 0.5, 0.0]  # Default arm position
    times = [1.0, 1.0, 1.0, 1.0, 1.0]  # Time to reach the position
    motion_proxy.angleInterpolation(names, angles, times, True)

    # Reset stiffness after the motion
    motion_proxy.setStiffnesses("RArm", 0.0)
    

pepper_cmd.robot.say('CIAOO!!')
pepper_cmd.robot.say('CIAO!!')
pepper_cmd.robot.say('CIAO !!')

#PEPPER_CMD.ROBOT.SAY(RANDOM.CHOICE((
#"UIIIII ...",
#"GOODNIGHT...",
#"CUDDLES...?"
#)))

#reset_arm()

wave_hello()

# Make Pepper say something while the gesture is happening
pepper_cmd.robot.say("GOODMORNING!")
pepper_cmd.robot.say("GOODMORNING!")
pepper_cmd.robot.say("GOODMORNING!")

# Reset the arm to the initial pose
reset_arm()

#def pepper_turn(agent):

autonomous_life_proxy.setState("solitary")    

end()
