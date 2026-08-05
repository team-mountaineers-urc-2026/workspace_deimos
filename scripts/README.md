# This Directory is for any scripts not in Packages or Libraries

# Comms
The comms scripts in this directory are as follows
| Script | Enabled | Purpose | 
| ------ | ------- | ------- |
| print_signal_strength | `TRUE` | Prints the RX signal strength of the Base and Rover Antennas (2.4 GHz) once every 3 seconds. As Nate P writes, this is jank but it works |
| set_frequencies | `FALSE` | This script when run would set the valid channel values for the Base and Rover Antennas (2.4 GHz). It is disabled because while it does set the available frequencies, it also resets every other setting the radios have |

# Rosbags
The rosbag scripts in this directory are as follows
| Script | Enabled | Purpose | 
| ------ | ------- | ------- |
| rosbag_recovery | `TRUE` | This script generates a metadata file for a given .db3 file. When run with the path to said .db3 file as the only argument, it will create a metadata.yaml file in the same directory with all the appropriate information filled |