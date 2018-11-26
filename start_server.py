import os
from flask import Flask, request, Response
from werkzeug import secure_filename
from main import main
import threading
import json
import subprocess
import json

app = Flask(__name__)
@app.route('/api', methods=['POST'])

def result():
    # print(request.get_data())
    print(request.form)
    f = request.files['logo']
    logo_name = secure_filename(f.filename)
    f.save(os.path.join("./assets/images", logo_name))
    blur = False
    date = False
    motion = False
    threshold = 100
    get_images = True
    
    cmd = "cat /proc/mounts | grep 'SeaweedFS'"
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    output = output.decode('utf-8')
    print(output)
    if not output:    
        t = threading.Thread(target=main, args = (request.form['exid'], request.form['camera_id'],request.form['from'], request.form['to'], request.form['schedule'], request.form['interval'], request.form['position'], threshold, logo_name, request.form['create_mp4'], request.form['analyze'], blur, date, motion, get_images))
        t.daemon = True
        t.start()
    
        return Response(json.dumps({
            'success': True,
            'status': 200
        }), mimetype=u'application/json')
    else:
        with open('pending.json', 'w') as outfile:
            json.dump(request.form, outfile)
        with open('pending.json') as data_file:    
            data = json.load(data_file)
            print(data)
        return Response(json.dumps({
            'success': False,
            'status': 204
        }), mimetype=u'application/json')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
