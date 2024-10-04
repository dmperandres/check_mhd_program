import math
import random

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

contador = 0


class painter_widget(QWidget):
    """A widget where user can draw with their mouse
    The user draws on a QPixmap which is itself paint from paintEvent()
    """
    my_released = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumWidth(globals.CANVAS_WIDTH)
        self.setMinimumHeight(globals.CANVAS_HEIGHT)

        self.image_rgb_size = QSize(self.height(), self.width())

        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.white)
        self.image_rgb = np.full((self.height(), self.width(), 3), 255, dtype=np.uint8)
        self.image_processed = np.full((self.height(), self.width(), 3), 255, dtype=np.uint8)

        self.previous_pos = None

        self.start_position = None
        self.end_position = None

        self.painter = QPainter()
        self.pen = QPen()
        self.pen.setWidth(globals.BRUSH_SIZE_DEFAULT)
        self.pen.setCapStyle(Qt.RoundCap)
        self.pen.setJoinStyle(Qt.RoundJoin)

        self.mode = globals.MODE_NONE
        self.positions = []
        self.colors = []
        self.show_positions_value = True

        self.brush_size = globals.BRUSH_SIZE_DEFAULT
        self.mhd_parameters_values = globals.MHD_PARAMETERS

        self.color_model_smooth = 1

        self.color_model = 'RGB'
        self.color_model_changed = False

        # self.kmeans_computed = True
        self.compute_kmeans_value = False
        self.kmeans_num_clusters_value = globals.KMEANS_NUM_CLUSTERS
        self.kmeans_num_iteractions_value = globals.KMEANS_NUM_ITERACTIONS

        # connectios
        self.connections = []

        self.setFocusPolicy(Qt.StrongFocus)


    def set_size(self, width, height):
        margins = self.contentsMargins()
        size = self.geometry()
        rect = self.contentsRect()
        margin_width = margins.left() + margins.right()
        margin_height = margins.top() + margins.bottom()
        self.setFixedSize(width + margin_width,height + margin_height)

    def set_image_size(self,image_size):
        self.image_rgb_size = image_size

    def reset_pixmap(self):
        self.pixmap = QPixmap(self.image_rgb_size)
        self.pixmap.fill(Qt.white)

    def set_image(self, image):
        self.image_rgb = image.copy()

    def get_values(self):
        # self.update_colors()
        return self.positions, self.colors, self.image_processed

    def resizeEvent(self, event):
        self.image_rgb = np.full((self.size().height(), self.size().width(), 3), 255, dtype=np.uint8)
        self.convert_cv_mat_to_qt_pixmap(self.image_rgb, self.pixmap)

    def set_color_smooth(self, index):
        if globals.COLOR_SMOOTH_KERNEL_SIZE[index] != self.color_model_smooth:
            self.color_model_smooth = globals.COLOR_SMOOTH_KERNEL_SIZE[index]

    def set_color_model(self, index):
        if globals.COLOR_MODELS[index] != self.color_model:
            self.color_model = globals.COLOR_MODELS[index]

    def set_compute_kmeans(self, value):
        self.compute_kmeans_value = value

    def set_kmeans_num_clusters_value(self, value):
        self.kmeans_num_clusters_value = value

    def process_image(self):
        self.image_processed = self.image_rgb.copy()

        if self.color_model_smooth>1:
            self.image_processed = cv2.blur(self.image_processed, (self.color_model_smooth, self.color_model_smooth))

        if self.color_model == 'HSV':
            self.image_processed = cv2.cvtColor(self.image_processed, cv2.COLOR_RGB2HSV)
        elif self.color_model == 'HLS':
            self.image_processed = cv2.cvtColor(self.image_processed, cv2.COLOR_RGB2HLS)
            self.image_processed[:, :, 2] = 255
            for x in range(self.image_processed.shape[1]):
                for y in range(self.image_processed.shape[0]):
                    if self.image_processed[y, x, 1] < 10:
                        self.image_processed[y, x, 1] = 0
                    elif self.image_processed[y, x, 1] > 240:
                        self.image_processed[y, x, 1] = 255
                    else:
                        self.image_processed[y, x, 1] = 128

            self.image_processed = cv2.cvtColor(self.image_processed, cv2.COLOR_HLS2RGB)
        # k-means
        if self.compute_kmeans_value == True:
            self.image_processed = self.k_means(self.image_processed, self.kmeans_num_clusters_value, self.kmeans_num_iteractions_value)

        self.convert_cv_mat_to_qt_pixmap(self.image_processed, self.pixmap)
        self.update_colors()
        self.update()


    def paint(self, painter):
        # Dibuja un círculo
        if self.show_positions_value:
            for pos in range(len(self.positions)):
                painter.setPen(QColor("white"))  # Color del borde
                painter.setBrush(QColor("white"))  # Color de relleno
                painter.drawEllipse(QPoint(self.positions[pos][1], self.positions[pos][0]), 10, 10)
                painter.setPen(QColor("black"))  # Color del borde
                painter.setBrush(QColor("black"))  # Color de relleno
                painter.drawEllipse(QPoint(self.positions[pos][1],self.positions[pos][0]), 8, 8)
                painter.setPen(QColor(self.colors[pos][0],self.colors[pos][1], self.colors[pos][2]))  # Color del borde
                painter.setBrush(QColor(self.colors[pos][0],self.colors[pos][1], self.colors[pos][2]))  # Color de relleno
                painter.drawEllipse(QPoint(self.positions[pos][1],self.positions[pos][0]), 6, 6)

        pen1 = QPen(QColor('black'), 1)
        painter.setPen(pen1)
        if  self.start_position != None and self.end_position != None:
            painter.drawLine(self.start_position,self.end_position)

        for connection in self.connections:
            painter.drawLine(connection[0], connection[1])


    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        painter.drawPixmap(0, 0, self.pixmap)
        self.paint(painter)

    def mousePressEvent(self, event: QMouseEvent):
        """Override from QWidget
        Called when user clicks on the mouse
        """
        if self.mode == globals.MODE_MINIMUM and event.buttons():
            self.end_position = event.position().toPoint()

        self.previous_pos = event.position().toPoint()
        QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Override method from QWidget
        Called when user moves and clicks on the mouse
        """
        if self.mode == globals.MODE_DRAW:
            if event.buttons() & Qt.MouseButton.LeftButton:
                current_pos = event.position().toPoint()
                cv2.circle(self.image_rgb, (current_pos.x(), current_pos.y()), int(self.brush_size/2), self.brush_color, -1)
                self.convert_cv_mat_to_qt_pixmap(self.image_rgb, self.pixmap)
        elif self.mode == globals.MODE_MINIMUM and event.buttons():
                self.end_position = event.position().toPoint()
                self.compute_mhd()

        QWidget.mouseMoveEvent(self, event)
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Override method from QWidget
        Called when user releases the mouse
        """
        if self.mode == globals.MODE_ADD_POSITIONS:
            if event.button() == Qt.MouseButton.LeftButton:
                # save as y , x for numpy
                self.positions.append([event.position().toPoint().y(),event.position().toPoint().x()])
        elif self.mode == globals.MODE_REMOVE_POSITIONS:
            self.remove_position([event.position().toPoint().y(),event.position().toPoint().x()])
        elif self.mode == globals.MODE_MINIMUM:
            self.start_position = None

        self.previous_pos = None
        self.process_image()
        self.my_released.emit()

    def keyReleaseEvent(self, event):
        if self.mode == globals.MODE_MINIMUM:
            if event.key() == Qt.Key.Key_F1:
                # add
                self.connections.append((self.start_position, self.end_position))
            elif event.key() == Qt.Key.Key_F2:
                # clear
                self.connections.clear()
                self.update()


    def distance(self, position1, position2):
        return math.sqrt((position2[0] - position1[0])**2 + (position2[1] - position1[1])**2)

    def remove_position(self, position):
        positions = []
        for pos in range(len(self.positions)):
            if self.distance(self.positions[pos], position) < 10:
                positions.append(pos)

        if len(positions)>0:
            del self.positions[positions[0]]


    # def convert_qt_pixmap_to_cv_mat(self, pixmap):
    #     print("pix to map")
    #     qt_image = pixmap.toImage()
    #     qt_image = qt_image.convertToFormat(QImage.Format.Format_RGB888)
    #     # version que falla
    #     # np_array = np.array(self.qt_image.constBits(), copy=False).reshape(self.qt_image.height(), self.qt_image.width(), 3)
    #     # version correcta
    #     # https://gallois.cc/blog/qimage/
    #     np_array = np.ndarray((qt_image.height(), qt_image.width(), 3), buffer=qt_image.constBits(),strides=[qt_image.bytesPerLine(), 3, 1], dtype=np.uint8)
    #     return np_array

    def convert_qt_pixmap_to_cv_mat(self, pixmap, image):
        qt_image = pixmap.toImage().convertToFormat(QImage.Format_RGB888)
        del image
        image = np.ndarray((qt_image.height(), qt_image.width(), 3), buffer=qt_image.constBits(),
                           strides=[qt_image.bytesPerLine(), 3, 1], dtype=np.uint8)

    def convert_cv_mat_to_qt_pixmap(self, image, pixmap):
        """Convertir de una imagen de OpenCV a QPixmap"""
        pixmap.convertFromImage(QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format.Format_RGB888))

    def get_color(self,position):
        qt_image = self.pixmap.toImage()
        color = qt_image.pixelColor(position)
        return [color.red(), color.green(), color.blue(), 255]

    def get_pixmap(self):
        pixmap_result = QPixmap(self.pixmap)
        painter = QPainter(pixmap_result)
        painter.setRenderHint(QPainter.Antialiasing, False)
        # painter.drawPixmap(0, 0, self.pixmap)
        self.paint(painter)
        return pixmap_result

    def clear(self):
        """ Clear the pixmap """
        self.pixmap.fill(Qt.white)
        self.positions.clear()
        self.colors.clear()
        self.update()

    def set_mode_value(self,mode):
        self.mode = mode
        self.update()

    def set_mhd_parameters(self,mhd_parameters):
        self.mhd_parameters_values = mhd_parameters

    @Slot()
    def set_show_positions(self, state):
        self.show_positions_value = state
        self.update()

    def set_brush_size(self, size):
        self.brush_size = size

    def set_brush_color(self, color):
        self.brush_color = color

    def compute_mhd(self):
        if len(self.positions)>0:
            positions = np.array(self.positions)
            colors = np.array(self.colors)
            pos_min = fast_computation.compute_mhd_one_position(positions, colors, self.image_rgb, self.mhd_parameters_values, self.end_position.x(), self.end_position.y())
            self.start_position =  QPoint(self.positions[pos_min][1], self.positions[pos_min][0])

    def update_colors(self):
        self.colors = []
        for pos in range(len(self.positions)):
            color = self.image_processed[self.positions[pos][0], self.positions[pos][1]]
            self.colors.append(color)


    def k_means(self, image, num_clusters, num_iteractions):
        Z = image.reshape((-1, 3))
        # # convert to np.float32
        Z = np.float32(Z)
        # define criteria, number of clusters(K) and apply kmeans()
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, num_iteractions, 1.0)
        ret, label, center = cv2.kmeans(Z, num_clusters, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        # Now convert back into uint8, and make original image
        center = np.uint8(center)
        result = center[label.flatten()]
        result2 = result.reshape(image.shape)
        return result2


    def paint_positions(self):
        # Crear un QPixmap del tamaño de la imagen original
        result_image = QPixmap(self.pixmap.size())
        result_image.fill(Qt.transparent)  # Llenar con transparencia

        # Crear un QPainter para dibujar en el QPixmap
        painter = QPainter(result_image)
        painter.setRenderHint(QPainter.Antialiasing, False)
        painter.drawPixmap(0, 0, self.pixmap)
        self.paint(painter)

        painter.end()

        return result_image