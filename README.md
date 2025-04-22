# Raspberry-Pi-Motion-Detection-Camera-Capture-w-Auto-Run-Script-at-Boot

**Project Overview**

This project provides a Raspberry Pi-based system for automatic video recording and motion detection. It includes two recording options:

- A **Bash script** for scheduled video recording (5 minutes on, 5 minutes off).

- A **Python script** for motion-triggered video recording using the Picamera2 library.

Both scripts are designed to **auto-run at boot** using **systemd** services. Captured videos are saved to an external USB flash drive for later access.

--------------------------------------------------------------------------------------------------

**System Requirements**

- Raspberry Pi 4 (or similar model)

- Raspberry Pi OS (Bullseye, 64-bit recommended)

- External USB flash drive

- Raspberry Pi Camera Module (configured for libcamera and Picamera2)

- Internet connection (for initial setup and package installation)

--------------------------------------------------------------------------------------------------

**Installation and Setup**

**Step 1: Install Raspberry Pi OS and Update Packages**

`sudo apt-get update`
`sudo apt-get upgrade`

**Note:** If updates fail, reboot your device and retry the update command. Also, only use the upgrade command when necessary.

--------------------------------------------------------------------------------------------------

**Step 2: Disable Legacy Camera Support**

**Note:** Only do this if you plan on using option 2.

Navigate to **Interface options > Camera** and disable the **Legacy camera system**.

Picamera2 requires the newer **libcamera** interface.

--------------------------------------------------------------------------------------------------

**Step 3: Organize Your Files and Folders**

Create a directory for your scripts:

`sudo mkdir /home/your-user/your_folder`

Example:

`sudo mkdir /home/pi/python_scripts`

Use underscores _ instead of spaces to avoid path issues.

Assign ownership:

`sudo chown -R your-user:your-user /home/your-user/your_folder`

Make sure to give permission here as well:

` sudo chown root:gpio /dev/gpiomem`
` sudo chmod 660 /dev/gpiomem`

**Optional**

To make rules permanent:

` sudo nano /etc/udev/rules.d/99-gpiomem.rules`

Then paste in the file:

` KERNEL=="gpiomem", GROUP="gpio", MODE="0660"`

Then save and exit, and then apply:

` sudo udevadm control --reload-rules`
` sudo udevadm trigger`

**Note:** Normally, problems I have had in the past always come from file permissions; ensure you give your files and file paths the proper permissions. 

--------------------------------------------------------------------------------------------------

**Step 4: USB Flash Drive Setup**

Your USB drive will mount under:

`/media/your-user/your-usb/`

Example mount points:

`/media/Fire/STORENGO`
`/media/pi/MYDRIVE`
`/media/username/USBSTICK`

Check mounted drives:

`df -h`

If camera access fails, do:

`sudo chmod 666 /dev/video0`
`sudo chmod 777 /media/your-user/`

Adjust script paths based on your own username and flash drive name.

--------------------------------------------------------------------------------------------------

**Understanding File Permissions**

Permissions are usually shown like this:

`-rw-r--r-- 1 user group file.py`

That breaks down to:

- r = read
- w = write
- x = execute
- First set: owner
- Second set: group
- Third set: others

**Common _chmod_ Values**

Value -------- Meaning

----------------------------------------------------------------------------------------------
777 ---------- Read, write, and execute for everyone (owner, group, others)
----------------------------------------------------------------------------------------------
755 ---------- Owner can write; others can read and execute (common for scripts)
----------------------------------------------------------------------------------------------
666 ---------- Read and write for everyone (no execute) -- often used for device files
----------------------------------------------------------------------------------------------
644 ---------- Owner can read/write; others can only read (common for config files)
----------------------------------------------------------------------------------------------
660 ---------- Read/write for owner and group, no access for others (used for controlled access to hardware, like /dev/gpiomem)
----------------------------------------------------------------------------------------------

--------------------------------------------------------------------------------------------------

**Option 1: Bash Script for Timed Recording**

**Create Bash Script**

 `sudo nano /home/your-user/Video.sh`

