import os
import math
from collections import deque

from PySide2 import QtCore, QtGui, QtWidgets, QtMultimedia
import random
import json


class Agent(QtWidgets.QWidget):

    started = QtCore.Signal()
    stopped = QtCore.Signal()

    def __init__(self, config, sprite, sounds, parent=None):
        super(Agent, self).__init__(parent)

        # public properties
        self.play_sounds = True

        # Animation resources
        with open(config, 'r') as f:
            self._config = json.load(f)
        self._sprite = sprite
        self._sounds = {}

        self._stopping = False

        # Animation and callback queue:
        self._queue = deque()
        self._current_callback = None

        # Tile properties
        self._frames = []
        self._tile_width = self._config['framesize'][0]
        self._tile_height = self._config['framesize'][1]

        # Animation state
        self._current_animation = None
        self._current_frame = 0
        self._frame_rate = 1000 / 24
        self._playing = False
        self._looping = False

        self._timer = QtCore.QTimer(self)
        self._idle_timer = QtCore.QTimer(self)

        self._load_frames()
        self._preload_sounds(sounds)
        self.init_ui()

    def init_ui(self):
        """ Initialize the widget """
        self._timer.timeout.connect(self._next_frame)
        self._timer.setSingleShot(True)

        self._idle_timer.timeout.connect(self.play_random_idle)
        self._idle_timer.setSingleShot(True)

    def animations(self):
        """ Return a list of available animations. """
        return self._config['animations'].keys()

    def play(self, animation, right_now=False, callback=None):
        """
        Play an animation, optionally with a callback when the animation is done.

        Parameters
        ----------
        animation : str
            Name of the animation to play
        right_now : bool
            If True, play the animation immediately, discarding the current animation and the queue.
            If False, add the animation to the queue.
        callback : callable
            Function to call when the animation is done. Use a lambda or partial if it needs arguments.
        """
        self.activate()
        if right_now:
            self.stop(right_now=True)
        if not self._playing:
            self._play(animation, callback)
        else:
            self._queue.append((animation, callback))

    def play_random_idle(self):
        """ Play a random idle animation. """
        idle_animations = [name for name in self._config['animations'] if name.startswith('Idle')]
        anim = random.choice(idle_animations)
        print('Playing idle:', anim)
        self.play(anim)

    def gesture_at(self, position):
        """
        Gesture towards a position on the screen

        Parameters
        ----------
        position : QtCore.QPoint
        """
        self.activate()
        direction = self._get_direction(position, granular=False)
        gesture = 'Gesture{}'.format(direction)
        self.play(gesture)

    def look_at(self, position):
        """
        Look towards a position on the screen

        Parameters
        ----------
        position : QtCore.QPoint
        """
        self.activate()
        direction = self._get_direction(position)
        look = 'Look{}'.format(direction)
        self.play(look)

    def activate(self):
        """
        Get out of idle mode.
        """
        self._idle_timer.stop()
        if self._playing:
            self._stopping = True

    def _next_frame(self):
        """ Advance to the next frame in the current animation. """
        if self._current_animation is None:
            return

        current_frame = self._current_animation['frames'][self._current_frame]

        if self._stopping and current_frame.get('exitBranch', False):
            self._stopping = False
            next_frame = current_frame['exitBranch']
        elif current_frame.get('branching', False):
            # Pick a random branch based on the weights of each possible branch
            random_roll = random.randint(0, 99)
            for branch in current_frame['branching']['branches']:
                if random_roll < branch['weight']:
                    next_frame = branch['frameIndex']
                    break
                random_roll -= branch['weight']
            else:
                next_frame = self._current_frame + 1
        else:
            next_frame = self._current_frame + 1

        if next_frame >= len(self._current_animation['frames']):
            if self._looping:
                self._current_frame = 0
            else:
                self._stop()
                return
        else:
            self._current_frame = next_frame

        self._queue_next_frame()
        self._play_sound()
        self.update()

    def stop(self, right_now=False):
        """ stop the current animation and clear the queue."""
        self._queue.clear()

        if not right_now and self._playing:
            self._stopping = True
            return
        if right_now:
            self._current_callback = None  # Cancel the current callback
        self._stop()

    def _stop(self):
        """ Fully stop the animation and emit the stopped signal. """
        self._playing = False
        self._stopping = False
        self._current_animation = None
        self._current_frame = 0
        self.update()
        self.stopped.emit()
        if self._current_callback:
            self._current_callback()
            self._current_callback = None
        if self.isVisible():
            self._idle_timer.start(random.randint(5000, 15000))
        if self._queue:
            self._play_next_in_queue()

    def _play(self, animation, callback=None):
        """ Play an animation and call the callback when done. """
        self._current_animation = self._config['animations'][animation]
        self._current_callback = callback
        self._current_frame = 0
        self._playing = True
        self.started.emit()
        self._queue_next_frame()
        self.update()

    def _play_next_in_queue(self):
        """ Play the next animation in the queue. """
        animation, callback = self._queue.popleft()
        self._play(animation, callback=callback)

    def _queue_next_frame(self):
        """ Queue the next frame in the animation. """
        self._timer.start(self._current_animation['frames'][self._current_frame]['duration'])

    def _load_frames(self):
        """ Load the frames from the sprite sheet. """
        self._frames = []
        pixmap = QtGui.QPixmap(self._sprite)
        columns = pixmap.width() // self._tile_width
        rows = pixmap.height() // self._tile_height
        for i in range(rows):
            for j in range(columns):
                frame = pixmap.copy(j * self._tile_width, i * self._tile_height, self._tile_width, self._tile_height)
                self._frames.append(frame)

    def _preload_sounds(self, sounds):
        """ Preload the sounds. """
        if not sounds:
            self.play_sounds = False
            return
        for wav_file in os.listdir(sounds):
            sound_name, ext = os.path.splitext(wav_file)
            if ext != '.wav':
                continue
            print('Loading sound:', sound_name, wav_file)
            self._sounds[sound_name] = QtMultimedia.QSound(os.path.join(sounds, wav_file))

    def _play_sound(self):
        """ Play a sound if the current frame has one. """
        if not self.play_sounds:
            return
        if 'sound' in self._current_animation['frames'][self._current_frame]:
            sound_name = self._current_animation['frames'][self._current_frame]['sound']
            self._sounds[sound_name].play()

    def _get_direction(self, position, granular=True):
        """ Get a direction based on a position on the screen. """
        print('position:', position, self.mapToGlobal(self.rect().center()))
        direction = position - self.mapToGlobal(self.rect().center())
        print('direction:', direction)
        angle = (180 * math.atan2(direction.y(), direction.x())) / math.pi
        print('angle:', angle)
        if granular:
            if -22.5 < angle <= 22.5:
                return 'Left'
            elif 22.5 < angle <= 67.5:
                return 'DownLeft'
            elif 67.5 < angle <= 112.5:
                return 'Down'
            elif 112.5 < angle <= 157.5:
                return 'DownRight'
            elif 157.5 < angle <= 180 or -180 <= angle <= -157.5:
                return 'Right'
            elif -157.5 < angle <= -112.5:
                return 'UpRight'
            elif -112.5 < angle <= -67.5:
                return 'Up'
            elif -67.5 < angle <= -22.5:
                return 'UpLeft'
        else:
            if -45 < angle <= 45:
                return 'Left'
            elif 45 < angle <= 135:
                return 'Down'
            elif 135 < angle <= 180 or -180 <= angle <= -135:
                return 'Right'
            elif -135 < angle <= -45:
                return 'Up'

    def paintEvent(self, _event):
        """ Draw the current frame."""

        painter = QtGui.QPainter(self)
        if not self._current_animation:
            target_frame = 0
        else:
            target_frame = self._current_animation['frames'][self._current_frame]['spriteIndex']
        painter.drawPixmap(0, 0, self._frames[target_frame])
        painter.end()

    def sizeHint(self):
        """ Return the size hint for the widget. """
        return QtCore.QSize(self._tile_width, self._tile_height)
