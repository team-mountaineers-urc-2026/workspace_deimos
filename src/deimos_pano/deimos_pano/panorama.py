import cv2
import os
import rclpy
import subprocess
import threading # Added for background processing
import time
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import Vector3
from rclpy.callback_groups import ReentrantCallbackGroup
import json
from std_msgs.msg import String, Empty
import datetime


class Panorama(Node):

	def __init__(self):
		super().__init__('pano_subscriber')

		self.cb_group = ReentrantCallbackGroup()

		# Parameters
		self.declare_parameter("pano_cam_id", "22")
		self.declare_parameter("base_ips", ["192.168.1.64", "192.168.1.65"])
		self.declare_parameter("base_user", "lenovo")
		self.declare_parameter("target_width", 800)
		self.declare_parameter("target_height", 800)

		self.pano_cam_id = self.get_parameter("pano_cam_id").value

		# Subscriptions — all with cb_group
		self.pano_snap_subscription = self.create_subscription(
			String, 'pano', self.listener_callback, 10, callback_group=self.cb_group
		)
		self.Camera_manager_subscription = self.create_subscription(Image, '/image_topic', self.image_callback, 10, callback_group=self.cb_group)
		self.file_subscription = self.create_subscription(String, 'new_file', self.new_file, 10, callback_group=self.cb_group)
		self.image_request_sub = self.create_subscription(Empty, "request_image", self.request_callback, 10, callback_group=self.cb_group)
		self.capture_frame_sub = self.create_subscription(String, 'capture_frame', self.capture_frame_callback, 10, callback_group=self.cb_group)
		self.gps_sub = self.create_subscription(NavSatFix, '/mavros/global_position/global', self.gps_callback, 10, callback_group=self.cb_group)
		self.heading_sub = self.create_subscription(Vector3, '/health_monitor/chassis_orientation', self.heading_callback, 10, callback_group=self.cb_group)

		self.gimbal_image = None
		self.belly_image  = None
		self.GIMBAL_CAM_ID = "39"
		self.BELLY_CAM_ID  = "40"
		self.arbitrary_frames = {}
		self.current_image = None
		self.imgs = []
		self.br = CvBridge()

		self.latitude = None
		self.longitude = None
		self.altitude = None
		self.heading = None

		self.folder_directory = 'src/science/daedalus_pano/daedalus_pano/daedalus_pano'
		self.folder_name = 'pano1'
		self.folder_path = os.path.join(self.folder_directory, self.folder_name)

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

	def process_and_send_panorama(self, images_to_stitch, lat, lon, alt, heading):
		""" Runs in a background thread. Stitches, crops, saves, and sends. """
		self.get_logger().info('Stitching process started...')

		stitched_image = self.stitch_images(images_to_stitch)
		if stitched_image is None:
			self.get_logger().error('Stitching failed! Images might not have enough overlap.')
			return

		cropped_image = self.crop_image(stitched_image)

		def get_cardinal(deg):
			cardinals = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
						'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N']
			return cardinals[round(deg / 22.5) % 16]

		cardinal = get_cardinal(heading) if heading is not None else "N/A"
		lines = [
			f"Lat:     {lat:.6f}"                      if lat     is not None else "Lat:     N/A",
			f"Lon:     {lon:.6f}"                      if lon     is not None else "Lon:     N/A",
			f"Alt:     {alt:.1f} m"                    if alt     is not None else "Alt:     N/A",
			f"Heading: {heading:.1f} deg ({cardinal})" if heading is not None else "Heading: N/A",
		]

		font, font_scale, thickness = cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
		padding, line_height = 10, 28

		max_w = max(cv2.getTextSize(line, font, font_scale, thickness)[0][0] for line in lines)
		block_h = line_height * len(lines) + padding
		box_x1, box_y1 = padding - 6, padding - 6
		box_x2, box_y2 = padding + max_w + 6, padding + block_h + 6

		cv2.rectangle(cropped_image, (box_x1, box_y1), (box_x2, box_y2), (80, 80, 80), -1)
		cv2.rectangle(cropped_image, (box_x1, box_y1), (box_x2, box_y2), (0, 0, 0), 2)

		for i, line in enumerate(lines):
			y = padding + (i + 1) * line_height
			cv2.putText(cropped_image, line, (padding + 1, y + 1), font, font_scale, (0, 0, 0), thickness + 1)
			cv2.putText(cropped_image, line, (padding, y), font, font_scale, (255, 255, 255), thickness)

		output_filename = os.path.join(self.folder_path, self.folder_name + '_panorama.jpg')
		cv2.imwrite(output_filename, cropped_image)
		self.get_logger().info(f'Saved panorama to: {output_filename}')

		meta_filename = os.path.join(self.folder_path, self.folder_name + '_metadata.txt')
		with open(meta_filename, 'w') as f:
			f.write(f"latitude:  {lat}\n")
			f.write(f"longitude: {lon}\n")
			f.write(f"altitude:  {alt}\n")
			f.write(f"heading:   {heading}\n")
			f.write(f"cardinal:  {cardinal}\n")
		self.get_logger().info(f'Saved metadata to: {meta_filename}')

		self.clear_imgs()
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

	def gps_callback(self, msg):
		self.latitude = msg.latitude
		self.longitude = msg.longitude
		self.altitude = msg.altitude

	def heading_callback(self, msg):
		# Same conversion as PoseData.jsx
		self.heading = (-msg.z * (180 / 3.141592653589793) + 360) % 360

	def clear_imgs(self):
		self.imgs = []
		self.get_logger().info('Cleared image memory.')

	

	def capture_frame_callback(self, msg: String):
		try:
			payload = json.loads(msg.data)
			name    = payload['camera'].strip().lower()
			lat     = payload.get('lat')
			lon     = payload.get('lon')
			alt     = payload.get('alt')
			heading = payload.get('heading')
		except (json.JSONDecodeError, KeyError):
			name    = msg.data.strip().lower()
			lat, lon, alt, heading = self.latitude, self.longitude, self.altitude, self.heading

		if name == "gimbal":
			ros_image, label = self.gimbal_image, "gimbal"
		elif name == "belly":
			ros_image, label = self.belly_image, "belly"
		elif name.isdigit():
			ros_image = self.arbitrary_frames.get(name)
			label = f"cam{name}"
		else:
			self.get_logger().warn(f"capture_frame: unknown camera '{name}'")
			return
		if ros_image is None:
			self.get_logger().error(f"capture_frame: no frame yet for '{name}'")
			return

		threading.Thread(
			target=self.process_and_send_frame,
			args=(ros_image, label, lat, lon, alt, heading)
		).start()


	def get_next_frame_index(self, label):
		i = 1
		while os.path.exists(os.path.join(self.folder_path, f"{label}_frame_{i}.png")):
			i += 1
		return i

	def process_and_send_frame(self, ros_image: Image, label: str, lat, lon, alt, heading):
		try:
			cv_img = self.br.imgmsg_to_cv2(img_msg=ros_image, desired_encoding='bgr8')
		except Exception as e:
			self.get_logger().error(f"capture_frame: conversion failed: {e}")
			return

		# Upscale to 1280 wide preserving aspect ratio
		target_w = 1280
		h, w = cv_img.shape[:2]
		scale = target_w / w
		frame = cv2.resize(cv_img, (target_w, int(h * scale)), interpolation=cv2.INTER_CUBIC)
		h, w = frame.shape[:2]

		# Use a smaller scale so the box doesn't dominate the image
		scale_factor = w / 2400.0  # was 800.0, now smaller relative size
		font = cv2.FONT_HERSHEY_SIMPLEX
		font_scale = 0.6 * scale_factor
		thickness = max(1, int(1 * scale_factor))
		padding = int(8 * scale_factor)
		line_height = int(22 * scale_factor)


		def get_cardinal(deg):
			cardinals = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
						'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N']
			return cardinals[round(deg / 22.5) % 16]

		lat_err = abs(lat  * 0.02) if lat  is not None else None
		lon_err = abs(lon  * 0.02) if lon  is not None else None
		alt_err = abs(alt  * 0.02) if alt  is not None else None
		cardinal = get_cardinal(heading) if heading is not None else "N/A"
		lines = [
			f"Lat:     {lat:.6f} +/- {lat_err:.6f} deg" if lat     is not None else "Lat:     N/A",
			f"Lon:     {lon:.6f} +/- {lon_err:.6f} deg" if lon     is not None else "Lon:     N/A",
			f"Alt:     {alt:.1f} +/- {alt_err:.1f} m"   if alt     is not None else "Alt:     N/A",
			f"Heading: {heading:.1f} deg ({cardinal})"   if heading is not None else "Heading: N/A",
		]

		max_w = max(cv2.getTextSize(line, font, font_scale, thickness)[0][0] for line in lines)
		block_h = line_height * len(lines) + padding
		box_x1, box_y1 = padding - 6, padding - 6
		box_x2, box_y2 = padding + max_w + 6, padding + block_h + 6

		cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (80, 80, 80), -1)
		cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (0, 0, 0), 2)

		for i, line in enumerate(lines):
			y = padding + (i + 1) * line_height
			cv2.putText(frame, line, (padding + 1, y + 1), font, font_scale, (0, 0, 0), thickness + 1)
			cv2.putText(frame, line, (padding, y), font, font_scale, (255, 255, 255), thickness)

		idx = self.get_next_frame_index(label)
		output_path = os.path.join(self.folder_path, f"{label}_frame_{idx}.png")
		cv2.imwrite(output_path, frame)
		self.get_logger().info(f"capture_frame: saved {output_path}")
		meta_path = os.path.join(self.folder_path, f"{label}_frame_metadata_{idx}.txt")		
		with open(meta_path, 'w') as f:
			f.write(f"camera:    {label}\n")
			f.write(f"latitude:  {lat}\n")
			f.write(f"longitude: {lon}\n")
			f.write(f"altitude:  {alt}\n")
			f.write(f"heading:   {heading}\n")
			f.write(f"cardinal:  {cardinal}\n")
		self.send_via_scp(output_path)



	def listener_callback(self, msg):
		try:
			payload = json.loads(msg.data)
			command = payload.get('command')
			lat     = payload.get('lat', self.latitude)
			lon     = payload.get('lon', self.longitude)
			alt     = payload.get('alt', self.altitude)
			heading = payload.get('heading', self.heading)
		except (json.JSONDecodeError, TypeError):
			try:
				command = int(msg.data)
			except ValueError:
				return
			lat, lon, alt, heading = self.latitude, self.longitude, self.altitude, self.heading

		if command == 0:
			if self.current_image is not None:
				self.snap_image(self.current_image)
			else:
				self.get_logger().warn('No image available on /image_topic')
		elif command == 1:
			if len(self.imgs) < 2:
				self.get_logger().error('Not enough images in memory to stitch.')
				return
			images_copy = list(self.imgs)
			stitch_thread = threading.Thread(
				target=self.process_and_send_panorama,
				args=(images_copy, lat, lon, alt, heading)
			)
			stitch_thread.start()
		elif command == 2:
			self.clear_imgs()
	def image_callback(self, msg: Image):
		frame_id = msg.header.frame_id
		if frame_id == str(self.pano_cam_id):
			self.current_image = msg
		if frame_id == self.GIMBAL_CAM_ID:
			self.gimbal_image = msg
		if frame_id == self.BELLY_CAM_ID:
			self.belly_image = msg
		# Store latest frame for every camera ID seen
		self.arbitrary_frames[frame_id] = msg

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
	executor = rclpy.executors.MultiThreadedExecutor()
	executor.add_node(panoSubscriber)
	executor.spin()
	rclpy.shutdown()

if __name__ == '__main__':
	main()
