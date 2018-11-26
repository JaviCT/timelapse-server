from color_analizer import ColorAnalyser
from create_mp4 import create_mp4, upload_zip
import os
import shlex, subprocess
import time
import datetime
import shutil
import calendar
import ast
import zipfile

def get_title():
    dt = datetime.datetime.now()
    seconds = int(dt.timestamp())
    return str(seconds)

def move(path, folder):
    if os.path.exists(path):
        s = path.split("/")[-5:]
        name = get_time(s)
        dest = folder + "/" + str(name) + ".jpg"
        shutil.copy(path, dest)

def get_time(s):
    year = int(s[0])
    month = int(s[1])
    day = int(s[2])
    hour = int(s[3])
    s2 = s[4].split("_")
    minute = int(s2[0])
    second = int(s2[1])
    dt = datetime.datetime(year, month, day, hour, minute, second)
    seconds = dt.timestamp()
    return int(seconds)

def valid_day(dateFrom, dateTo, s):
    dateFrom = dateFrom.split("/")
    dateTo = dateTo.split("/")
    
    year = int(s[0])
    month = int(s[1])
    day = int(s[2])
    hour = int(s[3])
    s2 = s[4].split("_")
    minute = int(s2[0])
    second = int(s2[1])
    
    fromyear = int(dateFrom[0])
    frommonth = int(dateFrom[1])
    fromday = int(dateFrom[2])
    
    toyear = int(dateTo[0])
    tomonth = int(dateTo[1])
    today = int(dateTo[2])
    
    dtFrom = datetime.datetime(fromyear, frommonth, fromday, 0, 0, 0)
    dtTo = datetime.datetime(toyear, tomonth, today, 0, 0, 0)
    dt = datetime.datetime(year, month, day, hour, minute, second)
    
    if dt > dtFrom and dt < dtTo:
        return True
    else:
        return False

def valid_hour(schedule, s):
    year = int(s[0])
    month = int(s[1])
    day = int(s[2])
    hour = int(s[3])
    s2 = s[4].split("_")
    minute = int(s2[0])
    second = int(s2[1])
    dt = (datetime.datetime(year, month, day, hour, minute, second).weekday() + 1)
    if dt == 7:
        dt = 0
    if schedule == "full_week":
        return True
    elif schedule == "working_hours":
        if dt != 5 or dt != 6:
            if hour > 7 and hour < 18:
                return True
        return False
    else:
        schedule = ast.literal_eval(schedule)
        for a in schedule[calendar.day_name[dt]]:
            hFrom, hTo = a.split("-")
            if hour < int(hFrom) or hour > int(hTo):
                return False
            else:
                return True
        return False

def main(title, camera_id, dateFrom, dateTo, schedule, interval, position, threshold, logo_name, create, analyze, blur, date, motion, get_images):
    Analyzer = ColorAnalyser()
    prevPath = None
    folder = "assets/images/" + camera_id
    if get_images:
        if not os.path.exists(folder):
            os.makedirs(folder)
        if not os.path.exists("media/" + camera_id):
            os.makedirs("media/" + camera_id)
        command_line = "./weed mount -filer=localhost:8888 -dirListLimit=3600 -dir=./media/" + camera_id + " -filer.path=/" + camera_id + "/snapshots/recordings/"
        args = shlex.split(command_line)
        print(args)
        subprocess.Popen(args)
        time.sleep(2)
        f= open("camera.txt","w+")
        cont = 0
        valid = 0
        zipf = zipfile.ZipFile(title + ".zip", 'w', zipfile.ZIP_DEFLATED)
        for subdir, dirs, files in sorted(os.walk("media/" + camera_id)):
            for file in sorted(files):
                cont += 1
                path = os.path.join(subdir, file)
                if prevPath is None:
                    prevPath = path
                print(path)
                s = path.split("/")[-5:]
                if s[0].isdigit():
                    validDay = valid_day(dateFrom, dateTo, s)
                    validHour = valid_hour(schedule, s)
                    if validDay and validHour:
                        before = get_time(s)
                        s3 = prevPath.split("/")[-5:]
                        after = get_time(s3)
                        diff = before - after
                        if diff > int(interval):
                            if date:
                                Analyzer.clean_date()
                            if analyze == "true":
                                good = Analyzer.main(path, prevPath, folder)
                            else:
                                good = True
                            if good:
                                prevPath = path
                                zipf.write(path)
                                # move(path, folder)
                                try:
                                    f.write("file '" + path + "'\n")
                                except:
                                    print("Something went wrong when writing to the file")
                                valid += 1
    f.close()
    zipf.close()
    print("Contador: ", cont)
    print("Valid: ", valid)
    print("Create: ", create)
    if create == "true":
        create_mp4(folder, position, camera_id, title, logo_name)
    else:
        upload_zip(camera_id, title, folder)
        """
        try:
            f = open("camera.txt", "r")
            temp = f.read().splitlines()
            for x in temp:
                folder = "assets/images/test"
                move(x, folder)
        except:
            print("Something went wrong when writing to the file")
        finally:
            f.close()
        """
    command_line = "fusermount -u ./media/" + camera_id
    args = shlex.split(command_line)
    subprocess.Popen(args)
    
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
    main(title, camera_id, dateFrom, dateTo, schedule, interval, position, threshold, logo_name, create_mp4, analyze, blur, date, motion, get_images)
