import os
from flask import Flask, request
from werkzeug import secure_filename
from main import main
import threading

app = Flask(__name__)
@app.route('/api', methods=['POST'])

def result():
    print(request.get_data())
    f = request.files['logo']
    f.save(os.path.join("./assets/images", secure_filename(f.filename)))
    create = True
    analyze = True
    blur = True
    date = False
    motion = False
    threshold = 100
    get_images = True
    t = threading.Thread(target=main, args = (request.form['camera_id'], request.form['position'],threshold, create, analyze, blur, date, motion, get_images))
    t.daemon = True
    t.start()
    return 'Done'

if __name__ == "__main__":
    app.run(host='0.0.0.0')
