#!/usr/bin/env python3
import cv2
from os import path
import time

def main():

    # Ask the user for the image name (Assume in same directory)
    filepath = input("What is the Image Name?\n")

    while not path.exists(filepath):
        filepath = input("Invalid filename, please try again. \n")


    # Ask the user for the Location
    latitude = input("What is the Latitude? ")
    longitude = input("What is the Longitude? ")
    altitude = input("What is the Altitude (meters)? ")
    heading = input("What is the Heading? (deg)? ")
    variance = input("What is the Variance? ")

    # Open the image and draw a box in the corner
    img = cv2.imread(filepath, cv2.IMREAD_COLOR)

    # get the height and width of the image
    im_height, im_width = img.shape[:2]

    # Get the box corners
    box_width = 500
    box_height = 220
    box_top_left = (20, im_height - 20 - box_height)
    box_lower_right = (20 + box_width, im_height - 20)

    cv2.rectangle(img, box_top_left, box_lower_right, (171, 233, 255), -1)
    cv2.rectangle(img, box_top_left, box_lower_right, (0, 0, 0), 3)

    VAR_OFFSET = 170

    cv2.putText(img, f"Latitude:", (10 + box_top_left[0], 40 + box_top_left[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(img, f"{latitude} N", (10 + box_top_left[0] + VAR_OFFSET, 40 + box_top_left[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(img, f"Longitude:", (10 + box_top_left[0], 80 + box_top_left[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(img, f"{longitude} W", (10 + box_top_left[0] + VAR_OFFSET, 80 + box_top_left[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(img, f"Altitude:", (10 + box_top_left[0], 120 + box_top_left[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(img, f"{altitude} (m)", (10 + box_top_left[0] + VAR_OFFSET, 120 + box_top_left[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(img, f"Heading:", (10 + box_top_left[0], 160 + box_top_left[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(img, f"{heading} (deg)", (10 + box_top_left[0] + VAR_OFFSET, 160 + box_top_left[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(img, f"Variance:", (10 + box_top_left[0], 200 + box_top_left[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(img, f"{variance}", (10 + box_top_left[0] + VAR_OFFSET, 200 + box_top_left[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

    cv2.imwrite(f"adj_pano_{time.ctime().replace(' ', '_')}.png", img)

    pass
    
if __name__ == "__main__":
    main()
