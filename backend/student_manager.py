import csv
import os
import pandas as pd
import re

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