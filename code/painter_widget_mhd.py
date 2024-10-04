import math

from PySide6.QtWidgets import (
    QWidget,
    QMainWindow,
    QApplication,
    QFileDialog,
    QStyle,
    QColorDialog,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QTabWidget,
    QLabel,
    QCheckBox,
    QRadioButton,
    QGroupBox,
)
from PySide6.QtCore import Qt, Slot, QStandardPaths, Signal, QObject, QPoint, QSize

from PySide6.QtGui import (
    QMouseEvent,
    QPaintEvent,
    QPen,
    QAction,
    QPainter,
    QColor,
    QPixmap,
    QImage,
    QIcon,
    QKeySequence,
	QImage,
	QPixmap,
)
import sys
import cv2
import numpy as np

import globals

import fast_computation

from copy import deepcopy

class painter_widget_mhd(QWidget):
    """A widget where user can draw with their mouse
    The user draws on a QPixmap which is itself paint from paintEvent()
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumWidth(globals.CANVAS_WIDTH)
        self.setMinimumHeight(globals.CANVAS_HEIGHT)

        self.image_size = QSize(self.height(), self.width())

        self.image = np.zeros((self.height(), self.width(), 3), dtype=np.uint8)
        self.image[:, :, 2] = 255

        self.image_mhd = np.zeros((self.height(), self.width(), 3), dtype=np.uint8)

        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.blue)

        self.positions = []
        self.colors = []

        self.show_positions_value = True
        self.compute_mhd_value = False

        self. mhd_parameters_values = globals.MHD_PARAMETERS

    def set_size(self, width, height):
        margins = self.contentsMargins()
        margin_width = margins.left() + margins.right()
        margin_height = margins.top() + margins.bottom()
        self.setFixedSize(width + margin_width, height + margin_height)

    def set_image_size(self,image_size):
        self.image_size = image_size
        self.image = np.zeros((self.image_size.height(), self.image_size.width(), 3), dtype=np.uint8)
        self.image[:, :, 2] = 255
        self.image_mhd = np.zeros((self.image_size.height(), self.image_size.width(), 3), dtype=np.uint8)
        self.convert_cv_mat_to_qt_pixmap(self.image, self.pixmap)
        self.update()

    def set_values(self,positions, colors, image):
        self.positions = positions
        self.colors = colors
        self.image = deepcopy(image)

    def set_compute_mhd_value(self, value):
        self.compute_mhd_value = value
        if value == False:
            self.compute_mhd()
        self.update()

    def get_image_mhd(self):
        return self.image_mhd.copy()

    def resizeEvent(self, event):
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.blue)
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
                painter.setPen(QColor("white"))  # Color del borde
                painter.setBrush(QColor("white"))  # Color de relleno
                painter.drawEllipse(QPoint(self.positions[pos][1], self.positions[pos][0]), 10, 10)
                painter.setPen(QColor("black"))  # Color del borde
                painter.setBrush(QColor("black"))  # Color de relleno
                painter.drawEllipse(QPoint(self.positions[pos][1], self.positions[pos][0]), 8, 8)
                painter.setPen(QColor(self.colors[pos][0], self.colors[pos][1], self.colors[pos][2]))  # Color del borde
                painter.setBrush(QColor(self.colors[pos][0], self.colors[pos][1], self.colors[pos][2]))  # Color de relleno
                painter.drawEllipse(QPoint(self.positions[pos][1], self.positions[pos][0]), 6, 6)

    def compute_mhd(self):
        if self.compute_mhd_value == True:
            positions = np.array(self.positions)
            colors = np.array(self.colors)
            del self.image_mhd
            self.image_mhd = fast_computation.compute_mhd(positions, colors, self.image, self.mhd_parameters_values)
        else:
            del self.image_mhd
            self.image_mhd = np.zeros((self.height(), self.width(), 3), dtype=np.uint8)
            self.image_mhd[:, :, 2] = 255

        self.convert_cv_mat_to_qt_pixmap(self.image_mhd, self.pixmap)
        self.update()

    def convert_cv_mat_to_qt_pixmap(self, image, pixmap):
        """Convertir de una imagen de OpenCV a QPixmap"""
        pixmap.convertFromImage(QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format.Format_RGB888))

    @Slot()
    def set_show_positions(self, state):
        self.show_positions_value = state
        self.update()

    def set_mhd_parameters(self, mhd_parameters):
        self.mhd_parameters_values = mhd_parameters
        self.update()


    def get_pixmap(self):
        return self.pixmap