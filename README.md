# AttendEase - Final Project

A streamlined attendance system for BSCS 3B Computer Science students, built using Python and OpenCV for fast and accurate face recognition to record and monitor attendance automatically.

## Features
- 👤 **Face Recognition**: Automatic student identification using OpenCV
- 📊 **Attendance Tracking**: Real-time attendance recording and management
- 📝 **Subject Management**: Organize attendance by different subjects/courses
- 📁 **Export Reports**: Generate attendance reports in CSV format
- 🎨 **User-Friendly Interface**: Clean and intuitive GUI built with Tkinter

## Prerequisites

Before you begin, ensure you have the following installed on your system:
- **Python 3.8 or higher** ([Download Python](https://www.python.org/downloads/))
- **Git** ([Download Git](https://git-scm.com/downloads))
- **Webcam** (for face recognition)

## Setup Instructions

Follow these steps to set up the AttendEase system on your local machine:

### 1. Clone the Repository

Open your terminal/command prompt and run:

```bash
git clone https://github.com/ghettongtigatira/AttendEase-Final-Project.git
cd AttendEase-Final-Project
```

### 2. Create a Virtual Environment (Recommended)

Creating a virtual environment keeps your project dependencies isolated:

**On Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` appear in your terminal prompt, indicating the virtual environment is active.

### 3. Install Required Dependencies

With the virtual environment activated, install all required packages:

```bash
pip install -r requirements.txt
```

This will install:
- `numpy` - Numerical computing
- `opencv-python` & `opencv-contrib-python` - Computer vision and face recognition
- `pandas` - Data manipulation and CSV handling
- `pillow` - Image processing
- `openpyxl` - Excel file support
- `pyttsx3` - Text-to-speech functionality

### 4. Verify Installation

Check that all packages are installed correctly:

```bash
pip list
```

### 5. Run the Application

Start the AttendEase system:

```bash
python main.py
```

The main window should appear, and you're ready to use the system!

## First-Time Usage Guide

### Registering Students

1. Click **"Register New Student"** in the main window
2. Fill in the student details:
   - Student ID
   - Name
   - Course/Section
3. Position your face in front of the webcam
4. Click **"Capture Images"** to train the face recognition model
5. Multiple images will be captured for better accuracy

### Managing Subjects

1. Click **"Manage Subjects"** to add or remove subjects/courses
2. Add subjects where you want to track attendance
3. Each subject will have its own attendance records

### Taking Attendance

1. Select a subject from the dropdown menu
2. Click **"Take Attendance"**
3. The system will activate the webcam and recognize registered faces
4. Attendance is automatically recorded with date and timestamp

### Viewing Attendance Records

1. Click **"View Attendance"** in the main window
2. Select a subject to view its attendance history
3. Export reports as CSV files for further analysis

## Project Structure

```
AttendEase-Final-Project/
├── main.py                 # Application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── backend/              # Backend logic
│   ├── face_recognition.py
│   ├── attendance_logic.py
│   ├── student_manager.py
│   └── attendance_handler.py
├── frontend/             # GUI components
│   ├── main_window.py
│   ├── register_window.py
│   ├── attendance_window.py
│   └── view_attendance_window.py
├── Attendance/           # Attendance records (CSV files)
├── StudentDetails/       # Student information
├── TrainingImage/        # Captured face images
└── TrainingImageLabel/   # Trained ML models

```

## Troubleshooting

### Webcam Not Working
- Ensure your webcam is properly connected
- Check if other applications are using the webcam
- Grant camera permissions to Python

### Import Errors
- Make sure the virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

### Face Recognition Not Accurate
- Ensure good lighting conditions
- Capture more training images during registration
- Position face directly in front of the camera

### Module Not Found Error
- Verify you're in the correct directory
- Check that all files are properly cloned from the repository

## Contributing

If you find any bugs or want to add features:
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Open a Pull Request

## License

This project is developed as a final project for BSCS 3B students. See the [LICENSE](LICENSE) file for details.

## Support

For questions or issues, please:
- Open an issue on GitHub
- Contact the development team
- Check the troubleshooting section above

## Author

**Cj Eleazar** - *Project Lead & Developer*  
GitHub: [@ghettongtigatira](https://github.com/ghettongtigatira)

---

**Developed by BSCS 3B Students** | **Built with Python & OpenCV**