import cv2
import os
import numpy as np
from PIL import Image

class FaceRecognizer:
    def __init__(self, haarcascade_path, model_path):
        self.haarcascade_path = haarcascade_path
        self.model_path = model_path
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.cascade = None
        
        # Safely load cascade with try-except
        try:
            if os.path.exists(haarcascade_path):
                self.cascade = cv2.CascadeClassifier(haarcascade_path)
                if self.cascade.empty():
                    print(f"Warning: Haarcascade file is empty or invalid: {haarcascade_path}")
                    self.cascade = None
                else:
                    print(f"✓ Haarcascade loaded successfully")
            else:
                print(f"Warning: Haarcascade file not found at {haarcascade_path}")
        except Exception as e:
            print(f"Error loading haarcascade: {str(e)}")
            self.cascade = None
    
    def load_model(self):
        """Load trained model"""
        try:
            if not os.path.exists(self.model_path):
                print(f"Model not found at {self.model_path}")
                return False
            
            self.recognizer.read(self.model_path)
            print(f"✓ Model loaded successfully")
            return True
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
    
    def train_model(self, faces, ids):
        """Train the face recognition model"""
        try:
            if len(faces) == 0:
                raise ValueError("No training images found")
            
            print(f"Training model with {len(faces)} images from {len(set(ids))} students...")
            self.recognizer.train(faces, np.array(ids))
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            self.recognizer.save(self.model_path)
            print(f"✓ Model trained and saved successfully")
            return True
        except Exception as e:
            print(f"Error training model: {str(e)}")
            return False
    
    def predict_face(self, face_image):
        """Predict face ID and confidence"""
        try:
            Id, conf = self.recognizer.predict(face_image)
            return Id, conf
        except Exception as e:
            print(f"Error predicting face: {str(e)}")
            return None, None
    
    def get_faces_from_image(self, image):
        """Detect faces in image"""
        try:
            if self.cascade is None:
                print("Error: Cascade classifier not loaded")
                return [], None
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # FIXED: Better face detection parameters
            faces = self.cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,      # More sensitive detection
                minNeighbors=5,       # Better accuracy
                minSize=(30, 30),     # Minimum face size
                maxSize=(300, 300)    # Maximum face size
            )
            return faces, gray
        except Exception as e:
            print(f"Error detecting faces: {str(e)}")
            return [], None
    
    def capture_faces(self, enrollment_id, name, training_path, samples=50):
        """Capture face images from camera"""
        try:
            camera = cv2.VideoCapture(0)
            if not camera.isOpened():
                return 0, "Camera not found"
            
            sample_num = 0
            folder_path = os.path.join(training_path, str(enrollment_id))
            os.makedirs(folder_path, exist_ok=True)
            
            print(f"Capturing {samples} samples for {name} (ID: {enrollment_id})...")
            
            while True:
                ret, frame = camera.read()
                if not ret:
                    break
                
                faces, gray = self.get_faces_from_image(frame)
                
                if len(faces) == 0:
                    # Show message if no face detected
                    cv2.putText(frame, "No face detected", (50, 50), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    sample_num += 1
                    
                    # Save the face region
                    face_region = gray[y:y + h, x:x + w]
                    image_path = os.path.join(folder_path, f"{name}_{enrollment_id}_{sample_num}.jpg")
                    cv2.imwrite(image_path, face_region)
                    
                    # Display progress
                    cv2.putText(frame, f"Samples: {sample_num}/{samples}", (x, y - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, name, (x, y + h + 25),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                cv2.imshow(f"Capturing face for {name} - Press ESC to stop", frame)
                key = cv2.waitKey(100) & 0xFF
                
                if key == 27 or sample_num >= samples:  # ESC key or samples reached
                    break
            
            camera.release()
            cv2.destroyAllWindows()
            
            return sample_num, f"✓ Captured {sample_num} images for {name}"
        
        except Exception as e:
            cv2.destroyAllWindows()
            return 0, f"Error: {str(e)}"
    
    def get_training_data(self, training_path):
        """Extract training data from images"""
        try:
            if not os.path.exists(training_path):
                return [], []
            
            student_folders = [os.path.join(training_path, d) for d in os.listdir(training_path) 
                             if os.path.isdir(os.path.join(training_path, d))]
            
            if len(student_folders) == 0:
                return [], []
            
            faces = []
            ids = []
            
            print(f"Loading training data from {len(student_folders)} students...")
            
            for folder in student_folders:
                for image_name in os.listdir(folder):
                    if image_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                        try:
                            image_path = os.path.join(folder, image_name)
                            image = Image.open(image_path).convert("L")
                            image_np = np.array(image, "uint8")
                            
                            # Parse enrollment ID (supports ####-#### format)
                            try:
                                enrollment_str = image_name.split("_")[1]
                                label_int = int(enrollment_str.replace("-", ""))
                            except (IndexError, ValueError):
                                print(f"Warning: Could not parse enrollment ID from {image_name}")
                                continue
                            
                            faces.append(image_np)
                            ids.append(label_int)
                        except Exception as e:
                            print(f"Error processing {image_name}: {str(e)}")
                            continue
            
            print(f"✓ Loaded {len(faces)} images for {len(set(ids))} unique students")
            return faces, ids
        
        except Exception as e:
            print(f"Error getting training data: {str(e)}")
            return [], []
    
    def recognize_face(self, face_image, confidence_threshold=70):
        """
        Recognize a face with confidence threshold
        Returns: (student_id, confidence, is_recognized)
        """
        try:
            student_id, confidence = self.predict_face(face_image)
            
            # FIXED: Better confidence threshold logic
            if student_id is None:
                return None, None, False
            
            is_recognized = confidence < confidence_threshold
            
            return student_id, confidence, is_recognized
        except Exception as e:
            print(f"Error recognizing face: {str(e)}")
            return None, None, False