import rclpy
from rclpy.node import Node

from std_msgs.msg import String, Bool, Empty, Float32
from sensor_msgs.msg import JointState
import numpy as np
from numpy import sign
import math
from time import time, sleep

column_dist = 0.02 # meters
row_dist = 0.02
first_row_offset = 0.011
second_row_offset = 0.015

key_offsets = {
    "Q" : (0,0),
    "W" : (0,1),
    "E" : (0,2),
    "R" : (0,3),
    "T" : (0,4),
    "Y" : (0,5),
    "U" : (0,6),
    "I" : (0,7),
    "O" : (0,8),
    "P" : (0,9),
    "A" : (1,0),
    "S" : (1,1),
    "D" : (1,2),
    "F" : (1,3),
    "G" : (1,4),
    "H" : (1,5),
    "J" : (1,6),
    "K" : (1,7),
    "L" : (1,8),
    "Z" : (2,0),
    "X" : (2,1),
    "C" : (2,2),
    "V" : (2,3),
    "B" : (2,4),
    "N" : (2,5),
    "M" : (2,6),
}

# Outputs cartesian relative distance from the Q key
def dist_out(key : str):
    row, col = key_offsets.get(key)
    delta_x = col * column_dist # horizontal distance
    delta_z = -row * row_dist # vertical distance
    if row == 1:
        delta_x = delta_x + first_row_offset
    elif row == 2:
        delta_x = delta_x + second_row_offset
    return delta_x, delta_z

