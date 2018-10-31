from color_analizer import ColorAnalyser
from create_mp4 import create_mp4
import os
import shlex, subprocess
import time

def main(camera_id, position, threshold, create, analyze, blur, date, motion, get_images):
    aux4 = 1
    prevPath = ""
    folder = "assets/images/" + camera_id
    if get_images:
        if not os.path.exists(folder):
            os.makedirs(folder)
        print("INSIDE")
        if not os.path.exists("media/" + camera_id):
            os.makedirs("media/" + camera_id)
        command_line = "./weed mount -filer=localhost:8888 -dirListLimit=3600 -dir=./media/" + camera_id + " -filer.path=/" + camera_id + "/snapshots/recordings/"
        args = shlex.split(command_line)
        print(args)
        subprocess.Popen(args)
        time.sleep(2)
        cpt = sum([len(files) for r, d, files in os.walk("media/" + camera_id)])
        print("Total images: " + str(cpt))
        for subdir, dirs, files in sorted(os.walk("media/" + camera_id)):
            for file in sorted(files):
                path = os.path.join(subdir, file)
                s = path.split("/")[-5:]
                if s[0].isdigit():
                    Analyzer = ColorAnalyser(path, folder)
                    if date:
                        Analyzer.clean_date()
                    if analyze:
                        good = Analyzer.main(aux4, prevPath, folder)
                    if good:
                        prevPath = path
        command_line = "fusermount -u ./media/" + camera_id
        args = shlex.split(command_line)
        subprocess.Popen(args)

    if create:
       create_mp4(folder, position, camera_id)

if __name__ == '__main__':
    # camera_id = "casti-etwpd"
    # position = 3
    # threshold = 100
    # create = True
    # analyze = True
    # blur = False
    # date = False
    # motion = True
    # get_images = True
    main(camera_id, position, threshold, create, analyze, blur, date, motion, get_images)
