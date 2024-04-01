from PySide2 import QtGui, QtCore


def get_clippy_palette():
    """
    Generate an ugly clippy palette, Windows 98 style

    Returns
    -------
    QtGui.QPalette
    """

    palette = QtGui.QPalette()

    # base
    palette.setColor(palette.WindowText, QtCore.Qt.black)
    palette.setColor(palette.Button, QtGui.QColor(235, 235, 184))
    palette.setColor(palette.Light, QtGui.QColor(180, 182, 184))
    palette.setColor(palette.Midlight, QtGui.QColor(89, 90, 91))
    palette.setColor(palette.Dark, QtGui.QColor(32, 35, 37))
    palette.setColor(palette.Text, QtGui.QColor(80, 80, 80))
    palette.setColor(palette.BrightText, QtGui.QColor(180, 180, 180))
    palette.setColor(palette.ButtonText,  QtCore.Qt.black)
    palette.setColor(palette.Base, QtGui.QColor(235, 235, 184))
    palette.setColor(palette.Window, QtGui.QColor(200, 200, 0))
    palette.setColor(palette.Shadow, QtGui.QColor(20, 20, 20))
    palette.setColor(palette.Highlight, QtGui.QColor(0, 110, 215))
    palette.setColor(palette.HighlightedText, QtGui.QColor(240, 240, 240))
    palette.setColor(palette.Link, QtGui.QColor(56, 252, 196))
    palette.setColor(palette.AlternateBase, QtGui.QColor(245, 245, 194))
    palette.setColor(palette.ToolTipBase, QtGui.QColor(51, 53, 55))
    palette.setColor(palette.ToolTipText, QtGui.QColor(180, 180, 180))
    palette.setColor(palette.LinkVisited, QtGui.QColor(80, 80, 80))

    # disabled
    palette.setColor(palette.Disabled, palette.WindowText, QtGui.QColor(127, 127, 127))
    palette.setColor(palette.Disabled, palette.Text, QtGui.QColor(127, 127, 127))
    palette.setColor(palette.Disabled, palette.ButtonText, QtGui.QColor(127, 127, 127))
    palette.setColor(palette.Disabled, palette.Highlight, QtGui.QColor(80, 80, 80))
    palette.setColor(palette.Disabled, palette.HighlightedText, QtGui.QColor(127, 127, 127))

    # all
    palette.setColor(palette.All, palette.Mid, QtGui.QColor(235, 235, 184))

    return palette
