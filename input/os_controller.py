"""
OS Controller - Controle de mouse e teclado
"""

import pyautogui
import threading
import time
from utils import config
from utils.filters import ExponentialMovingAverage


class OSController:
    """Controlador de input do sistema operacional"""
    
    def __init__(self):
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0
        
        self.screen_w, self.screen_h = pyautogui.size()
        self.cursor_filter = ExponentialMovingAverage(alpha=config.EMA_ALPHA)
        self.last_pos = None
        
        self.scroll_thread = None
        self.scroll_active = False
        self.scroll_direction = "DOWN"
        self.scroll_velocity = config.SCROLL_MIN_VELOCITY
        self.scroll_lock = threading.Lock()
    
    def move_cursor(self, x, y):
        """Move cursor para coordenadas normalizadas [0-1]"""
        smoothed = self.cursor_filter.update((x, y))
        if smoothed is None:
            return
        
        x, y = smoothed
        
        if self.last_pos:
            dx = abs(x - self.last_pos[0])
            dy = abs(y - self.last_pos[1])
            if dx < config.DEAD_ZONE and dy < config.DEAD_ZONE:
                return
        
        self.last_pos = (x, y)
        
        pixel_x = int(x * self.screen_w)
        pixel_y = int(y * self.screen_h)
        pixel_x = max(0, min(pixel_x, self.screen_w - 1))
        pixel_y = max(0, min(pixel_y, self.screen_h - 1))
        
        pyautogui.moveTo(pixel_x, pixel_y, duration=0)
    
    def click(self):
        """Clique esquerdo"""
        pyautogui.click()
    
    def next_page(self):
        """Próxima página (seta direita)"""
        pyautogui.press('right')
    
    def prev_page(self):
        """Página anterior (seta esquerda)"""
        pyautogui.press('left')
    
    def start_infinite_scroll(self, direction="DOWN", velocity=None):
        """Inicia scroll infinito contínuo"""
        with self.scroll_lock:
            if self.scroll_active:
                self.scroll_direction = direction
                if velocity is not None:
                    self.scroll_velocity = max(config.SCROLL_MIN_VELOCITY, min(1.0, velocity))
                return
            
            self.scroll_active = True
            self.scroll_direction = direction
            self.scroll_velocity = velocity if velocity is not None else config.SCROLL_MIN_VELOCITY
            
            def scroll_loop():
                while True:
                    with self.scroll_lock:
                        is_active = self.scroll_active
                        current_direction = self.scroll_direction
                        current_velocity = self.scroll_velocity
                    
                    if not is_active:
                        break
                    
                    base_amount = config.SCROLL_AMOUNT
                    max_amount = config.SCROLL_MAX_AMOUNT
                    scroll_amount = base_amount + (max_amount - base_amount) * current_velocity
                    
                    if current_direction == "UP":
                        scroll_amount *= config.SCROLL_UP_AMOUNT_BOOST
                    
                    base_interval = config.SCROLL_INTERVAL
                    min_interval = config.SCROLL_MIN_INTERVAL
                    scroll_interval = base_interval - (base_interval - min_interval) * current_velocity
                    
                    if current_direction == "UP":
                        scroll_interval *= config.SCROLL_UP_INTERVAL_MULTIPLIER
                    
                    if current_direction == "UP":
                        pyautogui.scroll(int(scroll_amount))
                    else:
                        pyautogui.scroll(-int(scroll_amount))
                    
                    time.sleep(scroll_interval)
            
            self.scroll_thread = threading.Thread(target=scroll_loop, daemon=True)
            self.scroll_thread.start()
    
    def update_scroll_direction(self, direction, velocity=None):
        """Atualiza direção e velocidade do scroll"""
        with self.scroll_lock:
            if self.scroll_active:
                self.scroll_direction = direction
                if velocity is not None:
                    self.scroll_velocity = max(config.SCROLL_MIN_VELOCITY, min(1.0, velocity))
    
    def stop_infinite_scroll(self):
        """Para o scroll infinito"""
        with self.scroll_lock:
            self.scroll_active = False
        
        if self.scroll_thread and self.scroll_thread.is_alive():
            self.scroll_thread.join(timeout=0.5)
    
    def get_screen_size(self):
        """Retorna tamanho da tela (width, height)"""
        return (self.screen_w, self.screen_h)
    
    def reset(self):
        """Reseta o filtro e estado do cursor"""
        self.cursor_filter.reset()
        self.last_pos = None
        self.stop_infinite_scroll()
    
    def cleanup(self):
        """Libera recursos"""
        self.stop_infinite_scroll()

