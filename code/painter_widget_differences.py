from PySide6.QtWidgets import (
    QWidget,
)
from PySide6.QtCore import Qt, Slot, QPoint, QSize

from PySide6.QtGui import (
    QPaintEvent,
    QPainter,
    QColor,
    QImage,
    QPixmap,
)
import sys
import numpy as np

import globals

import fast_computation

from copy import deepcopy

class painter_widget_differences(QWidget):
    """A widget where user can draw with their mouse
    The user draws on a QPixmap which is itself paint from paintEvent()
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumWidth(globals.CANVAS_WIDTH)
        self.setMinimumHeight(globals.CANVAS_HEIGHT)

        self.image_size = QSize(self.height(), self.width())

        self.image_original = np.zeros((self.height(), self.width(), 3), dtype=np.uint8)
        self.image_mhd = np.zeros((self.height(), self.width(), 3), dtype=np.uint8)

        self.pixmap = QPixmap(self.image_size)
        self.pixmap.fill(Qt.white)

        self.positions = []
        self.colors = []

        self.mode = globals.MODE_NONE
        # self.compute_mhd_value = False
        self.show_positions_value = False
        self.compute_differences_value = False

    def set_size(self, width, height):
        margins = self.contentsMargins()
        margin_width = margins.left() + margins.right()
        margin_height = margins.top() + margins.bottom()
        self.setFixedSize(width + margin_width, height + margin_height)

    def set_image_size(self, image_size):
        self.image_size = image_size
        self.image_original = np.full((self.image_size.height(), self.image_size.width(), 3), 255, dtype=np.uint8)
        self.image_mhd = np.full((self.image_size.height(), self.image_size.width(), 3), 255, dtype=np.uint8)
        self.convert_cv_mat_to_qt_pixmap(self.image_original, self.pixmap)
        self.update()

    def reset_pixmap(self):
        self.pixmap = QPixmap(self.image_size)
        self.pixmap.fill(Qt.white)

    def resizeEvent(self, event):
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.white)
        self.update()

    def set_compute_differences_value(self, value):
        self.compute_differences_value = value
        if value == False:
            self.reset_pixmap()
        self.update()

    def paintEvent(self, event: QPaintEvent):
        """Override method from QWidget
        Paint the Pixmap into the widget
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        painter.drawPixmap(0, 0, self.pixmap)

        # Dibuja un círculo
        if self.show_positions_value:
            for pos in range(len(self.positions)):
                painter.setPen(QColor("black"))  # Color del borde
                painter.setBrush(QColor("black"))  # Color de relleno
                painter.drawEllipse(QPoint(self.positions[pos][1], self.positions[pos][0]), 12, 12)
                painter.setPen(QColor(self.colors[pos][0], self.colors[pos][1], self.colors[pos][2]))  # Color del borde
                painter.setBrush(
                    QColor(self.colors[pos][0], self.colors[pos][1], self.colors[pos][2]))  # Color de relleno
                painter.drawEllipse(QPoint(self.positions[pos][1], self.positions[pos][0]), 8, 8)

    def set_values(self, positions, colors, image_original, image_mhd, threshold):
        self.positions = positions
        self.colors = colors
        self.image_original = deepcopy(image_original)
        self.image_mhd = deepcopy(image_mhd)
        self.threshold = threshold

    def compute_differences(self):
        if self.compute_differences_value == True:
            result, percentage = fast_computation.compute_differences(self.image_original, self.image_mhd, self.threshold)
            self.convert_cv_mat_to_qt_pixmap(result, self.pixmap)
        else:
            percentage = 100
            self.reset_pixmap()

        self.update()
        return percentage

    def convert_cv_mat_to_qt_pixmap(self, image, pixmap):
        """Convertir de una imagen de OpenCV a QPixmap"""
        pixmap.convertFromImage(QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format.Format_RGB888))

    def get_differences_pixmap(self):
        return self.pixmap

    @Slot()
    def set_show_positions(self, state):
        self.show_positions_value = state
        self.update()

    def get_pixmap(self):
        return self.pixmap