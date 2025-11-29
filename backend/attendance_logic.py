import cv2
import pandas as pd
import time
import datetime
import os
from backend.face_recognition import FaceRecognizer
from backend.attendance_handler import AttendanceHandler
from backend.student_manager import StudentManager

class AttendanceLogic:
    def __init__(self, base_dir, haarcascade_path, train_path, student_details_path, model_path):
        self.base_dir = base_dir
        self.haarcascade_path = haarcascade_path
        self.train_path = train_path
        self.student_details_path = student_details_path
        self.model_path = model_path
        
        self.face_recognizer = FaceRecognizer(haarcascade_path, model_path)
        self.attendance_handler = AttendanceHandler(os.path.join(base_dir, "Attendance"), student_details_path)
        self.student_manager = StudentManager(student_details_path)
    
    def start_attendance(self, subject):
        """
        Start attendance process
        Returns: (success, student_count, message)
        """
        try:
            # Load model
            if not self.face_recognizer.load_model():
                return False, 0, "Model not found! Train first."
            
            # Load student details
            df = pd.read_csv(self.student_details_path)
            
            if len(df) == 0:
                return False, 0, "No students registered!"
            
            # Start camera
            cam = cv2.VideoCapture(0)
            if not cam.isOpened():
                return False, 0, "Camera not found!"
            
            font_cv = cv2.FONT_HERSHEY_SIMPLEX
            attendance_records = []
            recognized_students = set()
            
            start_time = time.time()
            duration = 20  # 20 seconds
            
            while True:
                ret, frame = cam.read()
                if not ret:
                    break
                
                faces, gray = self.face_recognizer.get_faces_from_image(frame)
                
                for (x, y, w, h) in faces:
                    # Use improved recognition method
                    student_id, confidence, is_recognized = self.face_recognizer.recognize_face(
                        gray[y:y + h, x:x + w],
                        confidence_threshold=70
                    )
                    
                    if is_recognized and student_id is not None:
                        # Match by normalized ID: remove dash and compare as int
                        try:
                            normalized_ids = df["Enrollment"].astype(str).str.replace("-", "", regex=False).astype(int)
                            matches = normalized_ids == int(student_id)
                            student = df[matches]
                        except Exception:
                            student = pd.DataFrame()
                        
                        if len(student) > 0:
                            name = student["Name"].values[0]
                            
                            # Only record once per student
                            if student_id not in recognized_students:
                                ts = time.time()
                                date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                                time_str = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                                
                                record = self.attendance_handler.create_attendance_record(
                                    student_id, name, subject, date, time_str
                                )
                                if record:
                                    attendance_records.append(record)
                                    recognized_students.add(student_id)
                                    print(f"✓ Recognized: {name} (ID: {student_id}, Confidence: {confidence:.2f})")
                            
                            # Draw rectangle and name (Green = Recognized)
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 260, 0), 4)
                            cv2.putText(frame, f"{student_id}-{name}", (x + h, y), font_cv, 1, (255, 255, 0), 4)
                            cv2.putText(frame, f"Conf: {confidence:.1f}%", (x, y + h + 20), 
                                      font_cv, 0.6, (255, 255, 0), 2)
                        else:
                            # Unknown student
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 25, 255), 7)
                            cv2.putText(frame, "Unknown Student", (x + h, y), font_cv, 1, (0, 25, 255), 4)
                    else:
                        # Face detected but not recognized (Orange = Low confidence)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 165, 255), 2)
                        cv2.putText(frame, "Not Recognized", (x + h, y), font_cv, 0.7, (0, 165, 255), 2)
                        if confidence:
                            cv2.putText(frame, f"Conf: {confidence:.1f}%", (x, y + h + 20), 
                                      font_cv, 0.6, (0, 165, 255), 2)
                
                # Display timer and student count
                elapsed = int(time.time() - start_time)
                remaining = duration - elapsed
                cv2.putText(frame, f"Time: {remaining}s | Students: {len(recognized_students)}", 
                          (10, 30), font_cv, 1, (255, 255, 0), 2)
                
                cv2.imshow("Taking Attendance... (Press ESC to stop early)", frame)
                
                if remaining <= 0:
                    break
                
                if cv2.waitKey(30) & 0xFF == 27:  # ESC key
                    break
            
            cam.release()
            cv2.destroyAllWindows()
            
            # Save attendance
            if attendance_records:
                filepath, msg = self.attendance_handler.save_attendance(attendance_records, subject)
                return True, len(recognized_students), msg
            else:
                return False, 0, "No attendance recorded"
        
        except Exception as e:
            cv2.destroyAllWindows()
            return False, 0, f"Error: {str(e)}"