import time
from naoqi import ALProxy

def move_to_position(proxy_motion, x, y, theta):
    # Moves Pepper to the (x, y, theta) position
    # x, y are in meters, theta is in radians (orientation of the robot)
    proxy_motion.moveTo(x, y, theta)

def perform_dance(proxy_animation):
    # Play a dance animation (e.g., "Stand" animation as a placeholder)
    # Replace with a specific dance animation ID or a predefined dance
    proxy_animation.runBehavior("StandUp")
    time.sleep(1)  # Give time to complete the stand-up
    proxy_animation.runBehavior("Wave")
    time.sleep(5)  # Give time for the dance
    proxy_animation.runBehavior("Sit")

def main():
    # Connect to the robot using the NAOqi APIs
    try:
    	motion_proxy = ALProxy("ALMotion", "<pepper_ip>", 9559)
    	animation_proxy = ALProxy("ALAnimationPlayer", "<pepper_ip>", 9559)
    except Exception as e:
    	print("Error connecting to proxies: {}".format(e))
    	import traceback
    	traceback.print_exc()
    
    # Start the movement from point A to point B
    print("Moving from Point A to Point B")
    move_to_position(motion_proxy, 2.0, 0.0, 0.0)  # Example coordinates

    # Wait for the robot to reach the destination (you might want to check position in real-time)
    print("Arrived at Point B. Starting the dance.")
    perform_dance(animation_proxy)

    print("Dance complete.")

if __name__ == "__main__":
    main()
