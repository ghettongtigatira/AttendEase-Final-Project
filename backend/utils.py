import pyttsx3

class TextToSpeech:
    """Handle text-to-speech functionality"""
    
    @staticmethod
    def speak(text):
        """Convert text to speech"""
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Error in text-to-speech: {str(e)}")

def validate_enrollment_number(enrollment_num):
    """Validate enrollment number (digits only)"""
    try:
        return enrollment_num.isdigit()
    except Exception:
        return False

def validate_name(name):
    """Validate student name"""
    try:
        return len(name) > 0 and len(name) <= 100
    except Exception:
        return False

def validate_subject(subject):
    """Validate subject name"""
    try:
        return len(subject) > 0 and len(subject) <= 100
    except Exception:
        return False