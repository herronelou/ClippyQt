from PySide2 import QtCore, QtGui, QtWidgets


from clippy_qt.agent import Agent
from clippy_qt.agents import Clippy
from clippy_qt.balloon import Balloon


class ClippyEngine(QtWidgets.QDialog):
    def __init__(self, agent=None, parent=None):
        super(ClippyEngine, self).__init__(parent)

        if agent is None:
            agent = Clippy()
        elif not isinstance(agent, Agent):
            raise TypeError('agent must be an instance of Agent, not {}'.format(type(agent).__name__))

        self.agent = agent
        self.balloon = Balloon(parent=self)

        # Mouse tracking for dragging the dialog
        self._mouse_pressed = False
        self._old_pos = None
        self._old_rect = None

        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlag(QtCore.Qt.WindowDoesNotAcceptFocus)
        # self.setWindowFlag(QtCore.Qt.WindowTransparentForInput)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(self.balloon)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.agent)
        layout.addLayout(bottom_layout)

        # Agent should never change size, balloon should be only as big as it needs
        self.agent.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.balloon.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        # Connect signals
        self.balloon.contents_changed.connect(self.adjustSize)

    # Allow moving the dialog by clicking and dragging the agent
    def mousePressEvent(self, event):
        print('mousePressEvent')
        self._old_pos = event.globalPos()
        self._old_rect = self.frameGeometry()
        self._mouse_pressed = True
        event.accept()

    def mouseMoveEvent(self, event):
        if not self._mouse_pressed:
            event.ignore()
            return
        delta = QtCore.QPoint(event.globalPos() - self._old_pos)
        self.move(self._old_rect.topLeft() + delta)

    def mouseReleaseEvent(self, event):
        if not self._mouse_pressed:
            event.ignore()
        self._mouse_pressed = False
        if self._old_pos is not None:
            self.agent.look_at(self._old_pos)
        self._old_pos = None
        self._old_rect = None

    def resizeEvent(self, event):
        old_size = event.oldSize()
        new_size = event.size()
        # Move the widget to keep the bottom right corner in the same place
        offset = QtCore.QPoint(old_size.width() - new_size.width(), old_size.height() - new_size.height())
        self.move(self.pos() + offset)

    def set_widget(self, widget):
        self.balloon.set_widget(widget)
        if widget is None:
            self.balloon.hide()
        elif not self.balloon.isVisible():
            self.balloon.show()

    def show(self):
        """ Show the agent then after its greeting, show the balloon """
        self.balloon.hide()
        super(ClippyEngine, self).show()
        self.agent.play('Greeting', callback=self.balloon.show)

    def hide(self):
        self.agent.play('GoodBye', callback=super(ClippyEngine, self).hide)


if __name__ == '__main__':

    engine = ClippyEngine()

    bubble_layout = QtWidgets.QVBoxLayout(engine.balloon)
    bubble_layout.addWidget(QtWidgets.QLabel('Hello, World!'))
    bubble_layout.addStretch()
    bubble_layout.addWidget(QtWidgets.QCheckBox('Check me!'))
    bubble_layout.addWidget(QtWidgets.QTextEdit('Edit Me!'))
    bubble_layout.addWidget(QtWidgets.QPushButton('Close'))
    bubble_widget = QtWidgets.QWidget()
    engine.set_widget(bubble_widget)

    engine.show()

"""
other_widget = QtWidgets.QDateTimeEdit()
engine.set_widget(other_widget)
"""

