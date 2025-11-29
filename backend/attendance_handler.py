import os
import csv
import pandas as pd
import datetime
import time

class AttendanceHandler:
    def __init__(self, attendance_path, student_details_path):
        self.attendance_path = attendance_path
        self.student_details_path = student_details_path
        # Ensure base attendance directory exists
        os.makedirs(self.attendance_path, exist_ok=True)

    # -------------------- Subject Management --------------------
    def _subjects_file(self):
        return os.path.join(self.attendance_path, "subjects.csv")

    def add_subject(self, subject):
        """Register a subject; ensure folder exists and record in subjects.csv"""
        try:
            subject = str(subject).strip()
            if not subject:
                return False, "Subject name is required"

            # Create folder
            subject_path = os.path.join(self.attendance_path, subject)
            os.makedirs(subject_path, exist_ok=True)

            # Append to subjects.csv if not present
            subjects_file = self._subjects_file()
            rows = []
            if os.path.exists(subjects_file):
                try:
                    rows = pd.read_csv(subjects_file).to_dict("records")
                except Exception:
                    rows = []

            if not any(r.get("Subject") == subject for r in rows):
                created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                rows.append({"Subject": subject, "CreatedAt": created_at})
                pd.DataFrame(rows).to_csv(subjects_file, index=False)

            # Ensure a summary file exists
            summary_file = os.path.join(subject_path, "attendance.csv")
            if not os.path.exists(summary_file):
                pd.DataFrame(columns=[
                    "Enrollment", "Name", "PresentCount", "TotalSessions", "Attendance"
                ]).to_csv(summary_file, index=False)

            return True, f"Subject '{subject}' added"
        except Exception as e:
            return False, f"Error adding subject: {str(e)}"

    def list_subjects(self):
        """Return list of registered subjects"""
        try:
            subjects_file = self._subjects_file()
            if not os.path.exists(subjects_file):
                return [], "No subjects registered"
            df = pd.read_csv(subjects_file)
            subs = df["Subject"].dropna().astype(str).tolist()
            return subs, "Success"
        except Exception as e:
            return [], f"Error reading subjects: {str(e)}"
    
    def create_attendance_record(self, enrollment_id, name, subject, date=None, time_str=None):
        """Create an attendance record"""
        try:
            if date is None:
                date = datetime.datetime.now().strftime("%Y-%m-%d")
            if time_str is None:
                time_str = datetime.datetime.now().strftime("%H:%M:%S")
            
            return {
                "Enrollment": enrollment_id,
                "Name": name,
                "Date": date,
                "Time": time_str
            }
        except Exception as e:
            print(f"Error creating attendance record: {str(e)}")
            return None
    
    def save_attendance(self, attendance_data, subject):
        """Save attendance to CSV"""
        try:
            ts = time.time()
            date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
            time_stamp = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
            hour, minute, second = time_stamp.split(":")
            
            subject_path = os.path.join(self.attendance_path, subject)
            os.makedirs(subject_path, exist_ok=True)
            
            filename = f"{subject}_{date}_{hour}-{minute}-{second}.csv"
            filepath = os.path.join(subject_path, filename)
            
            df = pd.DataFrame(attendance_data)
            df = df.drop_duplicates(["Enrollment"], keep="first")
            df.to_csv(filepath, index=False)
            
            # After saving a session file, update subject summary
            self.calculate_attendance(subject)

            return filepath, f"Attendance saved successfully for {subject}"
        except Exception as e:
            return None, f"Error saving attendance: {str(e)}"
    
    def get_attendance_records(self, subject):
        """Get all attendance records for a subject"""
        try:
            subject_path = os.path.join(self.attendance_path, subject)
            if not os.path.exists(subject_path):
                return [], f"No attendance records found for {subject}"
            
            csv_files = [f for f in os.listdir(subject_path) if f.endswith('.csv')]
            
            if len(csv_files) == 0:
                return [], f"No attendance files found for {subject}"
            
            attendance_files = [os.path.join(subject_path, f) for f in csv_files 
                              if f.startswith(subject)]
            
            return attendance_files, "Success"
        except Exception as e:
            return [], f"Error getting attendance records: {str(e)}"
    
    def calculate_attendance(self, subject):
        """Calculate attendance percentage"""
        try:
            attendance_files, msg = self.get_attendance_records(subject)

            if len(attendance_files) == 0:
                return None, msg

            # Normalize each session file to a consistent schema:
            # Enrollment, Name, Present (1 per session file)
            normalized = []
            for fpath in attendance_files:
                try:
                    df = pd.read_csv(fpath)
                    # Ensure required columns exist
                    if not {"Enrollment", "Name"}.issubset(df.columns):
                        # Skip files that don't match expected schema
                        continue
                    # Mark everyone listed in this file as present for that session
                    df = df[["Enrollment", "Name"]].copy()
                    df["Present"] = 1
                    normalized.append(df)
                except Exception:
                    # Skip unreadable files but continue processing others
                    continue

            if not normalized:
                return None, "No valid attendance files to process"

            all_sessions_df = pd.concat(normalized, ignore_index=True)
            # Aggregate presents per student
            agg = (
                all_sessions_df
                .groupby(["Enrollment", "Name"], as_index=False)
                .agg({"Present": "sum"})
            )

            total_sessions = len(attendance_files)
            # Compute percentage and summary columns
            agg["TotalSessions"] = total_sessions
            agg["PresentCount"] = agg["Present"].astype(int)
            agg.drop(columns=["Present"], inplace=True)
            agg["Attendance"] = (agg["PresentCount"] / agg["TotalSessions"] * 100).round().astype(int).astype(str) + "%"

            subject_path = os.path.join(self.attendance_path, subject)
            output_file = os.path.join(subject_path, "attendance.csv")
            agg.to_csv(output_file, index=False)

            return agg, "Attendance calculated successfully"
        except Exception as e:
            return None, f"Error calculating attendance: {str(e)}"
    
    def reset_subject_attendance(self, subject):
        """Reset all attendance records for a subject"""
        try:
            import shutil
            subject_path = os.path.join(self.attendance_path, subject)
            
            if os.path.exists(subject_path):
                shutil.rmtree(subject_path)
                os.makedirs(subject_path, exist_ok=True)
                return True, f"Attendance records for {subject} have been reset"
            else:
                return False, f"No attendance records found for {subject}"
        except Exception as e:
            return False, f"Error resetting attendance: {str(e)}"
    
    def open_attendance_folder(self, subject):
        """Open attendance folder in file explorer"""
        try:
            subject_path = os.path.join(self.attendance_path, subject)
            if os.path.exists(subject_path):
                os.startfile(subject_path)
                return True
            else:
                return False
        except Exception as e:
            print(f"Error opening folder: {str(e)}")
            return False

    def remove_subject(self, subject):
        """Remove a subject from registry and delete its folder only if empty.
        Returns (success: bool, message: str)
        """
        try:
            subject = str(subject).strip()
            if not subject:
                return False, "Subject name is required"

            subject_path = os.path.join(self.attendance_path, subject)

            # Check for existing records
            has_records = False
            if os.path.exists(subject_path):
                files = [f for f in os.listdir(subject_path) if f.endswith('.csv')]
                has_records = len(files) > 0

            if has_records:
                return False, f"Subject '{subject}' has attendance records. Reset before removing."

            # Remove folder if exists (and empty)
            if os.path.isdir(subject_path):
                try:
                    os.rmdir(subject_path)
                except OSError:
                    # Non-empty for some other reason
                    return False, f"Unable to remove folder for '{subject}'. Ensure it is empty."

            # Update subjects.csv registry
            subjects_file = self._subjects_file()
            if os.path.exists(subjects_file):
                try:
                    df = pd.read_csv(subjects_file)
                    df = df[df["Subject"] != subject]
                    df.to_csv(subjects_file, index=False)
                except Exception:
                    return False, "Error updating subjects registry"

            return True, f"Subject '{subject}' removed"
        except Exception as e:
            return False, f"Error removing subject: {str(e)}"