#!/usr/bin/python3

import time
import os

import numpy as np

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

directory_path = "/media/your_user/flashdrive/"

# Time to sleep before checking for motion again (10 seconds)
sleep_duration = 10

# Check if the directory path exists, create it if it doesn't
if not os.path.exists(directory_path):
    os.makedirs(directory_path)

lsize = (320, 240)
picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": (1280, 720), "format": "RGB888"},
                                                 lores={"size": lsize, "format": "YUV420"})
picam2.configure(video_config)
encoder = H264Encoder(1000000)
picam2.start()

w, h = lsize
prev = None
encoding = False   
t0 = 0


while True:
    cur = picam2.capture_buffer("lores")
    cur = cur[:w * h].reshape(h, w)
    if prev is not None:
        # Measure pixels differences between current and
        # previous frame
        mse = np.square(np.subtract(cur, prev)).mean()
        if mse > 7:
            if not encoding:
                # Specify the output file path with a unqiue timestamp
                output_file_path = os.path.join(directory_path, f"{int(time.time())}.mp4")

                encoder.output = FfmpegOutput(output_file_path, audio=False)
                picam2.start_encoder(encoder)
                encoding = True
                print("New Motion", mse)
                t0 = time.time() # start time of recording
        else:
            if encoding:
                t1 = time.time() # current time
                duration = t1 - t0 # current time - start time
                if duration > 11:
                    picam2.stop_encoder()
                    encoding = False
                    print("Stop recording now that 10 seconds has passed") # Print statement to see that this section is actually being executed
                    print("Sleep for 10 seconds...") # Sleep for 10 seconds before beginning new motion capture
    prev = cur
    time.sleep(1)