Paste the example script below into the file you just created:

	#!/bin/bash
	
	flash_drive_directory="/media/<your-user>/<usb-name>"
	
	# Check if there is enough space on the flash drive (5GB minimum)
	min_space=5000000 # Minimum space required in KB
	
	# Error statement to prevent video file overflow 
	# Is the available space less than the minimum space? (which is defined above)
	while true; do
	    available_space=$(df "$flash_drive_directory" | awk 'NR==2 {print $4}') # Available space in KB
	
	    if (( available_space < min_space )); then
	        echo "Not enough space on the flash drive. Exiting."
	        exit 1
	    fi
	
	    # Your libcamera-vid command to start recording for 5 minutes 
	    # -t 300000 is the section in libcamera-vid you want to modify
	    # The duration is in milliseconds, so 300000 is 5 minutes in milliseconds, ex: 10,000ms is 10 seconds
	
	    libcamera-vid -t 300000 -b 9000000 --width 1280 --height 720 --codec libav -o /media/<your-user>/<usb-name>/"$(date +%Y%m%d_%H%M.mp4)" 
	
	    # Sleep for 5 minutes after recording completes
	    # Sleep duration is in seconds, 300 is 5 minutes
	    # 10 is 10 seconds
	    sleep 300
	
    done

**Save and Exit**

Then save and exit using **CTRL + X**, then press **Y**, then **Enter**


**Setup systemd Service**

 `sudo nano /etc/systemd/system/video.service`

Paste this into the **.service** file:

----------------------------------------------------------------------------------------
[Unit]

Description=Video Service

After=network.target

[Service]

ExecStart=/home/your-user/Video.sh

WorkingDirectory=/home/your-user

User=your-user

KillMode=mixed

Restart=always

RestartSec=3

[Install]

WantedBy=multi-user.target

----------------------------------------------------------------------------------------
Enable the service:

 `sudo chmod 644 /etc/systemd/system/video.service`
 `sudo systemctl daemon-reload`
 `sudo systemctl enable video.service`

Starting a service:

 `sudo systemctl start video.service`

- To stop it

` sudo systemctl stop video.service`

- To restart it

` sudo systemctl reload video.service`

If you want to check on the service, you can use the command:

 `sudo systemctl status video.service`

If you want to disable the service:

 `sudo systemctl disable video.service`

Just make sure to re-run **daemon-reload** whenever you edit the **.service** file. 

--------------------------------------------------------------------------------------------------

**Recap/Summary**

- Now that you have gone over everything here, you should be able to modify your video recording bash script. 
- Remember to disable the Python script you are using first if you happen to set both of these up on your Raspberry Pi, so use the **sudo systemctl disable your-service-name.service.**
- Then you can start messing with the bash script and the newly created systemd service file that goes with it. 
- But you should want to stop your service before disabling it, as this is standard, just as you want to enable a service and then start it. 
- The only two lines you need to modify are the video duration and sleep duration.  
- On line 18 ‘-t **300000**’ and line 21 ‘sleep **300**’, the bolded parts here are what you want to modify.

--------------------------------------------------------------------------------------------------

**Option 2: Python Script for Motion Detection**

**Prepare Your Environment**
- Install dependencies (ensure Picamera2 is installed)
- Launch Thonny, load your script, and save it as motion.py
- Set permissions:

**Configure Camera Overlay**

 `sudo nano /boot/config.txt`

Add at the bottom:

 `dtoverlay=imx219`

 Now this is dependent on which camera you are using and if they need to have **dtoverlay=something** enabled. Some cameras do not require this, so please make sure to look up your camera type and ensure if it requires dtoverlay. Typically, cameras for **IMX** will need it. However, if you have an **ov5647**, these usually do not need it.

**Create systemd Service**

 `sudo nano /etc/systemd/system/motion.service`

Paste this into the file:

------------------------------------------------------------------------
[Unit]

Description=Motion Detection

After=multi-user.target

Wants=motion.service

[Service]

Type=simple

