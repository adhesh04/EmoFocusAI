import cv2
import time
# import mediapipe as mp
import numpy as np
# from deepface import DeepFace
import math
import mediapipe as mp

try:
    # Try the standard internal path for Python 3.12
    from mediapipe.python.solutions import face_mesh as mp_face_mesh
    from mediapipe.python.solutions import drawing_utils as mp_drawing
except ImportError:
    try:
        # Try the top-level path
        import mediapipe.solutions.face_mesh as mp_face_mesh
    except ImportError:
        # Final fallback
        mp_face_mesh = mp.solutions.face_mesh

# mp_face_mesh = mp.solutions.face_mesh
class FocusService:
    def __init__(self, fps_limit=6):
        self.face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.last_frame_time = 0
        self.fps_limit = fps_limit
        self.smoothed_focus = None
        self.missing_face_frames = 0
        self.missing_threshold = 3  # tolerate 3 missed frames
        


    # ---------------- FPS CONTROL ----------------
    def _should_process(self):
        now = time.time()
        if now - self.last_frame_time >= 1 / self.fps_limit:
            self.last_frame_time = now
            return True
        return False

    # ---------------- GEOMETRY ----------------
    def _euclidean(self, p1, p2):
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    def extract_physical_features(self, frame):
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.face_mesh.process(rgb)

        if not res.multi_face_landmarks:
            return None

        lm = res.multi_face_landmarks[0].landmark

        # Gaze (eye openness proxy)
        left_eye = self._euclidean(
            (lm[33].x, lm[33].y),
            (lm[133].x, lm[133].y)
        )
        right_eye = self._euclidean(
            (lm[362].x, lm[362].y),
            (lm[263].x, lm[263].y)
        )
        gaze_score = (left_eye + right_eye) / 2

        # Head Pose (simple geometric proxy)
        pitch = lm[152].y - lm[1].y
        yaw = lm[1].x - 0.5

        # Emotion heuristics
        brow_furrow = abs(lm[70].y - lm[105].y)
        lip_compress = abs(lm[13].y - lm[14].y)

        return {
            "gaze": np.clip(gaze_score * 5, 0, 1),
            "pose": 1 - min(abs(yaw) + abs(pitch), 1),
            "brow": brow_furrow,
            "lip": lip_compress
        }

    def extract_focus_signals(self, frame):
        results = self.face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if not results.multi_face_landmarks:
            return None, None

        lm = results.multi_face_landmarks[0].landmark

    # ---------- HEAD POSTURE ----------
        nose = lm[1]
        head_score = max(0, 100 - abs(nose.x - 0.5) * 200)

    # ---------- IRIS GAZE ----------
        left_ratio = (lm[468].x - lm[33].x) / (lm[133].x - lm[33].x + 1e-6)
        right_ratio = (lm[473].x - lm[362].x) / (lm[263].x - lm[362].x + 1e-6)

        gaze_offset = abs(((left_ratio + right_ratio) / 2) - 0.5)
        eye_score = max(0, 100 - gaze_offset * 300)

    # ---------- EYE CLOSED ----------
        left_eye_open = abs(lm[159].y - lm[145].y)
        right_eye_open = abs(lm[386].y - lm[374].y)

        if left_eye_open < 0.01 and right_eye_open < 0.01:
            eye_score = 0

        return int(eye_score), int(head_score)

    # ---------------- EMOTION ----------------
    # def detect_emotion(self, frame, geometry):
    #     try:
    #         result = DeepFace.analyze(
    #             frame,
    #             actions=["emotion"],
    #             enforce_detection=False
    #         )[0]["emotion"]
    #     except:
    #         return "neutral", 0.5

    #     dominant = max(result, key=result.get)
    #     confidence = result[dominant] / 100

    #     # Heuristic adjustment for subtle emotions
    #     if dominant == "neutral":
    #         if geometry["brow"] > 0.02:
    #             return "frustrated", 0.6
    #         if geometry["lip"] < 0.01:
    #             return "sad", 0.55

    #     return dominant, confidence

    def detect_emotion(self, frame, geometry):
        brow = geometry["brow"]
        lip = geometry["lip"]
        if brow > 0.025:
            return "frustrated", 0.7
        elif lip < 0.008:
            return "stressed", 0.6
        elif geometry["gaze"] < 0.3:
            return "distracted", 0.65
        return "neutral", 0.5


    # ---------------- FOCUS ----------------
    def compute_focus(self, physical, digital, emotion_state):
    # def compute_focus(self, digital, emotion_state):
        emotion_penalty = 0.0
        if emotion_state in ["sad", "angry", "frustrated"]:
            emotion_penalty = 0.3

        physical_score = (physical["gaze"] + physical["pose"]) / 2
        cognitive_score = max(0, 1 - emotion_penalty)

        # return (
        #     0.5 * physical_score +
        #     0.3 * digital +
        #     0.2 * cognitive_score
        # )
        focus_score = int((eye * 0.4) + (head * 0.4) + (digital * 100 * 0.2))
        return focus_score


    # ---------------- MAIN PIPELINE ----------------
    # def process_frame(self, frame, digital_score):
    #     if not self._should_process():
    #         return None

    #     physical = self.extract_physical_features(frame)
    #     if not physical:
    #         return None

    #     emotion, confidence = self.detect_emotion(frame, physical)
    #     focus = self.compute_focus(physical, digital_score, emotion)

    #     return {
    #         "focus": round(focus, 3),
    #         "emotion": emotion,
    #         "emotion_confidence": round(confidence, 2)
    #     }
    def process_frame(self, frame, digital_score):
        if not self._should_process():
            return None
        # physical = self.extract_physical_features(frame)
        # if not physical:
        #     return None
        # emotion, confidence = self.detect_emotion(frame, physical)
        # eye, head = self.extract_focus_signals(frame)
        eye, head = self.extract_focus_signals(frame)

        if eye is None or head is None:
            self.missing_face_frames += 1

            if self.missing_face_frames >= self.missing_threshold:
                return {
                    "focus": 0.1,
                    "emotion": "no_face"
                }
            else:
                return None  # skip this frame silently
        else:
            self.missing_face_frames = 0

        # Fake geometry for emotion (demo safe)
        geometry = {
            "brow": 0.01,
            "lip": 0.01,
            "gaze": eye / 100
        }

        emotion, confidence = self.detect_emotion(frame, geometry)

# 🚨 FACE NOT DETECTED → STRONG PENALTY
        # if eye is None or head is None:
        #     tab_score = int(digital_score * 100)

        #     focus = int(
        #         (0 * 0.4) +        # eye
        #         (0 * 0.4) +        # head
        #         (tab_score * 0.2)  # digital only
        #     )
            
            # return {
            #     "focus": focus / 100,
            #     "emotion": "no_face"
            # }


    # Convert digital score (0–1) → 0–100
        tab_score = int(digital_score * 100)

        focus = int(
            (eye * 0.4) +
            (head * 0.4) +
            (tab_score * 0.2)
        )

        raw_focus = focus / 100
        # alpha = 0.7  # smoothing strength (0.6–0.8 is good)
        # alpha = 0.2
        # if self.smoothed_focus is None:
        #     self.smoothed_focus = raw_focus
        # else:
        #     self.smoothed_focus = (
        #         alpha * self.smoothed_focus +
        #         (1 - alpha) * raw_focus
        #     )

        return {
            # "focus": round(self.smoothed_focus, 3),
            "focus": round(raw_focus, 3),
            "emotion": emotion
        }


