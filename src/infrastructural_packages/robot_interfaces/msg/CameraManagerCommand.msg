# Type of command
# 0 - local start
# 1 - stream start
# 2 - local stop
# 3 - stream stop
# 4 - force camera restart
# 5 - set camera attribute
uint8 command_type

# Camera ID
# Positive - corresponds to logitech camera number
# -1 - Wrist camera (realsense)
int8 camera_id

# Quality number
# See enum clarity in settings.hpp
# 0-10 at time of writing.
uint8 quality

# Camera attribute number
# Brightness - 0
# Contrast - 1
# Saturation - 2
# Sharpness - 3
# Gain - 4 (doesn't really work)
# Auto white balance - 5 (also doesn't really work)
# There may be more after this is written - c++ headers in CameraManager
uint8 attribute

# Value for the attribute
# Default values are enforced on startup of a camera
# Suggested or modification values should be included as part of the GUI
# 0-255 for most attributes, toggles are typically 0 or 1.
# Check each attribute specifically, and changed this to signed if needed.
uint8 attr_value