ExecStart=/usr/bin/python3 /home/your-user/python_scripts/motion.py

User=your-user

KillMode=mixed

Restart=always

RestartSec=3

[Install]

WantedBy=multi-user.target

-----------------------------------------------------------------------
Then run these commands:

 `sudo chmod 644 /etc/systemd/system/motion.service`
 `sudo systemctl daemon-reload`
 `sudo systemctl enable motion.service`
 `sudo systemctl start motion.service`

To disable or check status:

 `sudo systemctl status motion.service`
 `sudo systemctl disable motion.service`

Just make sure to re-run **daemon-reload** whenever you edit the **.service** file. 

On the Raspberry Pi desktop environment, locate Thonny:

- This is where you are going to open the Python script.
- You should make sure you have the **motion.py** script on a flash drive.
- Click on **Load**, then go to the flash drive you connected to your Raspberry Pi and select **motion.py**

Look at the sleep duration line towards the beginning of the script:

- The sleep duration portion of the code is the section you want to modify, depending on how long you want the Raspberry Pi to sleep before it begins its motion detection script again.

Jump to line 40 in **motion.py**:

- Here we are using a mean standard error theorem to calculate the difference between the current and previous frames.
- **If mse > 7:** can be modified like so
           - **Ex: if mse > 6** or **if mse > 8**
           - For smaller motions (more motion), lower it (more likely to capture false positives).
           - For higher motions (less motion), raise it (less likely to capture false positives).

Click Save as and save to **your_folder**

Access your terminal/console:

- Now, there are a few things we will need to do.
- First type **sudo chmod 777 /home/your-user**
- Next, type **cd your_folder** and type **sudo chmod 777 motion.py**. This will give that file the permissions it needs to run on your system.
- Now type **cd** so that you will end up in the **your-user** user directory.

--------------------------------------------------------------------------------------------------

**Side Note -- USB Folder Duplication Bug**

If you **turn off the Raspberry Pi** by unplugging it abruptly, **unplug the USB drive without unmounting it**, or if the **system crashes**, the PI might leave behind a folder in **/media/** with the same name as your flash drive. Normally, Raspberry Pi will mount and unmount USB drives cleanly, but unclean shutdowns mess that up.

**What happens:** 

- On reboot, the system creates a new folder with a 1 suffix, like:

 `/media/your-user/STORENGO1`

- Your script keeps looking for the original path (/media/your-user/STORENGO), so you'll get errors.
- systemd might log:
  `Broken pipe [Errno 32]` or  `Permission denied`

**How to fix:**

1.  Run the script manually (e.g., in Thonny) and check for permission or file-not-found errors.
2. Check /media/your-user/ -- if you see a duplicate folder, one may be a leftover.
3. Unmount your USB, then clean up the ghost folder.

 `sudo rmdir /media/your-user/your-usb`

Once removed, reconnect your flash drive -- it should now mount with the correct name and path.

When I was trying to figure out this problem, it took me a bit to figure out, however, I did what anybody should do in this situation and looked through my folders and the file paths. At first, I thought this was a permission issue, but it was just the system creating a second mount point due to an unclean shutdown. Always try to unmount properly or power off safely!

--------------------------------------------------------------------------------------------------

**Sources**

The picamera2 GitHub was a very useful page for this project -- credit where credit is due! Special thanks to David Plowman and the Raspberry Pi team for their excellent documentation and examples. I highly recommend checking out the examples section, especially the motion capture reference:

- https://github.com/raspberrypi/picamera2/blob/main/examples/capture_motion.py

- https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf

- https://www.thedigitalpictureframe.com/ultimate-guide-systemd-autostart-scripts-raspberry-pi/

--------------------------------------------------------------------------------------------------

I really hope this tutorial was helpful!

This project was originally created as part of a work assignment, and I do not plan on adding further updates to this repository. You're absolutely welcome to use the code and information here for your own projects or learning — just please note that this repo is provided as-is, and I'm not maintaining it or accepting pull requests.

Thanks for checking it out — and enjoy building with Raspberry Pi!
