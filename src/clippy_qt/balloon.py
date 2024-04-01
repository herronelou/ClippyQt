from PySide2 import QtCore, QtGui, QtWidgets

from .palette import get_clippy_palette


class Balloon(QtWidgets.QWidget):

    contents_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super(Balloon, self).__init__(parent)

        self._internal_layout = QtWidgets.QVBoxLayout(self)
        self._internal_layout.setContentsMargins(10, 10, 10, 25)
        self.setPalette(get_clippy_palette())

    def _clear_layout(self):
        layout = self._internal_layout
        while layout.count():
            child = layout.takeAt(0)
            print(child)
            widget = child.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def set_widget(self, widget):
        self._clear_layout()
        if widget is not None:
            self._internal_layout.addWidget(widget)
        self.contents_changed.emit()

    def paintEvent(self, _event):
        """ Draw the speech bubble """
        # Use a QPainterPath to draw a rounded speech bubble
        path = QtGui.QPainterPath()

        rect = self.rect()
        # Shrink the rect a bit to take border and speech arrow into account
        rect.adjust(1, 1, -1, -14)

        # Draw the speech bubble
        path.addRoundedRect(rect, 10, 10)
        path.moveTo(rect.width() - 60, rect.height())
        path.lineTo(rect.width() - 60, rect.height() + 15)
        path.lineTo(rect.width() - 70, rect.height())

        # Bake the QPainterPath
        path.setFillRule(QtCore.Qt.WindingFill)
        path = path.simplified()

        painter = QtGui.QPainter(self)
        # Set the fill to FFFFCC
        painter.setBrush(QtGui.QColor(255, 255, 204))
        painter.setPen(QtGui.QColor(0, 0, 0))
        painter.drawPath(path)
        painter.end()
