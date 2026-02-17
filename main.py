"""
AutoGesture - Main Entry Point
"""

import cv2
import time
from vision.hand_tracker import HandTracker
from gestures.gesture_engine import GestureEngine
from actions.dispatcher import ActionDispatcher
from utils import config


def main():
    """Função principal"""
    print("🚀 Iniciando AutoGesture...")
    
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()
    engine = GestureEngine()
    dispatcher = ActionDispatcher()
    
    if not cap.isOpened():
        print("❌ Erro: Não foi possível abrir a câmera")
        return
    
    print("✅ Câmera iniciada")
    print("📋 Gestos disponíveis:")
    print("   - Movimento: Mova o dedo indicador")
    print("   - Clique: Pinça (polegar + indicador)")
    print("   - Swipe: Movimento horizontal rápido")
    print("   - Scroll Infinito: Estenda indicador + médio juntos")
    print("\n⚠️  Pressione ESC para sair")
    print("⚠️  Sistema pausa automaticamente se nenhuma mão for detectada\n")
    
    last_hand_detected = time.time()
    is_paused = False
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            hand = tracker.process(frame)
            
            if hand:
                last_hand_detected = time.time()
                if is_paused:
                    is_paused = False
                    print("▶️  Controle retomado")
                
                actions = engine.update(hand)
                dispatcher.dispatch(actions)
            else:
                time_since_last_hand = time.time() - last_hand_detected
                
                if time_since_last_hand > config.NO_HAND_TIMEOUT and not is_paused:
                    is_paused = True
                    print("⏸️  Controle pausado (nenhuma mão detectada)")
                    engine.reset()
                    if hasattr(dispatcher, 'os') and hasattr(dispatcher.os, 'reset'):
                        dispatcher.os.reset()
            
            cv2.imshow("Gesture Control", frame)
            
            if cv2.waitKey(1) & 0xFF == 27:
                break
    
    except KeyboardInterrupt:
        print("\n⚠️  Interrompido pelo usuário")
    
    finally:
        cap.release()
        tracker.cleanup()
        dispatcher.cleanup()
        cv2.destroyAllWindows()
        print("✅ Sistema parado")


if __name__ == "__main__":
    main()
