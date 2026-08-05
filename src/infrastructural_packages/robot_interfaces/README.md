# Robot Interfaces Package
This Package houses many of the custom message, service, and action types used by the rest of the code. It provides a centralized place for any non-package specific communications

## Nodes
- None

## Messages
| Message | Description / Purpose |
| --- | --- |
| `CameraManagerCommand` | A message designed for commands sent to the camera manager, includes quality setting and various attributes |
| **`DrillDirection`** | A message designed to set both the direction and speed of the science drill |
| `DynamixelData` | A message designed for sending data between the Briance and the dynamixel controller |
| `Example` | An example message containing only a string |
| `ImageMetadata` | A message used for Yolo distance detection, contains various camera intrinsics |
| **`MotorData`** | A message designed to set both the direction and speed of the science drill, as well as the scoops |
| `ObjectData` | A message designed to represent an object in 3D space relative to a given camera frame, used for autonomy |
| `PicoData` | A message designed to share data between the Briance and the Pico interface node |
| `Pose2DArray` | A 2D version of the geometry_msgs PoseArray |
| `SpectrometerData` | A message designed to send spectrometer data back to the gui |
| `SpectrometerParams` | A message designed to tell the spectrometer what to do |
| `Waypoint` | A message used to send autonomy goals from the GUI to the waypoint manager |

## Services
| Service | Description / Purpose |
| --- | --- |
| `Example` | An example service that takes a string as an input, and returns a string as an output |

## Actions
| Action | Description / Purpose |
| --- | --- |
| `Example` | An example action that takes a string as an input, uses a string for feedback, and returns a string as output |