import subprocess
import os
import PIL
from PIL import Image
import boto3
import datetime

def create_mp4(assets, logo_position, camera_id):
    if os.path.exists("result/" + camera_id + ".mp4"):
        os.remove("result/" + camera_id + ".mp4")

    mywidth = 300

    if os.path.exists('assets/logo.png'):
        img = Image.open('assets/logo.png')
        wpercent = (mywidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((mywidth,hsize), PIL.Image.ANTIALIAS)
        img.save('logo-resize.png')

    # Create timelapse
    subprocess.call('ffmpeg -r 24 -pattern_type glob -i "' + assets + '/*.jpg" -s hd1080 -vcodec libx264 -crf 18 -preset slow timelapse.mp4', shell = True)

    # Add logo and sponsor
    position = ""
    if logo_position == 0:
        # Botton-left
        position = "overlay=5:H-h-5"
    elif logo_position == 1:
        # Top-right
        position = "overlay=W-w-5:5"
    elif logo_position == 2:
        # Botton-right
        position = "overlay=W-w-5:H-h-5"
    else:
        # Top-left
        position = " overlay=5:5"
    subprocess.call("ffmpeg -i timelapse.mp4 -i logo-resize.png -filter_complex '[0:v][1:v] " + position + "' -pix_fmt yuv420p -c:a copy timelapse2.mp4", shell = True)
    # From second 0 to seconf 20 -> enable='between(t,0,20)'

    # Add header
    subprocess.call("ffmpeg -i assets/video/intro.mp4 -acodec libvo_aacenc -vcodec libx264 -s 1920x1080 -r 60 -strict experimental intro.mp4", shell = True)
    subprocess.call("ffmpeg -i assets/video/contact.mp4 -acodec libvo_aacenc -vcodec libx264 -s 1920x1080 -r 60 -strict experimental contact.mp4", shell = True)
    subprocess.call("ffmpeg -i timelapse2.mp4 -acodec libvo_aacenc -vcodec libx264 -s 1920x1080 -r 60 -strict experimental timelapse3.mp4", shell = True)
    subprocess.call("ffmpeg -f concat -i pathList.txt -c copy output.mp4", shell = True)

    # Add audio
    if not os.path.exists("result"):
        os.makedirs("result")
    subprocess.call("ffmpeg -i output.mp4 -i assets/audios/music2.mp3 -codec copy -shortest result/" + camera_id + ".mp4", shell=True)

    if os.path.exists("result/" + camera_id + ".mp4"):
        upload(camera_id)

    if os.path.exists("logo-resize.png"):
        os.remove("logo-resize.png")
    if os.path.exists("timelapse.mp4"):
        os.remove("timelapse.mp4")
    if os.path.exists("timelapse2.mp4"):
        os.remove("timelapse2.mp4")
    if os.path.exists("output.mp4"):
        os.remove("output.mp4")
    if os.path.exists("timelapse3.mp4"):
        os.remove("timelapse3.mp4")
    if os.path.exists("intro.mp4"):
        os.remove("intro.mp4")
    if os.path.exists("contact.mp4"):
        os.remove("contact.mp4")

def upload(camera_id):
    s3_resource = boto3.resource('s3')
    dt = datetime.datetime.now()
    seconds = int(dt.timestamp())
    s3_resource.Object("timelapse-server", str(seconds) + "-" + camera_id + ".mp4").upload_file(Filename="result/" + camera_id + ".mp4")

if __name__ == '__main__':
    create_mp4()
