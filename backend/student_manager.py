import csv
import os
import pandas as pd
import re
import cv2
from PIL import Image

class StudentManager:
    def __init__(self, student_details_path):
        self.student_details_path = student_details_path
        self.ensure_csv_exists()
    
    def ensure_csv_exists(self):
        """Ensure student details CSV exists with headers"""
        try:
            os.makedirs(os.path.dirname(self.student_details_path), exist_ok=True)
            
            if not os.path.exists(self.student_details_path):
                with open(self.student_details_path, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Enrollment", "Name", "Subjects"])
            else:
                # Ensure existing CSV has Subjects column
                df = pd.read_csv(self.student_details_path)
                if "Subjects" not in df.columns:
                    df["Subjects"] = ""
                    df.to_csv(self.student_details_path, index=False)
        except Exception as e:
            print(f"Error ensuring CSV exists: {str(e)}")
    
    def add_student(self, enrollment_id, name, subjects=None):
        """Add a new student with ID validation and duplicate prevention.
        Enrollment ID must match the strict format: 4 digits, a dash, 4 digits (e.g., 0123-0263).
        subjects: list of subject names the student is enrolled in
        """
        try:
            # Validate ID format: exactly 4 digits, '-', then 4 digits
            if not isinstance(enrollment_id, str):
                return False, "Enrollment ID must be a string"
            if not re.match(r"^\d{4}-\d{4}$", enrollment_id.strip()):
                return False, "Invalid ID format. Use ####-#### (e.g., 0123-0263)"

            # Validate name
            if not isinstance(name, str) or not name.strip():
                return False, "Name is required"

            df = pd.read_csv(self.student_details_path)

            # Prevent duplicate registration by ID
            if enrollment_id in df["Enrollment"].astype(str).values:
                return False, f"Student with ID {enrollment_id} already exists"

            # Format subjects as semicolon-separated string
            subjects_str = ";".join(subjects) if subjects else ""
            
            new_student = {"Enrollment": enrollment_id, "Name": name.strip(), "Subjects": subjects_str}
            df = pd.concat([df, pd.DataFrame([new_student])], ignore_index=True)
            df.to_csv(self.student_details_path, index=False)

            return True, f"Student {name.strip()} added successfully"
        except Exception as e:
            return False, f"Error adding student: {str(e)}"
    
    def get_all_students(self):
        """Get all registered students"""
        try:
            df = pd.read_csv(self.student_details_path)
            return df, "Success"
        except Exception as e:
            return None, f"Error getting students: {str(e)}"
    
    def get_student(self, enrollment_id):
        """Get specific student"""
        try:
            df = pd.read_csv(self.student_details_path)
            student = df[df["Enrollment"] == enrollment_id]
            
            if len(student) > 0:
                return student.iloc[0], True
            else:
                return None, False
        except Exception as e:
            return None, False
    
    def remove_student(self, enrollment_id):
        """Remove a student"""
        try:
            df = pd.read_csv(self.student_details_path)
            df = df[df["Enrollment"] != enrollment_id]
            df.to_csv(self.student_details_path, index=False)
            
            return True, "Student removed successfully"
        except Exception as e:
            return False, f"Error removing student: {str(e)}"
    
    def reset_all_students(self):
        """Reset all student data"""
        try:
            with open(self.student_details_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Enrollment", "Name", "Subjects"])
            
            return True, "All student data has been reset"
        except Exception as e:
            return False, f"Error resetting data: {str(e)}"
    
    def update_student_subjects(self, enrollment_id, subjects):
        """Update subjects for an existing student"""
        try:
            df = pd.read_csv(self.student_details_path)
            
            if enrollment_id not in df["Enrollment"].astype(str).values:
                return False, f"Student with ID {enrollment_id} not found"
            
            subjects_str = ";".join(subjects) if subjects else ""
            df.loc[df["Enrollment"].astype(str) == enrollment_id, "Subjects"] = subjects_str
            df.to_csv(self.student_details_path, index=False)
            
            return True, "Subjects updated successfully"
        except Exception as e:
            return False, f"Error updating subjects: {str(e)}"
    
    def get_student_subjects(self, enrollment_id):
        """Get subjects for a specific student"""
        try:
            df = pd.read_csv(self.student_details_path)
            student = df[df["Enrollment"].astype(str) == enrollment_id]
            
            if len(student) > 0:
                subjects_str = student.iloc[0].get("Subjects", "")
                if pd.isna(subjects_str) or subjects_str == "":
                    return [], True
                return subjects_str.split(";"), True
            return [], False
        except Exception as e:
            return [], False

    # ============== ID PHOTO MANAGEMENT ==============
    
    def get_id_photos_path(self):
        """Get the path to ID photos directory"""
        base_dir = os.path.dirname(os.path.dirname(self.student_details_path))
        id_photos_path = os.path.join(base_dir, "StudentDetails", "IDPhotos")
        os.makedirs(id_photos_path, exist_ok=True)
        return id_photos_path
    
    def save_id_photo(self, enrollment_id, image_source, is_file_path=False):
        """
        Save an ID photo for a student.
        
        Args:
            enrollment_id: Student's enrollment ID
            image_source: Either a file path (string) or a cv2 image (numpy array)
            is_file_path: True if image_source is a file path, False if it's a cv2 image
        
        Returns:
            (success: bool, message: str)
        """
        try:
            id_photos_path = self.get_id_photos_path()
            photo_path = os.path.join(id_photos_path, f"{enrollment_id}.jpg")
            
            if is_file_path:
                # Copy from file
                img = Image.open(image_source)
                # Resize to standard ID photo size (maintain aspect ratio)
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                img.save(photo_path, "JPEG", quality=95)
            else:
                # Save from cv2 image (numpy array)
                # Convert BGR to RGB if needed
                if len(image_source.shape) == 3 and image_source.shape[2] == 3:
                    image_rgb = cv2.cvtColor(image_source, cv2.COLOR_BGR2RGB)
                else:
                    image_rgb = image_source
                img = Image.fromarray(image_rgb)
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                img.save(photo_path, "JPEG", quality=95)
            
            return True, f"ID photo saved for {enrollment_id}"
        except Exception as e:
            return False, f"Error saving ID photo: {str(e)}"
    
    def capture_id_photo_from_camera(self, enrollment_id, cascade_path=None):
        """
        Capture an ID photo directly from camera with face detection.
        
        Args:
            enrollment_id: Student's enrollment ID
            cascade_path: Path to haarcascade file (optional)
        
        Returns:
            (success: bool, message: str, captured_image: numpy array or None)
        """
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return False, "Could not open camera", None
            
            # Load face cascade if provided
            face_cascade = None
            if cascade_path and os.path.exists(cascade_path):
                face_cascade = cv2.CascadeClassifier(cascade_path)
            
            captured_frame = None
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                display_frame = frame.copy()
                
                # Detect face if cascade available
                if face_cascade is not None:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(100, 100))
                    
                    for (x, y, w, h) in faces:
                        # Draw rectangle around face
                        cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 229, 255), 3)
                        # Add label
                        cv2.putText(display_frame, "Face Detected", (x, y-10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 229, 255), 2)
                
                # Add instructions
                cv2.putText(display_frame, "Press SPACE to capture, ESC to cancel", 
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 229, 255), 2)
                cv2.putText(display_frame, f"Student ID: {enrollment_id}", 
                            (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                cv2.imshow("Capture ID Photo", display_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == 32:  # SPACE key - capture
                    captured_frame = frame.copy()
                    break
                elif key == 27:  # ESC key - cancel
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            if captured_frame is not None:
                # Save the captured photo
                success, msg = self.save_id_photo(enrollment_id, captured_frame, is_file_path=False)
                return success, msg, captured_frame
            else:
                return False, "Photo capture cancelled", None
                
        except Exception as e:
            return False, f"Error capturing ID photo: {str(e)}", None
    
    def get_id_photo_path(self, enrollment_id):
        """Get the file path of a student's ID photo"""
        id_photos_path = self.get_id_photos_path()
        photo_path = os.path.join(id_photos_path, f"{enrollment_id}.jpg")
        if os.path.exists(photo_path):
            return photo_path
        return None
    
    def has_id_photo(self, enrollment_id):
        """Check if a student has an ID photo"""
        return self.get_id_photo_path(enrollment_id) is not None
    
    def delete_id_photo(self, enrollment_id):
        """Delete a student's ID photo"""
        try:
            photo_path = self.get_id_photo_path(enrollment_id)
            if photo_path and os.path.exists(photo_path):
                os.remove(photo_path)
                return True, "ID photo deleted"
            return False, "No ID photo found"
        except Exception as e:
            return False, f"Error deleting ID photo: {str(e)}"