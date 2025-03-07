import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime
from flask import Flask, render_template, Response, request, redirect, url_for, jsonify
from flask import make_response
import csv
from flask import send_from_directory
import pyttsx3
engine = pyttsx3.init()
last_spoken = {}


app = Flask(__name__)
ENROLL_DIR = "enrolled_students"
camera = cv2.VideoCapture(0)  
current_frame = None

# Load enrolled students
def load_enrolled_students():
    known_encodings = []
    known_names = []
    for filename in os.listdir(ENROLL_DIR):
        if filename.endswith((".jpg", ".png")):
            image_path = os.path.join(ENROLL_DIR, filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(os.path.splitext(filename)[0])
    return known_encodings, known_names

known_encodings, known_names = load_enrolled_students()

# Check if student is already marked present today
def is_already_present_today(name):
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists("attendance_log.txt"):
        with open("attendance_log.txt", "r") as f:
            for line in f:
                parts = line.strip().split(" - ")
                if len(parts) == 3 and parts[0] == name and parts[2].startswith(today):
                    return True
    return False

# Log attendance
def log_attendance(name):
    if not is_already_present_today(name):
        with open("attendance_log.txt", "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{name} - Present - {timestamp}\n")
        return True
    return False

# Generate video feed with recognition
def gen_frames():
    global current_frame, known_encodings, known_names
    while True:
        success, frame = camera.read()
        if not success:
            break

        current_frame = frame.copy()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        status = "No face detected"
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_names[first_match_index]
                if log_attendance(name) and name not in last_spoken:
                  
                    engine.runAndWait()
                    last_spoken[name] = datetime.now()
                    engine.say(f"Welcome, {name}!")
                else:
                    status = f"{name} - Present"
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)
                status = "Unknown Detected"

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/enroll', methods=['GET', 'POST'])
def enroll():
    global current_frame, known_encodings, known_names
    if request.method == 'POST':
        name = request.form['name'].strip()

        if name and os.path.exists(os.path.join(ENROLL_DIR , f"{name}.jpg")):
            return render_template("enroll.html" , error = f"Student '{name}' is already enrolled")
        
        if name and current_frame is not None:
            rgb_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)
            if not face_recognition.face_encodings(rgb_frame):
                return "Error: No face detected in the current frame. Please try again.", 400
            filename = os.path.join(ENROLL_DIR, f"{name}.jpg")
            cv2.imwrite(filename, current_frame)

            known_encodings, known_names = load_enrolled_students()
            return redirect(url_for('index'))
        return "Error: Invalid name or no frame captured", 400
    return render_template('enroll.html')

@app.route('/attendance')
def attendance():
    logs = []
    if os.path.exists("attendance_log.txt"):
        with open("attendance_log.txt", "r") as f:
            logs = [line.strip().split(" - ") for line in f.readlines()]
    return render_template('attendance.html', logs=logs)

@app.route("/reset" , methods = ["GET" , "POST"])
def reset():
    if request.method == "POST":
        open('attendance_log.txt' , "w").close()
        return redirect(url_for('attendance'))
    return render_template('reset.html')
    
@app.route("/export")
def export():
    logs = []
    if os.path.exists("attendance_log.txt"):
        with open("attendance_log.txt", "r") as f:
            logs = [line.strip().split(" - ") for line in f.readlines()]
    response = make_response("\n".join([",".join(log) for log in logs]))
    response.headers["Content-Disposition"] = "attachment; filename=attendance.csv"
    response.headers["Content-Type"] = "text/csv"
    return response


@app.route("/students")
def student():
    students = [os.path.splitext(f)[0] for f in os.listdir(ENROLL_DIR) if f.endswith(('.jpg' , '.png'))]
    return render_template("students.html" , students = students)


@app.route('/enrolled_students/<filename>')
def serve_student_photo(filename):
    return send_from_directory('enrolled_students', filename)


def count_streak(dates):
    from datetime import datetime , timedelta
    dates = sorted(set(dates))
    if not dates:
        return 0
    streak = 1
    for i in range(1 , len(dates)):
        if (datetime.strptime(dates[i], "%Y-%m-%d") - 
            datetime.strptime(dates[i-1], "%Y-%m-%d")).days == 1:
            streak += 1
        else:
            streak = 1
    return streak


@app.route("/dashboard")
def dashboard():
    logs = {}
    if os.path.exists('attendance_log.txt'):
        with open("attendance_log.txt" , "r") as f:
            for line in f:
                name , _ , timeStamp = line.strip().split(" - ")
                date = timeStamp.split(" ")[0]
                if name not in logs:
                    logs[name] = []
                logs[name].append(date)
            
    streaks = {name: count_streak(dates) for name , dates in logs.items()}
    students = [os.path.splitext(f)[0] for f in os.listdir(ENROLL_DIR) if f.endswith(('.jpg' , '.png'))]
    return render_template('dashboard.html' , streaks = streaks , students = students)


if __name__ == "__main__":
    if not os.path.exists(ENROLL_DIR):
        os.makedirs(ENROLL_DIR)
    app.run(debug=True, host='0.0.0.0', port=5000)