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
    RING_TIP = 16
    PINKY_TIP = 20
    INDEX_PIP = 6
    MIDDLE_PIP = 10
    RING_PIP = 14
    PINKY_PIP = 18
    
    # Dedos que contam para velocidade do scroll (polegar excluído): (tip, pip)
    SCROLL_FINGERS = [
        (INDEX_TIP, INDEX_PIP),
        (MIDDLE_TIP, MIDDLE_PIP),
        (RING_TIP, RING_PIP),
        (PINKY_TIP, PINKY_PIP),
    ]
    
    def __init__(self):
        self.history = deque(maxlen=10)
        self.last_click = 0
        self.scroll_active = False
        
        self.click_cooldown = config.CLICK_COOLDOWN
        self.pinch_threshold = config.PINCH_THRESHOLD
        self.swipe_threshold = config.SWIPE_THRESHOLD
        self.swipe_velocity_threshold = config.SWIPE_VELOCITY_THRESHOLD
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
        
        scroll_result = self._detect_scroll_gesture(landmarks)
        if scroll_result:
            gesture_type, direction, velocity = scroll_result
            if gesture_type == "START_SCROLL" and not self.scroll_active:
                actions.append(("START_SCROLL", direction, velocity))
                self.scroll_active = True
            elif gesture_type == "STOP_SCROLL" and self.scroll_active:
                actions.append(("STOP_SCROLL",))
                self.scroll_active = False
            elif gesture_type == "UPDATE_SCROLL" and self.scroll_active:
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
        """
        Detecta gesto de scroll por orientação da mão e quantidade de dedos.
        - Mão para cima (dedos estendidos para cima) = scroll para cima.
        - Mão para baixo (dedos estendidos para baixo) = scroll para baixo.
        - Velocidade = número de dedos estendidos (1 a 4), excluindo o polegar.
        Retorna (tipo_gesto, direção, velocidade) ou None.
        """
        index_tip = landmarks.landmark[self.INDEX_TIP]
        index_pip = landmarks.landmark[self.INDEX_PIP]
        dy_index = index_tip.y - index_pip.y

        # Direção: indicador define se a mão está "para cima" ou "para baixo"
        if dy_index < -self.scroll_direction_threshold:
            direction = "UP"   # ponta do dedo acima da junta = mão ereta para cima
        elif dy_index > self.scroll_direction_threshold:
            direction = "DOWN"  # ponta do dedo abaixo da junta = mão ereta para baixo
        else:
            # Orientação ambígua ou mão aberta → para tudo na hora
            if self.scroll_active:
                return ("STOP_SCROLL", None, None)
            return None

        # Conta quantos dedos (exceto polegar) estão claramente estendidos na direção
        extended_count = 0
        for tip_idx, pip_idx in self.SCROLL_FINGERS:
            tip = landmarks.landmark[tip_idx]
            pip = landmarks.landmark[pip_idx]
            if direction == "UP":
                extended = tip.y < pip.y - self.scroll_direction_threshold * 0.5
            else:
                extended = tip.y > pip.y + self.scroll_direction_threshold * 0.5
            if extended:
                extended_count += 1

        if extended_count == 0:
            if self.scroll_active:
                return ("STOP_SCROLL", None, None)
            return None

        # Velocidade: 1 dedo = 0.25, 2 = 0.5, 3 = 0.75, 4 = 1.0
        velocity = (extended_count / 4.0)

        if not self.scroll_active:
            return ("START_SCROLL", direction, velocity)
        return ("UPDATE_SCROLL", direction, velocity)
    
    def reset(self):
        """Reseta o estado do engine"""
        self.history.clear()
        self.last_click = 0
        self.scroll_active = False

