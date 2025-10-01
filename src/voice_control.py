# src/voice_control.py
import speech_recognition as sr
import pyttsx3
from object_detection import detect_target_object
import cv2

# Known object classes (subset of COCO)
KNOWN_CLASSES = {'bottle', 'cup', 'book', 'cell phone', 'keyboard'}

recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen_for_command():
    with sr.Microphone() as source:
        print("[LISTEN] Say command (e.g., 'fetch bottle')...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"[VOICE] You said: {command}")
        words = command.split()
        if words and words[-1] in KNOWN_CLASSES:
            return words[-1]
        else:
            speak("Object not recognized.")
            return None
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return None
    except sr.RequestError as e:
        speak("Speech service is down.")
        print(f"[ERROR] Google API error: {e}")
        return None

def main():
    speak("System ready. Say 'fetch' followed by an object.")
    target = listen_for_command()
    if target:
        speak(f"Searching for {target}. Please wait.")
        # Now start detection loop (simplified)
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        found = False
        for _ in range(100):  # Try for ~20 seconds
            ret, frame = cap.read()
            if not ret:
                break
            success, _ = detect_target_object(frame, target)
            if success:
                found = True
                break
        cap.release()
        if found:
            speak(f"{target} retrieved successfully!")
        else:
            speak(f"Could not find {target}.")

if __name__ == "__main__":
    main()
