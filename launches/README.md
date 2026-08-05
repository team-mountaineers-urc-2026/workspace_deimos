# Daedalus Launch Files:

## How To Run a Launch File

After successfully building the workspace, launch files can now be accessed and executed.

To run the launch files, navigate to the root of the workspace and run the following commands:
```bash
source install/setup.bash
```
Now you can execute the following launch files using the following command:
```bash
ros2 launch launches/<launch_category>/<launch_file_name>
```

The possible launch categories are:
- `base_station`  → Launch Files to be run on a Base Station Computer
- `daedalus`      → Launch Files to be run on Daedalus
- `heimdall`      → Launch Files to be run on Heimdall
- `wanderer2`     → Launch Files to be run on wanderer2
- `testing`       → Launch Files created to be used for temporary testing
- `components`    → Launch Files that are used for general purposes

## Current Launch Files

Details about each current launch file should be included in a comment section located above the import statements