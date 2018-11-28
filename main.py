from color_analizer import ColorAnalyser
from create_mp4 import create_mp4
import os
import shlex, subprocess
import time
import datetime
import shutil
import calendar
import ast
from PIL import Image

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
    if schedule == "null":
        return True
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

def main(title, camera_id, dateFrom, dateTo, schedule, position, threshold, logo_name, analyze, duration, headers, blur, date, motion):
    start_time = time.time()
    Analyzer = ColorAnalyser()
    prevPath = None
    folder = "assets/images/" + camera_id
    if not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.exists("media/" + camera_id):
        os.makedirs("media/" + camera_id)
    command_line = "/home/javict/evercam/machinelearning/timelapse-server/weed mount -filer=localhost:8888 -dirListLimit=3600 -dir=./media/" + camera_id + " -filer.path=/" + camera_id + "/snapshots/recordings/"
    args = shlex.split(command_line)
    print(args)
    subprocess.Popen(args)
    time.sleep(2)
    f= open("camera.txt","w+")
    cont = 0
    valid = 0
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
                print("Day: ", validDay)
                print("Hour: ", validHour)
                if validDay and validHour:
                    if date:
                        Analyzer.clean_date()
                    if analyze == "true":
                        good = Analyzer.main(path, prevPath, folder)
                    else:
                        good = True
                    if good:
                        prevPath = path
                        # move(path, folder)
                        try:
                            img = Image.open(path)
                            img.verify()
                            f.write("file '" + path + "'\n")
                        except (IOError, SyntaxError) as e:
                            print('Bad file:', path)
                            print(e)
                        valid += 1
    f.close()
    print("Contador: ", cont)
    print("Valid: ", valid)
    
    f = open("camera.txt", "r")
    lines = f.readlines()
    num_lines = len(lines)
    f.close
    remove = num_lines - (int(duration) * 24)
    if num_lines > 0:
        leave = num_lines - remove
        aux = leave / num_lines
        cont = 0
        f = open("camera.txt", "w")
        write = 1
        for x in lines:
            cont += aux
            if cont > write:
                write += 1
                f.write(x)
        f.close()
            
        create_mp4(folder, position, camera_id, title, logo_name, headers)
    command_line = "fusermount -u ./media/" + camera_id
    args = shlex.split(command_line)
    subprocess.Popen(args)
    print("--- %s seconds ---" % (time.time() - start_time))
    
if __name__ == '__main__':
    # camera_id = "casti-etwpd"
    # position = 3
    # threshold = 100
    # create = True
    # analyze = True
    # blur = False
    # date = False
    # motion = True
    main(title, camera_id, dateFrom, dateTo, schedule, position, threshold, logo_name, create_mp4, analyze, duration, headers, blur, date, motion)
