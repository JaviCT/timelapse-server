import os
import boto3
import shutil
import cv2
import moviepy.editor as mpe

def create_mp4(assets, logo_position, camera_id, title, logo_name, headers):
    if os.path.exists("result/" + camera_id + ".mp4"):
        os.remove("result/" + camera_id + ".mp4")

    f = open("camera.txt", "r")
    temp = f.read().splitlines()
    video_name = 'timelapse.mp4'
    images = [x for x in temp if x.endswith(".jpg")]
    print(images[0])
    frame = cv2.imread(images[0])
    height, width, layers = frame.shape
    video = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'H264'), 24.0, (width,height))
    for image in images:
        video.write(cv2.imread(image))

    cv2.destroyAllWindows()
    video.release()

    # Add header
    if headers == "true":
        video1 = mpe.VideoFileClip('timelapse.mp4')
        video2 = mpe.VideoFileClip('assets/video/intro.mp4')
        video2 = video2.resize(height=height, width=width)
        video3 = mpe.VideoFileClip('assets/video/contact.mp4')
        video3 = video3.resize(height=height, width= width)
        final = mpe.concatenate_videoclips([video2, video1, video3], method="compose")
    else:
        final = mpe.VideoFileClip('timelapse.mp4')

     # Add logo and sponsor
    position1 = ""
    position2 = ""
    if logo_position == "0":
        # Botton-left
        position1 = "bottom"
        position2 = "left"
    elif logo_position == "1":
        # Top-right
        position1 = "top"
        position2 = "right"
    elif logo_position == "2":
        # Botton-right
        position1 = "bottom"
        position2 = "right"
    else:
        # Top-left
        position1 = "top"
        position2 = "left"

    if logo_position >= "0":
        if os.path.exists('assets/images/' + logo_name):
            logo = (mpe.ImageClip('assets/images/' + logo_name)
              .set_duration(final.duration)
              .resize(height=300)
              .margin(right=8, top=8, bottom=8, left=8, opacity=0)
              .set_pos((position2,position1)))
            final = mpe.CompositeVideoClip([final, logo])

    # Add audio
    if not os.path.exists("result"):
        os.makedirs("result")

    if logo_position >= "0" or headers == "true":
        audio_background = mpe.AudioFileClip('assets/audios/music3.mp3')
        final = final.set_audio(audio_background.set_duration(final.duration))
        final.write_videofile("output.mp4")
        shutil.move("output.mp4", "result/" + camera_id + ".mp4")
    else:
        shutil.move("timelapse.mp4", "result/" + camera_id + ".mp4")

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
    if os.path.exists('assets/images/' + logo_name):
        os.remove('assets/images/' + logo_name)

def upload_mp4(camera_id, title, assets):
    print("Uploading mp4...")
    s3_resource = boto3.resource('s3')
    s3_resource.Object("timelapse-server", title + ".mp4").upload_file(Filename="result/" + camera_id + ".mp4")
    print("Mp4 uploaded")

if __name__ == '__main__':
    create_mp4()
