"""
Action Dispatcher - Traduz ações abstratas em comandos reais
"""

from input.os_controller import OSController


class ActionDispatcher:
    """Recebe ações abstratas e as converte em comandos reais"""
    
    def __init__(self):
        self.os = OSController()
    
    def dispatch(self, actions):
        """Processa lista de ações e executa no SO"""
        for action in actions:
            action_type = action[0]
            
            try:
                if action_type == "MOVE":
                    self.os.move_cursor(action[1], action[2])
                elif action_type == "CLICK":
                    self.os.click()
                elif action_type == "SWIPE_RIGHT":
                    self.os.next_page()
                elif action_type == "SWIPE_LEFT":
                    self.os.prev_page()
                elif action_type == "START_SCROLL":
                    direction = action[1] if len(action) > 1 else "DOWN"
                    velocity = action[2] if len(action) > 2 else None
                    self.os.start_infinite_scroll(direction, velocity)
                elif action_type == "UPDATE_SCROLL":
                    direction = action[1] if len(action) > 1 else "DOWN"
                    velocity = action[2] if len(action) > 2 else None
                    self.os.update_scroll_direction(direction, velocity)
                elif action_type == "STOP_SCROLL":
                    self.os.stop_infinite_scroll()
            except Exception as e:
                print(f"Erro ao executar ação {action_type}: {e}")
    
    def cleanup(self):
        """Libera recursos"""
        if hasattr(self.os, 'cleanup'):
            self.os.cleanup()

