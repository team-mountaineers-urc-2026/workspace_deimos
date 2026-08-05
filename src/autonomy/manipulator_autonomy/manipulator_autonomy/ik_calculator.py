import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from sensor_msgs.msg import JointState
import numpy as np
import key_offsets
import math

DEG_PER_M = 44500

class ArmParameters():
    def __init__(self, l1, l2, l3):
        self.links = (l1, l2, l3)

        self.offsets = (None, None, None)
        self.rail_offset = None
        self.rail_value = None

        self.thetas = (None, None, None)

    def set_theta(self, joint : int, arm_angle : float):

        # Update the Thetas
        shifted_theta = arm_angle + self.offsets[joint - 1]
        self.theta[joint - 1] = shifted_theta % 360

        # Update the Phi's

    def get_theta(self, joint : int):
        return self.thetas(joint - 1)

    def get_phi(self, joint : int):
        match joint:

            case 1 :
                if self.thetas(0) == None: return None
                return self.thetas(0)
            
            case 2:
                if self.thetas(0) == None or self.thetas(1) == None: return None
                return self.thetas(0) + self.thetas(1)
            
            case 3:
                if self.thetas(0) == None or self.thetas(1) == None or self.thetas(2) == None: return None
                return self.thetas(0) + self.thetas(1) + self.thetas(2)

    def theta_phi_to_goal(self, theta1, phi2, translation):
        goal_pos = {
            'shoulder' : theta1 + self.offsets(0),
            'elbow' : theta1 - phi2 - self.offsets(1),
            'wrist_pitch' : phi2 - 2*theta1 - self.offsets(2),
            'wrist_roll' : 0,
            'linear_rail' : translation * DEG_PER_M - self.rail_offset,
        }

        return goal_pos

class IKCalculator(Node):

    def __init__(self):
        super().__init__('ik_calculator')
        
        self.current_key = None
        self.current_js = None
        self.arm = ArmParameters(0.2, 0.2, 0.1)

        # Arm pos subscriber
        self.pose_sub = self.create_subscription(
            JointState,
            'joint_pos',
            self.set_current_js,
            10
        )

        # Go to next key
        self.key_sub = self.create_subscription(
            String,
            'next_key',
            self.set_current_key,
            10
        )

        # Arm goal pos publisher
        self.goal_pos_pub = self.create_publisher(
            JointState,
            'goal_pos',
            10
        )

    def set_current_key(self, msg : String):
        self.current_key = msg.data

    def set_current_js(self, msg : JointState):

        for i in range(len(msg.name)):
            match msg.name[i]:
                case 'shoulder':
                    self.arm.set_theta(1, msg.position[i])

                case 'elbow':
                    self.arm.set_theta(2, msg.position[i])

                case 'pitch':
                    self.arm.set_theta(3, msg.position[i])

                case 'rail':
                    self.arm.rail_value = msg.position[i]

    def get_next_js(self, next_key : str):

        current_offset = key_offsets.dist_out(self.current_key)
        goal_from_origin = key_offsets.dist_out(next_key)

        goal_offset = (goal_from_origin[0] - current_offset[0], goal_from_origin[1] - current_offset[1])

        # Get the current pose and modify it with the goal offset
        cur_pose = self.fwd_kinematics()

        goal_pos = (cur_pose[0], cur_pose[1] + goal_offset[0], cur_pose[2] + goal_offset[1])

        # Feed goal pose
        goal_pose = self.inverse_kinematics(goal_pos)

        goal_JS = JointState()
        goal_JS.name = ['shoulder', 'elbow', 'wrist_pitch', 'wrist_roll', 'linear_rail']
        for name in goal_JS.name:
            goal_JS.position.append(goal_pose.get(name))

        self.goal_pos_pub.publish(goal_JS)

    def fwd_kinematics(self):
        x = self.arm.link1 * math.cos(self.arm.get_theta(1)) + self.arm.link_2 * math.cos(self.arm.get_phi(2)) + self.arm.link_3 * math.cos(self.arm.get_phi(3))
        y = self.arm.link1 * math.sin(self.arm.get_theta(1)) + self.arm.link_2 * math.sin(self.arm.get_phi(2)) + self.arm.link_3 * math.sin(self.arm.get_phi(3))
        z = self.joints.get('rail')

        return (x,y,z)
    
    def inverse_kinematics(self, goal_pose):

        # Define the functions
        f = lambda theta1, phi2, phi3: self.arm.link1 * math.cos(theta1) + self.arm.link_2 * math.cos(phi2) + self.arm.link_3 * math.cos(phi3) - goal_pose[0]
        g = lambda theta1, phi2, phi3: self.arm.link1 * math.sin(theta1) + self.arm.link_2 * math.sin(phi2) + self.arm.link_3 * math.sin(phi3) - goal_pose[1]

        df_dtheta1  = lambda theta1: self.arm.link1 * -math.sin(theta1)
        df_dphi2    = lambda phi2:   self.arm.link2 * -math.sin(phi2)
        dg_dtheta1  = lambda theta1: self.arm.link1 * math.cos(theta1)
        dg_dphi2    = lambda phi2:   self.arm.link2 * math.sin(phi2)

        theta1_guess = self.arm.get_theta(1)
        phi2_guess = self.arm.get_phi(2)

        theta1 = theta1_guess
        phi2 = phi2_guess
        phi3 = 0 # Always parallel to ground

        for i in range(100):
            J = np.array([[df_dtheta1(theta1), df_dphi2(phi2)],
                          [dg_dtheta1(theta1), dg_dphi2(phi2)]])
            try:
                J_inv = np.linalg.inv(J)

            except np.linalg.LinAlgError:
                self.get_logger().error("Jacobian matrix is singular, Newton-Rhapson method fails.")

            F = np.array([f(theta1, phi2, phi3), g(theta1, phi2, phi3)])

            delta = np.dot(J_inv, F)
            theta1 -= delta[0]
            theta2 -= delta[1]
            if np.linalg.norm(delta) < 0.01:
                break

            if i == 99:
                self.get_logger().error("Newton-Rhapson method did not converge")
                return None

        # If we got here, then we have an estimate for theta1 and phi2, adjust for real values
        goal_pos = self.arm.theta_phi_to_goal(theta1, phi2, goal_pos[1])
        return goal_pos

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1


def main(args=None):
    rclpy.init(args=args)

    ik_calculator = IKCalculator()

    rclpy.spin(ik_calculator)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    ik_calculator.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()