# Team Mountaineers Programming Setup Process
This ReadMe Document is Specifically for the 2025-2026 Competition Year


## Document Contents
- [Setting Up Ubuntu \(Virtual Machine)](#Setting-Up-Ubuntu-Virtual-Machine)
- [Using the Ubuntu Terminal](#using-the-ubuntu-terminal)
- [Setting Up Github](#setting-up-github)
- [Setting Up The URC Repo](#setting-up-the-urc-repo)
- [Making Your Own ROS2 Package](#making-your-own-ros2-package)
- [Running Code](#running-code)
- [Troubleshooting](#troubleshooting)

## Setting Up Ubuntu (Virtual Machine)

1. Download the URC-2026.ova from the Google Drive [Link](https://drive.google.com/drive/folders/100POtVLa4rvBCi5dp1wo0mRN9ubErJ1n)

2. Download the VirtualBox host associated with the operating system you are currently using [Download Page](https://www.virtualbox.org/wiki/Downloads) 
   - When installing, you may encounter a Python Binding Error, this is fine and you can ignore it.

3. Open VirtualBox and select 'Import Appliance' from the File Dropdown in the top left corner

4. Import the .ova file that you downloaded from the Google Drive

5. Click Next and Tweak the Appliance Settings as you see fit (the defaults should work for most people)

6. Wait while it imports

7. Run the Virtual Machine by double clicking the new entry in the list off to the left, the password is the same as the username (If you have trouble getting it functional, see [Troubleshooting](#VirtualBox)

## Using the Ubuntu Terminal

1. To begin using the Terminal, select the `>_` icon from the desktop sidebar
   ![Screenshot from 2024-11-01 09-53-52](https://github.com/user-attachments/assets/13b025c3-c947-423a-81b0-636f2ba93b9c)

3. The terminal should now look like like the picture below. The pre-printed text, or prompt, always follows the same format: `username@computername~:directory$`.\
The image below shows that the user `urc` running on the computer `URC` is at the `~` or `home` directory. The home directory can be thought of like the user folder from windows.
  ![image](https://github.com/user-attachments/assets/d4c52689-11f5-4e57-9019-b94694105cb2)

4. Important Commands to Know:
   - `$ ls` this command will list out all files and folders found in the current directory
   - `$ cd` this command will change your directory, there are several variations:
     - `$ cd`        running this command without arguments will place your terminal back in the home directory
     - `$ cd <folder>` running this command will move you into a given folder (`<folder>` found by running `$ ls`)
     - `$ cd ..`     running this command will move you out of the current folder, back up one level
   - `$ sudo <command>` this command (SuperUserDO) runs other commands with the highest permissions possible
     - When running a `$ sudo` command, you may be prompted for a password, the password will be the one associated with your account
     - Typing this password doesn't result in text showing for security reasons, but it is registering your keyboard inputs
    
5. Other Notes:
   - When copying and pasting from the terminal in Ubuntu 22.04, you must use `ctrl` + `shift` + `c` and `ctrl` + `shift` + `v`. If you forget the `shift` it will print strange characters on either side of the text
   - If you see `$` followed by a command of some kind, it means that this should be run in a terminal


## Setting Up GitHub

1. Open a new terminal and create and SSH Key by running the command `$ ssh-keygen`. Keep the default file path by pressing enter, and add a password if you want to (not strictly necessary).

2. Go to [https://github.com/settings/keys](https://github.com/settings/keys) and select the 'New SSH Key' button shown below.
  ![Screenshot from 2024-11-01 10-31-02](https://github.com/user-attachments/assets/e8fb9361-67a2-4bc7-aa29-fc7e298d42f3)


3. Title this key whatever you want but make sure the 'Key type' is 'Authentication Key'.

4. Run the command `$ cat ~/.ssh/id_rsa.pub` and Copy and paste its output into the 'Key' field and select 'Add SSH key'
![Screenshot from 2024-11-01 10-37-16](https://github.com/user-attachments/assets/9a341ea9-6753-4618-8167-1569b7c01a39)


5. Run the command `$ git config --global user.email "\<your email>"` to set the email associated with your commits

6. To set the username associated with your commits, run the command `$ git config --global user.name "\<your username>"`

## Setting Up The URC Repo

1. Open a new terminal by pressing the `+` icon in the top left of the terminal window and make sure you are in the `home` directory. (See [Using the Ubuntu Terminal](#using-the-ubuntu-terminal) for how to check and correct this)

2. Run the command `$ git clone git@github.com:wvu-urc/workspace-newrobot2026.git workspace-newrobot2026`. This command will clone the current repo into a folder named `$ workspace-daedalus` in your home directory. You can check this by running `$ ls` and making sure the output matches the image below.
![Git Clone Picture](https://github.com/user-attachments/assets/c20c2be7-d6f4-479e-a9be-56a59ddc2b1f)

3. Run the command `$ cd workspace-newrobot2026` to move the current terminal into the newly downloaded repo. Your terminal should now look similar to the one below.
![cd workspace pic](https://github.com/user-attachments/assets/2cd2f074-b791-4cf8-9b3c-a2d93040ade4)

4. Run the command `$ ./setup/install_humble.bash` to download ROS2 Humble and the other packages we use. This will take a while to install, 10-30 minutes in total depending on internet connection
- There are certain points when you will be prompted with the option `(Y/n)` or `(y/n)`. In both cases, type `y` into the terminal and hit enter to accept

5. Make sure you are still in the `$ workspace-newrobot2026` directory (`username@computer:~/workspace-newrobot2026$`). If you aren't, run the command `$ cd ~/workspace-newrobot2026`.

6. Run the command `$ source ~/.bashrc` to reload environment variables and give the current terminal access to ROS2.

7. Run the command `$ vcs import src < repos.yaml` to import all of the additional packages into the repo. Usually this will output text indicating the download of several packages, but two known failures can occur (See [Troubleshooting](#vcs-tool-isnt-working) for more information)

8. Install Additional Dependencies by running the command `$ rosdep install --from-paths src --ignore-src -r -y`. This will install all the specific dependencies that are in packages you just downloaded.

9. Compile the workspace by running `$ colcon build`. See [Troubleshooting](#errors-running-colcon-build) if you encounter errors or crashes.

10. After running the above commands, you should have a directory structure that follows something similar to this:
   ```
    /workspace-newrobot
       /build
       /install
       /launches
       /log
       /scripts
       /setup
       /src
   ```
   This can be checked by opening the Ubuntu File explorer and checking to see the contents of the `workspace-newrobot` folder
![File Directory Image](https://github.com/user-attachments/assets/8bbdb8f1-bef9-456e-8e20-0782482ea8b4)

## Making Your Own ROS2 Package

1. Go to [https://github.com/orgs/wvu-urc/repositories](https://github.com/orgs/wvu-urc/repositories) and select the New Repository Button.
![Screenshot from 2024-11-01 10-58-55](https://github.com/user-attachments/assets/64284bf5-dcd7-49ae-bdcf-c8c7fe1b3467)

2. Give this repository a descriptive name and leave it Private. Select Add a README file and choose MIT License from the dropdown menu. Then create the repository
![Screenshot from 2024-11-01 11-01-08](https://github.com/user-attachments/assets/a78cddfd-68fa-467b-9c31-b90fb2c0bd21)

3. Open `workspace-newrobot2026` in the code editor of your choice and open the `repos.yaml` file in the main level of the workspace.

4. Add your new repo in with the following format (Follow the same Tabbing as the existing repo import lines:
   ```
   <category>/<package_name>:
     type: git
     url: <ssh_clone_code>
     version: <branch>
   ```
   - `\<category>` is the general category your package falls into (i.e. autonomy, hardware_interfacing, user_interfacing)
   - `\<package_name>` is the name you gave your repository
   - `\<ssh_clone_code>` is the link copied from the code button on your repositories page (in the format of `git@github.com:wvu-urc/<package_name>.git`)
   - `\<branch>` is the specific branch of your repo you want included
  
5. In your code editor, open the `.gitignore` file in the main level of the workspace and add `src/<category>/<package_name>` to the list of ignored folders
  
6. Make sure you are in the `~/workspace-newrobot2026` directory before continuing on to the next steps

7. Run the command `vcs import src < repos.yaml` to import all of the additional packages into the repo. Usually this will output text indicating the download of several packages, but two known failures can occur (See [Troubleshooting](#vcs-tool-isnt-working) for more information)

8. Navigate in a terminal to the category folder of new repo you just downloaded. It should be located at `~/workspace-newrobot2026/src/<category>`

9. Run the command `$ mv ./<package_name> ./<package_name>2 .` to rename the package folder temporarily. This command doesn't give any outputs but you can check it worked by running `$ ls`. This output should contain `<package_name>2` instead of `<package_name>`
![image](https://github.com/user-attachments/assets/c47ff537-6846-4a4e-a863-5219303b2f0e)

10. Run the command `$ ros2 pkg create --build-type ament_python <package_name>` to make the ROS2 package

11. Run the command `$ cp -a ./<package_name>2/. ./<package_name>/; rm -rf ./<package_name>2` to merge the files of the two folders together.  This command doesn't give any outputs but you can check it worked by running `$ ls`. This output should now contain `<package_name>` not `<package_name>2`
![image](https://github.com/user-attachments/assets/1bf8b6b1-ad9d-4e75-8652-fb1f4e85c7e9)

12. Run `$ cd ~/workspace-newrobot2026` to get back to the top level of the workspace. Once there, compile the workspace by running `$ colcon build`. See [Troubleshooting](#errors-running-colcon-build) if you encounter errors or crashes. 

## Running Code

1. Move to the top level of the workspace by running the command `cd ~/workspace-newrobot2026`

2. Make sure your code is up to date by running `vcs pull src`

3. Compile the workspace by running `$ colcon build`. See [Troubleshooting](#errors-running-colcon-build) if you encounter errors or crashes.

4. Allow files to be run by your terminal by running `$ source install/setup.bash`

5. Run code in one of the following ways:
   - `ros2 run <package_name> <node_name>`
   - `ros2 launch <packate_name> <launch_file_name>`
   - `ros2 launch launches/<launch_file_name>`
   If you run into errors or crashes, See [Troubleshooting](#Troubleshooting).

6. When you are finished running your script, you can keyboard interrupt to stop it using `ctrl` + `c`

# Troubleshooting

## VirtualBox
- If you get a black screen on startup try reimporting the OVA
- If you aren't able to see anything on a computer with a 4K display, select view in the top menu bar and manually set your resolution to `1920 x 1080` or `1920 x 1200` and set the scale factor to `200%`
- If you are using Windows and have WSL2 installed you may encounter a slow VM or one that doesn't run at all. To solve this problem, search `Turn Windows Features on or off` in the windows search bar and uncheck `Virtual Machine Platform`. This will disable WSL2 until you re-enable it, at which point your VirtualBox problems may start happening again.

## VCS Tool isn't working
- `Input data is not valid format: 'NoneType' object is not subscriptable`
   - This error is cause by the repos.yaml file being empty. Check with one of the Programming coordinators to see if this should be the case
- Most of the Imports are failing
   - WVU has anti-spam protection set up in place and that causes issues when downloading our repositories at once. Try waiting a few minutes and running the command again. If that doesn't work, try using another internet source like a mobile hotspot.

 ## Errors when Running `colcon build`
- Most errors are related to specific packages so see if a particular one is mentioned
   - If a python stack trace is shown the code in that package is messed up
- `The current CMakeCache.txt <directory> is different than the directory <directory> where CMakeCache.txt was created. This may result in binaries being created in the wrong place.`
   - Run `$ rm -rf ./log ./install ./build` to clear the workspace, then try building again
- `The source directory <directory> does not exist`
   - Run `$ rm -rf ./log ./install ./build` to clear the workspace, then try building again
- My computer / VM keeps crashing when building the code
   - `colcon build` uses a lot of computing resources and can sometimes starve out other important processes. If this keeps happening, try running `$ colcon build --executor sequential` instead. This will reduce the number of packages it tries to build at once from 4 to 1
