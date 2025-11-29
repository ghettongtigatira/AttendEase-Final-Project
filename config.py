import os

# Base directory
BASE_DIR = r"C:\Users\cjele\Desktop\ATTENDANCE CHECKER FINAL PROJECT"

# Paths
HAARCASCADE_PATH = os.path.join(BASE_DIR, "haarcascade_frontalface_default.xml")
TRAIN_IMAGE_PATH = os.path.join(BASE_DIR, "TrainingImage")
MODEL_PATH = os.path.join(BASE_DIR, "TrainingImageLabel", "Trainner.yml")
STUDENT_DETAILS_PATH = os.path.join(BASE_DIR, "StudentDetails", "studentdetails.csv")
ATTENDANCE_PATH = os.path.join(BASE_DIR, "Attendance")
UI_IMAGE_PATH = os.path.join(BASE_DIR, "UI_Image")

# Create directories if they don't exist
os.makedirs(os.path.dirname(TRAIN_IMAGE_PATH), exist_ok=True)
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
os.makedirs(os.path.dirname(STUDENT_DETAILS_PATH), exist_ok=True)
os.makedirs(ATTENDANCE_PATH, exist_ok=True)

# Verify paths exist
print(f"Base DIR: {BASE_DIR}")
print(f"Haarcascade exists: {os.path.exists(HAARCASCADE_PATH)}")
print(f"Haarcascade file size: {os.path.getsize(HAARCASCADE_PATH) if os.path.exists(HAARCASCADE_PATH) else 'N/A'}")