import os
from flask import Flask, request, Response
from werkzeug import secure_filename
from main import main
import threading
import json
import subprocess
import urllib.request

app = Flask(__name__)
@app.route('/api', methods=['POST'])

def result():
    # print(request.get_data())
    print(request.form)
    f = request.files['logo']
    logo_name = secure_filename(f.filename)
    f.save(os.path.join("./assets/images", logo_name))
    blur = "false"
    date = "false"
    motion = "false"
    threshold = "100"

    cmd = "cat /proc/mounts | grep 'SeaweedFS'"
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    output = output.decode('utf-8')
    print(output)
    if not output:
        t = threading.Thread(target=main, args = (request.form['exid'], request.form['camera_id'],request.form['from'], request.form['to'], request.form['schedule'], request.form['position'], threshold, logo_name, request.form['analyze'], request.form['duration'], request.form['headers'], blur, date, motion))
        t.daemon = True
        t.start()

        return Response(json.dumps({
            'success': True,
            'status': 200
        }), mimetype=u'application/json')
    else:
        with open('pending.txt', 'a') as data:
            data.write(request.form['exid'] + ":" + request.form['camera_id'] + ":" + request.form['from'] + ":" + request.form['to'] + ":" + request.form['schedule'] + ":" + request.form['position'] + ":" + threshold + ":" + logo_name + ":" + request.form['analyze'] + ":" + request.form['duration'] + ":" + request.form['headers'] + ":" + blur + ":" + date + ":" + motion + "\n")
            data.close()
        return Response(json.dumps({
            'success': False,
            'status': 204
        }), mimetype=u'application/json')

@app.route('/api2', methods=['POST'])

def result2():
    # print(request.get_data())
    print(request.form)

    logo_name = "none"
    blur = "false"
    date = "false"
    motion = "false"
    threshold = "100"

    cmd = "cat /proc/mounts | grep 'SeaweedFS'"
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    output = output.decode('utf-8')
    print(output)
    if not output:
        t = threading.Thread(target=main, args = (request.form['exid'], request.form['camera_id'],request.form['from'], request.form['to'], request.form['schedule'], request.form['position'], threshold, logo_name, request.form['analyze'], request.form['duration'], request.form['headers'], blur, date, motion))
        t.daemon = True
        t.start()

        return Response(json.dumps({
            'success': True,
            'status': 200
        }), mimetype=u'application/json')
    else:
        with open('pending.txt', 'a') as data:
            data.write(request.form['exid'] + ":" + request.form['camera_id'] + ":" + request.form['from'] + ":" + request.form['to'] + ":" + request.form['schedule'] + ":" + request.form['position'] + ":" + threshold + ":" + logo_name + ":" + request.form['analyze'] + ":" + request.form['duration'] + ":" + request.form['headers'] + ":" + blur + ":" + date + ":" + motion + "\n")
            data.close()
        return Response(json.dumps({
            'success': False,
            'status': 204
        }), mimetype=u'application/json')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
