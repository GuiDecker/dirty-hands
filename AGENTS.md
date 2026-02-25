# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

AutoGesture ("Dirty Hands") is a single-process Python desktop application that uses a webcam + MediaPipe to detect hand gestures and translate them into OS-level mouse/keyboard actions via PyAutoGUI. See `README.md` for full architecture and gesture docs.

### Environment requirements

- **Python 3.10+** with a virtual environment at `venv/`.
- **Virtual display**: The app requires a display (OpenCV `imshow` + PyAutoGUI). In headless environments, start Xvfb first: `Xvfb :99 -screen 0 1280x1024x24 &` and `export DISPLAY=:99`.
- **System packages**: `python3-tk`, `xdotool` are needed for PyAutoGUI on Linux.
- **MediaPipe version**: `requirements.txt` pins `mediapipe==0.10.8`, which is unavailable for Python 3.12+. Use `mediapipe==0.10.13` (still < 0.10.14, so `mp.solutions.hands` API works). The `hand_tracker.py` has try/except for both old and new APIs.

### Running the application

```bash
source venv/bin/activate
export DISPLAY=:99  # if headless
python main.py
```

The app will exit gracefully with `"Erro: Não foi possível abrir a câmera"` when no webcam is available.

### Testing

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

No test framework was originally configured. Tests exist at `tests/test_core.py` for the EMA filter, config, and gesture engine.

### Linting

```bash
source venv/bin/activate
python -m flake8 --max-line-length=120 --exclude=venv main.py vision/ gestures/ actions/ input/ utils/
```

Pre-existing whitespace warnings (W293/W391) are present in the codebase. No actual errors (E-class).

### Key caveats

- **No webcam in cloud VMs**: The app's core loop requires `cv2.VideoCapture(0)` which needs a real or virtual camera device. Without it, `main.py` exits immediately. Testing the full gesture pipeline end-to-end requires a webcam.
- **PyAutoGUI FAILSAFE**: The app sets `pyautogui.FAILSAFE = False`, so moving the mouse to corners won't trigger the failsafe exception.
- All code and UI strings are in Portuguese (pt-BR).
