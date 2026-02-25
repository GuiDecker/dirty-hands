"""
Tests for core components of AutoGesture.
These tests validate the gesture engine, filters, and config modules
without requiring a webcam or display.
"""

import time
from unittest.mock import MagicMock, patch
import pytest
from utils.filters import ExponentialMovingAverage
from utils import config
from gestures.gesture_engine import GestureEngine


class TestExponentialMovingAverage:
    def test_initial_value_passthrough(self):
        ema = ExponentialMovingAverage(alpha=0.3)
        result = ema.update((0.5, 0.5))
        assert result == (0.5, 0.5)

    def test_smoothing_effect(self):
        ema = ExponentialMovingAverage(alpha=0.3)
        ema.update((0.0, 0.0))
        result = ema.update((1.0, 1.0))
        assert result[0] == pytest.approx(0.3, abs=1e-6)
        assert result[1] == pytest.approx(0.3, abs=1e-6)

    def test_convergence(self):
        ema = ExponentialMovingAverage(alpha=0.5)
        ema.update((0.0, 0.0))
        for _ in range(20):
            result = ema.update((1.0, 1.0))
        assert result[0] == pytest.approx(1.0, abs=0.01)
        assert result[1] == pytest.approx(1.0, abs=0.01)

    def test_reset(self):
        ema = ExponentialMovingAverage(alpha=0.3)
        ema.update((0.5, 0.5))
        ema.reset()
        assert ema.value is None
        result = ema.update((0.8, 0.8))
        assert result == (0.8, 0.8)


class TestConfig:
    def test_camera_config_exists(self):
        assert hasattr(config, 'CAMERA_DEVICE_ID')
        assert hasattr(config, 'CAMERA_WIDTH')
        assert hasattr(config, 'CAMERA_HEIGHT')

    def test_gesture_thresholds_exist(self):
        assert hasattr(config, 'PINCH_THRESHOLD')
        assert hasattr(config, 'SWIPE_THRESHOLD')
        assert hasattr(config, 'CLICK_COOLDOWN')

    def test_scroll_config_exists(self):
        assert hasattr(config, 'SCROLL_AMOUNT')
        assert hasattr(config, 'SCROLL_MAX_AMOUNT')
        assert hasattr(config, 'SCROLL_INTERVAL')

    def test_ema_config_values(self):
        assert 0 < config.EMA_ALPHA <= 1
        assert config.DEAD_ZONE >= 0


class TestGestureEngine:
    def _make_landmarks(self, index_x=0.5, index_y=0.5,
                        thumb_x=0.5, thumb_y=0.5,
                        middle_x=0.5, middle_y=0.5,
                        index_pip_y=0.6, middle_pip_y=0.6):
        landmarks = MagicMock()
        lm = {}
        for i in range(21):
            m = MagicMock()
            m.x = 0.5
            m.y = 0.5
            lm[i] = m
        lm[GestureEngine.INDEX_TIP].x = index_x
        lm[GestureEngine.INDEX_TIP].y = index_y
        lm[GestureEngine.THUMB_TIP].x = thumb_x
        lm[GestureEngine.THUMB_TIP].y = thumb_y
        lm[GestureEngine.MIDDLE_TIP].x = middle_x
        lm[GestureEngine.MIDDLE_TIP].y = middle_y
        lm[GestureEngine.INDEX_PIP].y = index_pip_y
        lm[GestureEngine.MIDDLE_PIP].y = middle_pip_y
        landmarks.landmark = lm
        return landmarks

    def test_move_action_always_emitted(self):
        engine = GestureEngine()
        landmarks = self._make_landmarks(index_x=0.3, index_y=0.4,
                                         thumb_x=0.8, thumb_y=0.8)
        actions = engine.update(landmarks)
        move_actions = [a for a in actions if a[0] == "MOVE"]
        assert len(move_actions) == 1
        assert move_actions[0] == ("MOVE", 0.3, 0.4)

    def test_pinch_click(self):
        engine = GestureEngine()
        landmarks = self._make_landmarks(
            index_x=0.5, index_y=0.5,
            thumb_x=0.5, thumb_y=0.5,
            middle_x=0.5, middle_y=0.6,
            index_pip_y=0.6, middle_pip_y=0.55
        )
        actions = engine.update(landmarks)
        click_actions = [a for a in actions if a[0] == "CLICK"]
        assert len(click_actions) == 1

    def test_click_cooldown(self):
        engine = GestureEngine()
        landmarks = self._make_landmarks(
            index_x=0.5, index_y=0.5,
            thumb_x=0.5, thumb_y=0.5,
        )
        actions1 = engine.update(landmarks)
        clicks1 = [a for a in actions1 if a[0] == "CLICK"]
        assert len(clicks1) == 1

        actions2 = engine.update(landmarks)
        clicks2 = [a for a in actions2 if a[0] == "CLICK"]
        assert len(clicks2) == 0

    def test_reset_clears_state(self):
        engine = GestureEngine()
        landmarks = self._make_landmarks()
        engine.update(landmarks)
        engine.reset()
        assert len(engine.history) == 0
        assert engine.last_click == 0
        assert engine.scroll_active is False
