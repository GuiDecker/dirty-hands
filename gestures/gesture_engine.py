"""
Gesture Engine - Reconhece gestos e emite ações abstratas
"""

import time
from collections import deque
from utils import config


class GestureEngine:
    """Reconhece gestos e emite ações abstratas"""
    
    INDEX_TIP = 8
    THUMB_TIP = 4
    MIDDLE_TIP = 12
    INDEX_PIP = 6
    MIDDLE_PIP = 10
    
    def __init__(self):
        self.history = deque(maxlen=10)
        self.last_click = 0
        self.scroll_active = False
        self.scroll_history = deque(maxlen=5)
        
        self.click_cooldown = config.CLICK_COOLDOWN
        self.pinch_threshold = config.PINCH_THRESHOLD
        self.swipe_threshold = config.SWIPE_THRESHOLD
        self.swipe_velocity_threshold = config.SWIPE_VELOCITY_THRESHOLD
        self.scroll_gesture_threshold = config.SCROLL_GESTURE_THRESHOLD
        self.scroll_direction_threshold = config.SCROLL_DIRECTION_THRESHOLD
    
    def update(self, landmarks):
        """Atualiza com novos landmarks e retorna lista de ações"""
        actions = []
        
        index_tip = landmarks.landmark[self.INDEX_TIP]
        thumb_tip = landmarks.landmark[self.THUMB_TIP]
        
        actions.append(("MOVE", index_tip.x, index_tip.y))
        
        dist = abs(index_tip.x - thumb_tip.x) + abs(index_tip.y - thumb_tip.y)
        if dist < self.pinch_threshold and time.time() - self.last_click > self.click_cooldown:
            actions.append(("CLICK",))
            self.last_click = time.time()
        
        swipe_action = self._detect_swipe(index_tip)
        if swipe_action:
            actions.append(swipe_action)
        
        scroll_gesture = self._detect_scroll_gesture(landmarks)
        if scroll_gesture:
            if scroll_gesture == "START_SCROLL" and not self.scroll_active:
                scroll_info = self._get_scroll_info(landmarks)
                if scroll_info:
                    direction, velocity = scroll_info
                    actions.append(("START_SCROLL", direction, velocity))
                    self.scroll_active = True
            elif scroll_gesture == "STOP_SCROLL" and self.scroll_active:
                actions.append(("STOP_SCROLL",))
                self.scroll_active = False
                self.scroll_history.clear()
            elif self.scroll_active:
                scroll_info = self._get_scroll_info(landmarks)
                if scroll_info:
                    direction, velocity = scroll_info
                    actions.append(("UPDATE_SCROLL", direction, velocity))
        
        self.history.append((index_tip.x, index_tip.y, time.time()))
        return actions
    
    def _detect_swipe(self, index_tip):
        """Detecta swipe horizontal baseado no histórico"""
        if len(self.history) < 3:
            return None
        
        initial_x, _, initial_time = self.history[0]
        current_x = index_tip.x
        current_time = time.time()
        
        dx = current_x - initial_x
        dt = current_time - initial_time
        
        if dt == 0:
            return None
        
        velocity = abs(dx) / dt
        
        if abs(dx) > self.swipe_threshold and velocity > self.swipe_velocity_threshold:
            return ("SWIPE_RIGHT",) if dx > 0 else ("SWIPE_LEFT",)
        
        return None
    
    def _detect_scroll_gesture(self, landmarks):
        """Detecta gesto de scroll: dois dedos estendidos"""
        index_tip = landmarks.landmark[self.INDEX_TIP]
        index_pip = landmarks.landmark[self.INDEX_PIP]
        middle_tip = landmarks.landmark[self.MIDDLE_TIP]
        middle_pip = landmarks.landmark[self.MIDDLE_PIP]
        
        index_extended = index_tip.y < index_pip.y
        middle_extended = middle_tip.y < middle_pip.y
        finger_distance = abs(index_tip.x - middle_tip.x) + abs(index_tip.y - middle_tip.y)
        fingers_close = finger_distance < self.scroll_gesture_threshold
        
        if index_extended and middle_extended and fingers_close:
            return "START_SCROLL"
        elif self.scroll_active:
            return "STOP_SCROLL"
        return None
    
    def _get_scroll_info(self, landmarks):
        """Detecta direção e velocidade do scroll baseado na posição Y dos dedos"""
        index_tip = landmarks.landmark[self.INDEX_TIP]
        middle_tip = landmarks.landmark[self.MIDDLE_TIP]
        
        avg_y = (index_tip.y + middle_tip.y) / 2
        self.scroll_history.append((avg_y, time.time()))
        
        if len(self.scroll_history) < 2:
            if avg_y < config.SCROLL_UP_ZONE:
                return ("UP", config.SCROLL_UP_BASE_VELOCITY)
            elif avg_y > 0.6:
                return ("DOWN", config.SCROLL_MIN_VELOCITY)
            return None
        
        initial_y, initial_time = self.scroll_history[0]
        current_y = avg_y
        current_time = time.time()
        
        dy = current_y - initial_y
        dt = current_time - initial_time
        
        if dt == 0:
            return None
        
        velocity_y = abs(dy) / dt
        min_velocity = config.SCROLL_MIN_VELOCITY
        max_velocity_threshold = config.SCROLL_MAX_VELOCITY_THRESHOLD
        
        if velocity_y >= max_velocity_threshold:
            normalized_velocity = 1.0
        elif velocity_y <= 0:
            normalized_velocity = min_velocity
        else:
            normalized_velocity = min_velocity + (velocity_y / max_velocity_threshold) * (1.0 - min_velocity)
        
        scroll_up_threshold = self.scroll_direction_threshold * config.SCROLL_UP_THRESHOLD_MULTIPLIER
        
        if abs(dy) > scroll_up_threshold if dy < 0 else self.scroll_direction_threshold:
            if dy < 0:
                boosted_velocity = min(1.0, normalized_velocity * config.SCROLL_UP_VELOCITY_BOOST)
                return ("UP", boosted_velocity)
            else:
                return ("DOWN", normalized_velocity)
        
        if avg_y < config.SCROLL_UP_ZONE:
            return ("UP", config.SCROLL_UP_BASE_VELOCITY)
        elif avg_y > 0.6:
            return ("DOWN", min_velocity)
        
        return None
    
    def reset(self):
        """Reseta o estado do engine"""
        self.history.clear()
        self.scroll_history.clear()
        self.last_click = 0
        self.scroll_active = False

