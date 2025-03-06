# School Attendance System with Facial Recognition

A web-based attendance system built with Flask that uses facial recognition to mark students as "Present" once per day. It captures student images dynamically from a webcam, stores them by filename (e.g., `samar.jpg`), and logs attendance in a text file.

## Features
- **Real-Time Facial Recognition**: Identifies enrolled students via a webcam feed.
- **Single Daily Attendance**: Marks each student "Present" only once per day.
- **Dynamic Enrollment**: Captures the current camera frame for new students, requiring only a name input.
- **Attendance Log**: View a table of attendance records.
- **Professional UI**: Modern design with navigation, status feedback, and styled tables.
- **No Database**: Uses file-based storage for simplicity.

## Project Structure

attendance_system/
│
├── static/                   # CSS and JS files
│   ├── style.css
│   └── script.js
├── templates/                # HTML templates
│   ├── index.html
│   ├── enroll.html
│   └── attendance.html
├── enrolled_students/        # Folder for student images
├── attendance_log.txt        # Attendance log file
├── app.py                    # Flask application
├── requirements.txt          # Python dependencies
└── README.md                 # This file



## Prerequisites
- Python 3.8 or higher
- A webcam (or IP camera with URL support)
- Git (for cloning the repository)

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/attendance_system.git
   cd attendance_system
2. **Install Dependencies**
   pip install -r requirements.txt


3. **enrolled_students folder**
   mkdir enrolled_students

4. ** Run the Application **
    python main.py
