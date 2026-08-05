import cv2
import os
import rclpy
import subprocess
import threading # Added for background processing

from rclpy.node import Node
from std_msgs.msg import Int32, String, Empty
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class Panorama(Node):

	def __init__(self):
		super().__init__('pano_subscriber')

		# Parameters
		self.declare_parameter("pano_cam_id", "22")
		self.declare_parameter("base_ips", ["192.168.1.64", "192.168.1.65"])
		self.declare_parameter("base_user", "lenovo")
		self.declare_parameter("target_width", 800)
		self.declare_parameter("target_height", 800)

		self.pano_cam_id = self.get_parameter("pano_cam_id").value

		# Subscriptions
		self.pano_snap_subscription = self.create_subscription(Int32, 'pano', self.listener_callback, 10)
		self.Camera_manager_subscription = self.create_subscription(Image, '/image_topic', self.image_callback, 10)
		self.file_subscription = self.create_subscription(String, 'new_file', self.new_file, 10)
		self.image_request_sub = self.create_subscription(Empty, "request_image", self.request_callback, 10)

		self.current_image = None
		self.imgs = [] # Images will stay in RAM here
		self.br = CvBridge()
		
		# Folder setup
		self.folder_directory = 'src/science/daedalus_pano/daedalus_pano/daedalus_pano'
		self.folder_name = 'pano1'
		self.folder_path = os.path.join(self.folder_directory, self.folder_name)
		
		# Ensure base directory exists
		if not os.path.exists(self.folder_path):
			os.makedirs(self.folder_path, exist_ok=True)

	def new_file(self, msg: str):
		check_path = os.path.join(self.folder_directory, msg.data)
		if not os.path.isdir(check_path):
			os.mkdir(check_path)
		self.folder_name = msg.data
		self.folder_path = os.path.join(self.folder_directory, self.folder_name)
			
	def stitch_images(self, images):
		stitcher = cv2.Stitcher.create()
		(status, stitched_image) = stitcher.stitch(images)
		if status == cv2.STITCHER_OK:
			return stitched_image
		else:
			return None

	def crop_image(self, image):
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]
		contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
		x, y, w, h = cv2.boundingRect(contours[0])
		cropped_image = image[y:y + h, x:x + w]
		return cropped_image

	def process_and_send_panorama(self, images_to_stitch):
		""" Runs in a background thread. Stitches, crops, saves, and sends. """
		self.get_logger().info('Stitching process started...')
		
		stitched_image = self.stitch_images(images_to_stitch)
		if stitched_image is None:
			self.get_logger().error('Stitching failed! Images might not have enough overlap.')
			return

		cropped_image = self.crop_image(stitched_image)

		# Save the final stitched image
		output_filename = os.path.join(self.folder_path, self.folder_name + '_panorama.jpg')
		cv2.imwrite(output_filename, cropped_image)
		self.get_logger().info(f'Saved panorama to: {output_filename}')

		# Automatically trigger the SCP send after saving
		self.send_via_scp(output_filename)

	def snap_image(self, img: Image):
		try:
			# Convert ROS Image to CV2
			cv_img = self.br.imgmsg_to_cv2(img_msg=img, desired_encoding='bgr8')
			
			# Resize immediately to save RAM and future processing time
			target_w = self.get_parameter("target_width").value
			target_h = self.get_parameter("target_height").value
			resized_img = cv2.resize(cv_img, (target_w, target_h))
			
			# Store in memory
			self.imgs.append(resized_img)
			
			# Backup save to disk (Optional, but good for debugging)
			image_name = str(len(self.imgs) - 1)
			output_image_path = os.path.join(self.folder_path, f"{image_name}.jpg")
			cv2.imwrite(output_image_path, resized_img)
			
			self.get_logger().info(f'Snapped image {image_name}')
		except Exception as e:
			self.get_logger().error(f'Failed to snap image: {e}')

	def clear_imgs(self):
		self.imgs = []
		self.get_logger().info('Cleared image memory.')

	def listener_callback(self, msg):
		if msg.data == 0:
			if self.current_image is not None:
				self.snap_image(self.current_image)
			else:
				self.get_logger().warn('Received snap command, but no image is currently available on /image_topic')
		elif msg.data == 1:
			# Check if there are at least two images in memory
			if len(self.imgs) < 2:
				self.get_logger().error('Not enough images in memory to stitch.')
				return
				
			# Create a copy of the list for the thread, so we don't mutate it if new snaps arrive
			images_copy = list(self.imgs)
			
			# Offload to background thread so ROS keeps spinning
			stitch_thread = threading.Thread(target=self.process_and_send_panorama, args=(images_copy,))
			stitch_thread.start()

		elif msg.data == 2:
			self.clear_images()

	def image_callback(self, msg: Image):
		if msg.header.frame_id == str(self.pano_cam_id):
			self.current_image = msg

	def request_callback(self, msg):
		""" Manual request to resend the current panorama """
		image_loc = os.path.join(self.folder_path, self.folder_name + '_panorama.jpg')
		if not os.path.exists(image_loc):
			self.get_logger().error(f"No Panorama found at {image_loc}")
			return
		
		# Offload SCP to thread to prevent blocking
		scp_thread = threading.Thread(target=self.send_via_scp, args=(image_loc,))
		scp_thread.start()

	def send_via_scp(self, image_loc):
		""" Executes the SCP transfer """
		ips = self.get_parameter("base_ips").value
		name = self.get_parameter("base_user").value
		
		for ip in ips:
			self.get_logger().info(f"Attempting to send to {ip}...")
			data = subprocess.run(["sshpass", "-p", name, "scp", image_loc, f"{name}@{ip}:/home/{name}/Desktop"])
			if data.returncode == 0:
				self.get_logger().info(f"Successfully sent to {ip}")
			else:
				self.get_logger().error(f"Failed to send to {ip}")

def main(args=None):
	rclpy.init(args=args)
	panoSubscriber = Panorama()
	rclpy.spin(panoSubscriber)
	rclpy.shutdown()

if __name__ == '__main__':
	main()