class KeyManager(Node):

    def __init__(self):
        super().__init__('key_manager')
        self.publisher_ = self.create_publisher(String, 'topic', 10)

        self.word = ""
        self.index = 0
        self.goal_pos = 0
        self.current_pos = 0
        self.auto_state = "START"
        self.goal_letter = ""
        self.timer_time = 0
        self.start_key = ""
        self.goal_angle = 0.0
        self.start_angle = 0.0
        self.current_angle = 0.0

        self.word_subscriber = self.create_subscription(
            String,
            'word_to_spell',
            self.save_word,
            10
        )

        self.autonomy_loop = self.create_timer(
            0.1,
            self.auto_loop_callback
        )
        self.autonomy_loop.cancel()

        self.speed_publisher = self.create_publisher(
            JointState,
            '/manipulator/joint_vel',
            10
        )

        self.solenoid_publisher = self.create_publisher(
            Bool,
            '/manipulator/solenoid_control',
            10
        )

        self.start_key_sub = self.create_subscription(
            String,
            '/manipulator/original_key',
            self.set_start_key,
            10
        )

        self.autonomy_led_pub = self.create_publisher(
            Bool,
            'is_autonomous',
            10
        )

        self.enable_sub = self.create_subscription(
            Bool,
            'enable_autonomy',
            self.enable_auto,
            10
        )

        self.restart_sub = self.create_subscription(
            Empty,
            'restart_autonomy',
            self.restart_auto,
            10
        )

        self.update_pos = self.create_subscription(
            JointState,
            '/manipulator/joint_pos',
            self.current_pos_sub,
            10
        )

        self.update_angle = self.create_subscription(
            Float32,
            '/manipulator/wrist_pitch/position',
            self.current_angle_sub,
            10
        )

        self.position_pub = self.create_publisher(
            JointState,
            '/manipulator/next_pos',
            10
        )

    def set_start_key(self, msg : String):
        if len(msg.data) > 1:
            self.get_logger().error(f"Error: Input {msg.data} is not a single key")
            return
        
        if not (msg.data.upper() in key_offsets.keys()):
            self.get_logger().error(f"Error: Input {msg.data.upper()} not in known key offsets")
            return

        self.start_key = msg.data.upper()
        self.get_logger().info(f"Start Key Set To {self.start_key}")

    def save_word(self, msg : String):
        self.word = msg.data.upper()
        self.index = 0
        self.get_logger().info(f"Word Set To {self.word}")

    def restart_auto(self, msg : Empty):
        self.auto_state = "START"

    def enable_auto(self, auto_status : Bool):
        if auto_status.data:
            self.autonomy_led_pub.publish(Bool(data=True))
            self.autonomy_led_pub.publish(Bool(data=True))
            self.autonomy_led_pub.publish(Bool(data=True))

            # Not good practice, but we want to make sure the light changes color
            sleep(1)
            self.autonomy_loop.reset()
        else:
            self.autonomy_loop.cancel()
            self.autonomy_led_pub.publish(Bool(data=False))
            self.autonomy_led_pub.publish(Bool(data=False))
            self.autonomy_led_pub.publish(Bool(data=False))

    def current_angle_sub(self, angle : Float32):
        # self.get_logger().info(f"THIS IS THE CURRENT ANGLE: {angle.data}")
        self.current_angle = angle.data

    def current_pos_sub(self, state : JointState):
        if "linear_rail" in state.name:
            self.current_pos = state.position[state.name.index("linear_rail")]

    def auto_loop_callback(self):
        
        match self.auto_state:

            case "START" :
                # We are beginning for the first time
                self.index = 0

                # SAVE THE POSITION RIGHT NOW
                self.start_key_pos = self.current_pos
                self.start_angle = self.current_angle

                self.goal_pos = self.calculate_goal(self.word[self.index])
                self.goal_angle = self.calculate_angle(self.word[self.index])
                self.solenoid_publisher.publish(Bool(data=False))
                self.auto_state = "MOVING"
                self.get_logger().info(f"Started, now moving to {self.word[self.index]}, {self.goal_pos - self.current_pos:.5f} away")

            case "MOVING" :
                # We are moving to the goal key
                
                # Are we there yet?
                if abs(self.current_pos - self.goal_pos) < 0.001:
                    # Send speed zero
                    self.speed_publisher.publish(JointState(name=["linear_rail"], velocity=[0.0]))
                    at_lin = True

                else:
                    # publish to go to the same goal
                    # Negative is rail right
                    d_err = self.current_pos - self.goal_pos
                    if int(sign(d_err)) == -1:
                        p_vel = max(2500 * d_err - 100, -1000)

                    else:
                        p_vel = min(2500 * d_err + 100, 1000)

                    self.get_logger().info(f"Trying to send {p_vel} because c: {self.current_pos} is not g: {self.goal_pos}")
                    self.speed_publisher.publish(JointState(name=['linear_rail'], velocity=[p_vel]))
                    at_lin = False

                # Are we at the right angle?
                # self.get_logger().info(f"Goal Angle: {self.goal_angle}")
                # self.get_logger().info(f"Current Angle: {self.current_angle}")
                if abs(self.goal_angle - self.current_angle) > 0.1:
                    # self.position_pub.publish(JointState(name=['wrist_pitch'], position=[self.goal_angle]))
                    at_angle = True
                else:
                    # self.speed_publisher.publish(JointState(name=['wrist_pitch'], velocity=[0.0]))
                    at_angle = True

                # If we're here, move to the next state
                if at_lin and at_angle:
                    self.auto_state = "ARRIVED"
                    self.timer_time = time()
                    self.get_logger().info(f"Arrived at key {self.word[self.index]}")
                    self.get_logger().info(f"Beginning Wait")


            case "ARRIVED" :
                # We have arrived at the goal key

                # Check if we are still there
                if abs(self.current_pos - self.goal_pos) > 0.001:
                    self.get_logger().info("We have moved :(")
                    self.auto_state = "MOVING"

                # Wait for 3 seconds to make sure we aren't jiggling
                if time() - self.timer_time < 5:
                    self.speed_publisher.publish(JointState(name=["linear_rail"], velocity=[0.0]))
                else:
                    self.auto_state = "KEY_PRESS"
                    self.get_logger().info(f"Wait Done")
                    self.get_logger().info(f"Clicking Solenoid")
                    self.timer_time = time()

            case "KEY_PRESS" :
                # We are pressing the goal key
                if time() - self.timer_time <= 2:
                    # Fire the solenoid, wait 2 seconds, then retract it for 2 seconds
                    self.solenoid_publisher.publish(Bool(data=True))

                else:
                    self.auto_state = "KEY_UNPRESS"
                    self.get_logger().info(f"Solenoid Clicked")
                    self.get_logger().info(f"Unclicking Solenoid")
                    self.timer_time = time()

            case "KEY_UNPRESS" :
                # We are pressing the goal key
                if time() - self.timer_time <= 2:
                    # Fire the solenoid, wait 2 seconds, then retract it for 2 seconds
                    self.solenoid_publisher.publish(Bool(data=False))

                else:
                    self.auto_state = "CONTINUING"
                    self.get_logger().info(f"Solenoid Unclicked")
                    self.timer_time = time()

            case "CONTINUING" :
                # We are continuing to the next key
                self.index += 1

                if self.index >= len(self.word):
                    self.auto_state = "END"
                    return

                self.goal_pos = self.calculate_goal(self.word[self.index])
                self.goal_angle = self.calculate_angle(self.word[self.index])
                self.auto_state = "MOVING"
                self.get_logger().info(f"Now moving to {self.word[self.index]}, {self.goal_pos - self.current_pos:.5f} away")

            case "END" :
                # We have finished the word
                self.get_logger().info(f"Word {self.word} finished")
                self.enable_auto(Bool(data=False))

            case _ :
                self.get_logger().info(f"INVALID STATE \"{self.auto_state}\" REACHED")

    def calculate_goal(self, next_key : str):
        current_offset = dist_out(self.start_key)
        goal_from_origin = dist_out(next_key)

        # self.get_logger().info(f"Start Key Offset: {current_offset}")
        # self.get_logger().info(f"Goal Key Offset: {goal_from_origin}")

        goal_offset = goal_from_origin[0] - current_offset[0]
        return self.start_key_pos + goal_offset
        
    def calculate_angle(self, next_key : str):

        self.get_logger().info(f"Start Angle {self.start_angle}")
        self.get_logger().info(f"Next Key Value {key_offsets.get(next_key)[0]}")

        match key_offsets.get(next_key)[0]:


            case 0:
                return -self.start_angle

            case 1:
                return -self.start_angle - 1905

            case 2:
                return -self.start_angle - 10.0

def main(args=None):
    
    rclpy.init(args=args)
    key_manager = KeyManager()
    rclpy.spin(key_manager)
    key_manager.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
