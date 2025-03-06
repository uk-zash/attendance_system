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