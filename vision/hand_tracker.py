"""
Hand Tracker - MVP
Captura frame, detecta mão, retorna landmarks normalizados
"""

import cv2
import mediapipe as mp


class HandTracker:
    """
    Rastreia mãos usando MediaPipe
    Retorna landmarks normalizados [0-1]
    """
    
    def __init__(self):
        # Tentar usar API antiga primeiro
        try:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7
            )
        except AttributeError:
            # Se não tiver solutions, usar importação direta
            from mediapipe.python.solutions import hands
            self.hands = hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7
            )
    
    def process(self, frame):
        """
        Processa um frame e retorna landmarks da primeira mão detectada
        
        Args:
            frame: Frame BGR do OpenCV
            
        Returns:
            HandLandmarks do MediaPipe ou None se não detectar mão
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        
        result = self.hands.process(rgb)
        
        if not result.multi_hand_landmarks:
            return None
        
        # Retornar primeira mão detectada
        return result.multi_hand_landmarks[0]
    
    def cleanup(self):
        """Libera recursos"""
        self.hands.close()

