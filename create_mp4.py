import subprocess
import os
import PIL
from PIL import Image
import boto3
import shutil

def create_mp4(assets, logo_position, camera_id, title, logo_name, headers):
    if os.path.exists("result/" + camera_id + ".mp4"):
        os.remove("result/" + camera_id + ".mp4")

    mywidth = 300

    # Create timelapse
    subprocess.call('ffmpeg -f concat -i "camera.txt" -vf fps=24 -pix_fmt yuv420p timelapse.mp4', shell = True)

    # create timelapse opencv
    '''
    f = open("camera2.txt", "r")
    temp = f.read().splitlines()
    video_name = 'timelapse.avi'
    images = [x for x in temp if x.endswith(".jpg")]
    print(images[0])
    frame = cv2.imread(images[0])
    height, width, layers = frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    video = cv2.VideoWriter(video_name, fourcc, 1, (width,height), False)

    for image in images:
        print(image)
        video.write(cv2.imread(image))

    cv2.destroyAllWindows()
    video.release()
    '''

    # Add logo and sponsor
    position = ""
    if logo_position == "0":
        # Botton-left
        position = "overlay=5:H-h-5"
    elif logo_position == "1":
        # Top-right
        position = "overlay=W-w-5:5"
    elif logo_position == "2":
        # Botton-right
        position = "overlay=W-w-5:H-h-5"
    else:
        # Top-left
        position = " overlay=5:5"
     
    if logo_position >= "0":
        if os.path.exists('assets/images/' + logo_name):
            img = Image.open('assets/images/' + logo_name)
            wpercent = (mywidth/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            img = img.resize((mywidth,hsize), PIL.Image.ANTIALIAS)
            img.save('logo-resize.png')
        print("Logo position: ", position)
        subprocess.call("ffmpeg -i timelapse.mp4 -i logo-resize.png -filter_complex '[0:v][1:v] " + position + "' -pix_fmt yuv420p -c:a copy timelapse2.mp4", shell = True)
        # From second 0 to seconf 20 -> enable='between(t,0,20)'
    else:
        shutil.move("timelapse.mp4", "timelapse2.mp4")

    # Add header
    if headers == "true":
        subprocess.call("ffmpeg -i assets/video/intro.mp4 -acodec libvo_aacenc -vcodec libx264 -s 1920x1080 -r 60 -strict experimental intro.mp4", shell = True)
        subprocess.call("ffmpeg -i assets/video/contact.mp4 -acodec libvo_aacenc -vcodec libx264 -s 1920x1080 -r 60 -strict experimental contact.mp4", shell = True)
        subprocess.call("ffmpeg -i timelapse2.mp4 -acodec libvo_aacenc -vcodec libx264 -s 1920x1080 -r 60 -strict experimental timelapse3.mp4", shell = True)
        subprocess.call("ffmpeg -f concat -i pathList.txt -c copy output.mp4", shell = True)
    else:
        if os.path.exists("timelapse2.mp4"):
            shutil.move("timelapse2.mp4", "output.mp4")

    # Add audio
    if not os.path.exists("result"):
        os.makedirs("result")
    subprocess.call("ffmpeg -i output.mp4 -i assets/audios/music2.mp3 -codec copy -shortest result/" + camera_id + ".mp4", shell=True)

    # upload_zip(camera_id, title, assets)
    if os.path.exists("result/" + camera_id + ".mp4"):
        upload_mp4(camera_id, title, assets)
        #os.remove("result/" + camera_id + ".mp4")

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

def upload_zip(camera_id, title, assets):
    print("Uploading zip...")
    s3_resource = boto3.resource('s3')
    s3_resource.Object("timelapse-server", title + ".zip").upload_file(Filename= title + ".zip")
    print("Zip uploaded")
    if os.path.exists(title + ".zip"):
        os.remove(title + ".zip")

def upload_mp4(camera_id, title, assets):
    print("Uploading mp4...")
    s3_resource = boto3.resource('s3')
    s3_resource.Object("timelapse-server", title + ".mp4").upload_file(Filename="result/" + camera_id + ".mp4")
    print("Mp4 uploaded")

if __name__ == '__main__':
    create_mp4()
