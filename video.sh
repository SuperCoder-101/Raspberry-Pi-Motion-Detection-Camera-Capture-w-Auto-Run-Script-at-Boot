#!/bin/bash

flash_drive_directory="/media/your-user/your-usb"

# Check if there is enough space on the flash drive (5GB minimum)
min_space=5000000 # Minimum space required in KB

while true; do
    available_space=$(df "$flash_drive_directory" | awk 'NR==2 {print $4}') # Available space in KB

    if (( available_space < min_space )); then
        echo "Not enough space on the flash drive. Exiting."
        exit 1
    fi

    # Your libcamera-vid command to start recording for 5 minutes 

    libcamera-vid -t 10000 -b 9000000 --width 1280 --height 720 --codec libav -o /media/Orchird/STORENGO/"$(date +%Y%m%d_%H%M.mp4)" 

    # Sleep for 5 minutes after recording completes
    sleep 10

done
