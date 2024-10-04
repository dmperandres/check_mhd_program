import math
import os

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
    QSlider,
    QSpinBox,
    QMessageBox,
    QComboBox,
    QLineEdit,
    QSizePolicy,
)

from PySide6.QtCore import Qt, Slot, QStandardPaths, Signal, QObject, QPoint, QDir, QSize

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
    QIntValidator,
    QCursor,
)
import sys
import cv2
import numpy as np

import globals
from painter_widget import painter_widget
from painter_widget_mhd import painter_widget_mhd
from painter_widget_differences import painter_widget_differences


class NumericLineEdit(QLineEdit):
    enterPressed = Signal(int)  # Señal personalizada

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setValidator(QIntValidator())  # Solo permitir números enteros
        self.minimum = globals.CANVAS_WIDTH
        self.maximum = globals.CANVAS_MAXIMUM

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            value = int(self.text())
            if value >= self.minimum and value <= self.maximum:
                self.enterPressed.emit(value)  # Emitir señal personalizada
        else:
            super().keyPressEvent(event)  # Procesar otros eventos normalmente

    def setMinimum(self, value):
        self.minimum = value

    def setMaximum(self, value):
        self.maximum = value

    def setValue(self, value):
        self.setText(str(value))

class MainWindow(QMainWindow):
    """An Application example to draw using a pen """

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.setSizePolicy(size_policy)
        # print(os.environ)
        # print(sys.executable)
        # print(sys.path)
        self.main_widget = QWidget()
        self.layout_main = QHBoxLayout()

        widget_painting = QWidget()
        widget_painting.setSizePolicy(size_policy)

        vboxlayout_painting = QVBoxLayout()
        vboxlayout_painting.setSpacing(0)
        vboxlayout_painting.setContentsMargins(0,0,0,0)


        label_painting = QLabel('Painting')
        label_painting.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_painting.setSizePolicy(size_policy)

        self.painting_widget = painter_widget(self)
        self.painting_widget.my_released.connect(self.update_painting_widgets)

        vboxlayout_painting.addWidget(label_painting)
        vboxlayout_painting.addWidget(self.painting_widget,10)

        widget_painting.setLayout(vboxlayout_painting)

        #
        widget_mhd = QWidget()
        vboxlayout_mhd = QVBoxLayout()
        vboxlayout_mhd.setSpacing(0)
        vboxlayout_mhd.setContentsMargins(0, 0, 0, 0)

        label_mhd = QLabel('MHD')
        # label_mhd.sizeHint()
        label_mhd.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_mhd.setSizePolicy(size_policy)
        self.mhd_widget = painter_widget_mhd(self)

        vboxlayout_mhd.addWidget(label_mhd)
        vboxlayout_mhd.addWidget(self.mhd_widget,10)
        widget_mhd.setLayout(vboxlayout_mhd)

        #
        widget_differences = QWidget()
        vboxlayout_differences = QVBoxLayout()
        vboxlayout_differences.setSpacing(0)
        vboxlayout_differences.setContentsMargins(0, 0, 0, 0)

        self.label_differences = QLabel('Differences (100%)')
        self.label_differences.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_differences.setSizePolicy(size_policy)
        self.differences_widget = painter_widget_differences(self)

        vboxlayout_differences.addWidget(self.label_differences)
        vboxlayout_differences.addWidget(self.differences_widget,10)
        widget_differences.setLayout(vboxlayout_differences)

        #
        self.tab_widget = QTabWidget()
        self.tab_widget.setMaximumWidth(globals.TAB_SIZE)
        self.tab_widget.setMinimumWidth(globals.TAB_SIZE)
        self.tab_widget.addTab(self.add_tab1(), "Actions")
        self.tab_widget.addTab(self.add_tab2(), "Draw")

        self.layout_main.addWidget(widget_painting)
        self.layout_main.addWidget(widget_mhd)
        self.layout_main.addWidget(widget_differences)
        self.layout_main.addWidget(self.tab_widget)

        self.main_widget.setLayout(self.layout_main)
        self.mhd_parameters_values = globals.MHD_PARAMETERS

        # actions
        action_load_image =QAction(QApplication.style().standardIcon(QStyle.SP_DialogOpenButton),'Load image',self)
        action_load_image.triggered.connect(self.load_image)

        action_save_image = QAction(QApplication.style().standardIcon(QStyle.SP_DialogSaveButton),'Save image', self)
        action_save_image.triggered.connect(self.save_image)

        action_save_images = QAction(QApplication.style().standardIcon(QStyle.SP_DialogSaveButton), 'Save images', self)
        action_save_images.triggered.connect(self.save_images)

        action_save_image_with_positions = QAction(QApplication.style().standardIcon(QStyle.SP_DialogSaveButton), 'Save image with pos.', self)
        action_save_image_with_positions.triggered.connect(self.save_image_with_positions)

        action_load_positions = QAction(QApplication.style().standardIcon(QStyle.SP_DialogOpenButton), 'Load positions', self)
        action_load_positions.triggered.connect(self.load_positions)

        action_save_positions = QAction(QApplication.style().standardIcon(QStyle.SP_DialogSaveButton), 'Save positions', self)
        action_save_positions.triggered.connect(self.save_positions)


        action_exit = QAction('Exit', self)
        action_exit.triggered.connect(QApplication.quit)

        #
        self.menu_bar = self.menuBar()
        menu_file = self.menu_bar.addMenu('File')
        menu_file.addAction(action_load_image)
        menu_file.addAction(action_save_image)
        menu_file.addAction(action_save_images)
        menu_file.addAction(action_save_image_with_positions)
        menu_file.addSeparator()
        menu_file.addAction(action_load_positions)
        menu_file.addAction(action_save_positions)
        menu_file.addSeparator()
        menu_file.addAction(action_exit)

        #
        self.bar = self.addToolBar("Draw")
        self.bar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.draw_action = QAction(QIcon('icons/applications-painting.svg'),'Draw', self, checkable=True)
        self.draw_action.triggered.connect(self.on_draw)
        self.bar.addAction(self.draw_action)

        self.add_positions_action = QAction(QIcon('icons/add_points.png'), 'Add positions', self, checkable=True)
        self.add_positions_action.triggered.connect(self.on_add_positions)
        self.bar.addAction(self.add_positions_action)

        self.remove_positions_action = QAction(QIcon('icons/delete_points.png'), 'Remove positions', self, checkable=True)
        self.remove_positions_action.triggered.connect(self.on_remove_positions)
        self.bar.addAction(self.remove_positions_action)

        self.show_minimum_action = QAction(QIcon('icons/move_points.png'), 'Show minimum', self, checkable=True)
        self.show_minimum_action.triggered.connect(self.on_show_minimum)
        self.bar.addAction(self.show_minimum_action)

        self.bar.addAction(
            qApp.style().standardIcon(QStyle.SP_DialogResetButton),  # noqa: F821
            "Clear",
            self.on_clear,
        )
        self.bar.addSeparator()

        self.color_action = QAction('Pigment')
        self.color_action.triggered.connect(self.on_color_clicked)
        self.bar.addAction(self.color_action)

        self.setCentralWidget(self.main_widget)

        self.mode = globals.MODE_DRAW

        self.brush_color = Qt.red
        self.set_color(self.brush_color)

        self.compute_mhd_value = False
        self.compute_differences_value = False

        # self.image_rgb = cv2.Mat
        # self.image_rgb_processed = cv2.Mat

        self.image_loaded = False
        self.difference_threshold = 0

        self.canvas_width = globals.CANVAS_WIDTH
        self.canvas_height = globals.CANVAS_HEIGHT

        self.adjustSize()
        self.setFixedSize(self.size())

        self.mode_draw = False
        self.mode_add_positions = False
        self.mode_remove_positions = False
        self.mode_show_minimum_distance = False

        # button = QMessageBox.information(self, "Information", "Adjust the size of the window to your needs before loading an image or painting in the canvas")

    def add_tab1(self):
        # Crea un widget para el contenido de la primera pestaña
        tab1_widget = QWidget()
        # Crea un layout y añade widgets al layout
        tab1_vboxlayout = QVBoxLayout()

        #
        groupbox_show = QGroupBox('Show')
        gridlayout_show = QGridLayout()

        label_show_pos1 = QLabel('Positions w1')
        checkbox_show_pos1 = QCheckBox()
        checkbox_show_pos1.setChecked(True)
        checkbox_show_pos1.stateChanged.connect(self.painting_widget.set_show_positions)

        label_show_pos2 = QLabel('Positions w2')
        checkbox_show_pos2 = QCheckBox()
        checkbox_show_pos2.setChecked(True)
        checkbox_show_pos2.stateChanged.connect(self.mhd_widget.set_show_positions)

        gridlayout_show.addWidget(label_show_pos1, 0, 0)
        gridlayout_show.addWidget(checkbox_show_pos1, 0, 1)
        gridlayout_show.addWidget(label_show_pos2, 1, 0)
        gridlayout_show.addWidget(checkbox_show_pos2, 1, 1)

        groupbox_show.setLayout(gridlayout_show)

        #
        groupbox_color = QGroupBox('Color')
        gridlayout_color = QGridLayout()

        label_color_smooth = QLabel('Smooth')
        combobox_color_smooth = QComboBox()
        text = [str(value) for value in globals.COLOR_SMOOTH_KERNEL_SIZE]
        combobox_color_smooth.addItems(text)
        combobox_color_smooth.currentIndexChanged.connect(self.change_color_smooth)

        label_color_model = QLabel('Model')
        combobox_color_model = QComboBox()
        combobox_color_model.addItems(globals.COLOR_MODELS)
        combobox_color_model.currentIndexChanged.connect(self.change_color_model)

        label_color_kmeans = QLabel('k-means')
        checkbox_color_kmeans = QCheckBox()
        checkbox_color_kmeans.stateChanged.connect(self.change_compute_kmeans)

        gridlayout_color.addWidget(label_color_smooth, 0, 0)
        gridlayout_color.addWidget(combobox_color_smooth, 0, 1)
        gridlayout_color.addWidget(label_color_model, 1, 0)
        gridlayout_color.addWidget(combobox_color_model, 1, 1)
        gridlayout_color.addWidget(label_color_kmeans, 2, 0)
        gridlayout_color.addWidget(checkbox_color_kmeans, 2, 1)

        groupbox_color.setLayout(gridlayout_color)
        #
        groupbox_compute = QGroupBox('Compute')
        gridlayout_compute = QGridLayout()

        label_mhd = QLabel('MHD')
        self.checkbox_compute_mhd = QCheckBox()
        self.checkbox_compute_mhd.stateChanged.connect(self.change_compute_mhd_value)

        label_show_differences = QLabel('Differences')
        self.checkbox_compute_differences = QCheckBox()
        self.checkbox_compute_differences.stateChanged.connect(self.change_compute_differences_value)

        gridlayout_compute.addWidget(label_mhd, 0, 0)
        gridlayout_compute.addWidget(self.checkbox_compute_mhd, 0, 1)
        gridlayout_compute.addWidget(label_show_differences, 1, 0)
        gridlayout_compute.addWidget(self.checkbox_compute_differences, 1, 1)

        groupbox_compute.setLayout(gridlayout_compute)

        #
        groupbox_mhd_parameters = QGroupBox('MHD parameters')
        gridlayout_mhd_parameters = QGridLayout()

        text_labels = ['Color 1','Color 2','Color 3', 'Position 1', 'Position 2']
        self.list_checkbox = []

        for pos in range(len(text_labels)):
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            checkbox.clicked.connect(self.change_mhd_parameters)
            self.list_checkbox.append(checkbox)
            gridlayout_mhd_parameters.addWidget(QLabel(text_labels[pos]), pos, 0)
            gridlayout_mhd_parameters.addWidget(self.list_checkbox[pos], pos, 1)

        groupbox_mhd_parameters.setLayout(gridlayout_mhd_parameters)

        # Establece el layout en el widget
        tab1_vboxlayout.addWidget(groupbox_show)
        tab1_vboxlayout.addWidget(groupbox_color)
        tab1_vboxlayout.addWidget(groupbox_compute)
        tab1_vboxlayout.addWidget(groupbox_mhd_parameters)
        tab1_vboxlayout.addStretch()

        tab1_widget.setLayout(tab1_vboxlayout)

        return tab1_widget

    def add_tab2(self):
        # Crea un widget para el contenido de la primera pestaña
        tab2_widget = QWidget()
        # Crea un layout y añade widgets al layout
        tab2_layout = QVBoxLayout()

        #
        tab2_aux_widget = QWidget()
        tab2_gridlayout = QGridLayout()

        tab2_label_canvas_width = QLabel('Canvas width')
        self.tab2_numericlineedit_canvas_width = NumericLineEdit()
        self.tab2_numericlineedit_canvas_width.setMinimum(globals.CANVAS_WIDTH)  # Valor mínimo
        self.tab2_numericlineedit_canvas_width.setMaximum(5000)  # Valor máximo
        self.tab2_numericlineedit_canvas_width.setValue(globals.CANVAS_WIDTH)
        self.tab2_numericlineedit_canvas_width.enterPressed.connect(self.canvas_width_changed)

        tab2_label_canvas_height = QLabel('Canvas height')
        self.tab2_numericlineedit_canvas_height = NumericLineEdit()
        self.tab2_numericlineedit_canvas_height.setMinimum(globals.CANVAS_WIDTH)  # Valor mínimo
        self.tab2_numericlineedit_canvas_height.setMaximum(5000)  # Valor máximo
        self.tab2_numericlineedit_canvas_height.setValue(globals.CANVAS_WIDTH)
        self.tab2_numericlineedit_canvas_height.enterPressed.connect(self.canvas_height_changed)

        tab2_label_size = QLabel('Brush size')
        tab2_slider_size =QSlider(Qt.Orientation.Horizontal)
        tab2_slider_size.setRange(globals.BRUSH_MIN_SIZE,globals.BRUSH_MAX_SIZE)
        tab2_slider_size.setValue(globals.BRUSH_SIZE_DEFAULT)
        tab2_slider_size.valueChanged.connect(self.brush_size_changed)

        tab2_label_num_clusters = QLabel('Num clusters')
        tab2_spinbox_num_clusters = QSpinBox()
        tab2_spinbox_num_clusters.setMinimum(2)  # Valor mínimo
        tab2_spinbox_num_clusters.setMaximum(50)  # Valor máximo
        tab2_spinbox_num_clusters.setValue(globals.KMEANS_NUM_CLUSTERS)
        tab2_spinbox_num_clusters.valueChanged.connect(self.num_clusters_changed)

        tab2_label_threshold = QLabel('Threshold')
        tab2_spinbox_num_threshold = QSpinBox()
        tab2_spinbox_num_threshold.setSuffix('%')
        tab2_spinbox_num_threshold.setRange(0,100)
        tab2_spinbox_num_threshold.setValue(0)
        tab2_spinbox_num_threshold.valueChanged.connect(self.difference_threshold_changed)

        tab2_gridlayout.addWidget(tab2_label_canvas_width, 0, 0)
        tab2_gridlayout.addWidget(self.tab2_numericlineedit_canvas_width,0, 1)
        tab2_gridlayout.addWidget(tab2_label_canvas_height, 1, 0)
        tab2_gridlayout.addWidget(self.tab2_numericlineedit_canvas_height, 1, 1)
        tab2_gridlayout.addWidget(tab2_slider_size, 2, 1)
        tab2_gridlayout.addWidget(tab2_label_size, 2, 0)
        tab2_gridlayout.addWidget(tab2_slider_size, 2, 1)
        tab2_gridlayout.addWidget(tab2_label_num_clusters, 3, 0)
        tab2_gridlayout.addWidget(tab2_spinbox_num_clusters, 3, 1)
        tab2_gridlayout.addWidget(tab2_label_threshold, 4, 0)
        tab2_gridlayout.addWidget(tab2_spinbox_num_threshold, 4, 1)

        tab2_aux_widget.setLayout(tab2_gridlayout)

        # Establece el layout en el widget
        tab2_layout.addWidget(tab2_aux_widget)
        tab2_layout.addStretch()

        tab2_widget.setLayout(tab2_layout)

        return tab2_widget

    # def sizeHint(self):
    #     return self.layout_main.sizeHint()

    # def resizeEvent(self, event):
    #     # Cuando el QWidget es redimensionado, actualiza el QPixmap para coincidir con el nuevo tamaño
    #     # self.blockSignals(True)
    #     size = event.size()
    #     # print("Size ", size)
    #     self.canvas_width = int((size.width() - self.tab_widget.width())/3)
    #     self.canvas_height = int(size.height()- self.label_differences.height() - 66)
    #     # self.painting_widget.set_size(self.canvas_width, self.canvas_height)
    #     # self.mhd_widget.set_size(self.canvas_width, self.canvas_height)
    #     # self.differences_widget.set_size(self.canvas_width, self.canvas_height)
    #     # self.blockSignals(False)
    #     self.tab2_numericlineedit_canvas_width.setValue(self.canvas_width)
    #     self.tab2_numericlineedit_canvas_height.setValue(self.canvas_height)
    #     super().resizeEvent(event)


    @Slot()
    def load_image(self):
        dialog = QFileDialog(self, "Load image")
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setNameFilter("Image files (*.png *.jpg)")
        dialog.setDirectory(QDir(os.getcwd()+'/data'))

        if dialog.exec() == QFileDialog.Accepted:
            if dialog.selectedFiles():
                """ load pixmap from filename """
                image_bgr = cv2.imread(dialog.selectedFiles()[0])
                self.image_width = self.canvas_width
                self.image_height = int(self.image_width * image_bgr.shape[0] / image_bgr.shape[1])
                self.canvas_height = self.image_height

                # adjust all the sizes
                self.change_size()

                image_bgr = cv2.resize(image_bgr, (self.image_width, self.image_height))
                self.image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

                # pixmap = self.convert_cv_mat_to_qt_pixmap(self.image_rgb)
                # pixmap = pixmap.scaledToWidth(self.painting_widget.width(), Qt.TransformationMode.SmoothTransformation)

                # self.painting_widget.setFixedSize(pixmap.size())
                # self.painting_widget.set_image_size(pixmap.size())
                self.painting_widget.set_image(self.image_rgb)

                # self.mhd_widget.setFixedSize(pixmap.size())
                # self.mhd_widget.set_image_size(pixmap.size())

                # self.differences_widget.setFixedSize(pixmap.size())
                # self.differences_widget.set_image_size(pixmap.size())

                self.image_loaded = True
                self.update_painting_widgets()

    @Slot()
    def save_image(self):
        dialog = QFileDialog(self, "Save image")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setDefaultSuffix("png")
        dialog.setDirectory(QDir(os.getcwd()+'/data'))

        if dialog.exec() == QFileDialog.Accepted:
            if dialog.selectedFiles():
                """ save pixmap to filename """
                self.painting_widget.get_pixmap().save(dialog.selectedFiles()[0])
                QMessageBox.information(self,'Information','The file has been correctly saved')

    @Slot()
    def save_images(self):
        dialog = QFileDialog(self, "Save images")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setDefaultSuffix("png")
        dialog.setDirectory(QDir(os.getcwd()+'/data'))

        if dialog.exec() == QFileDialog.Accepted:
            if dialog.selectedFiles():
                """ Takes the full path and removes the extensio """
                file_name_without_ext = os.path.splitext(dialog.selectedFiles()[0])[0]
                self.painting_widget.get_pixmap().save(file_name_without_ext+'_ori.png')
                self.mhd_widget.get_pixmap().save(file_name_without_ext+'_mhd.png')
                self.differences_widget.get_pixmap().save(file_name_without_ext+'_dif.png')
                QMessageBox.information(self, 'Information', 'The files have been correctly saved')

    @Slot()
    def save_image_with_positions(self):
        dialog = QFileDialog(self, "Save image")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setDefaultSuffix("png")
        dialog.setDirectory(QDir(os.getcwd() + '/data'))

        if dialog.exec() == QFileDialog.Accepted:
            if dialog.selectedFiles():
                """ save pixmap to filename """
                self.painting_widget.paint_positions().save(dialog.selectedFiles()[0])
                QMessageBox.information(self, 'Information', 'The file has been correctly saved')

    @Slot()
    def load_positions(self):
        dialog = QFileDialog(self, "Load positions")
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setNameFilter("Positions files (*.csv)")
        dialog.setDirectory(QDir(os.getcwd()+'/data'))

        if dialog.exec() == QFileDialog.Accepted:
            if dialog.selectedFiles():
                with open(dialog.selectedFiles()[0], mode='r', encoding='utf-8') as file:
                    lines =file.readlines()
                    self.painting_widget.positions = []

                    for pos in range(1,len(lines)):
                        line = lines[pos].strip()
                        tokens = line.split(';')
                        # read as x, y but added as y, x for numpy
                        self.painting_widget.positions.append([int(float(tokens[2])*(self.image_height-1)),int(float(tokens[1])*(self.image_width-1))])

                    # self.painting_widget.update_colors()
                    self.update_painting_widgets()
                    self.update()

    @Slot()
    def save_positions(self,file_name):
        dialog = QFileDialog(self, "Save positions")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilter("Positions files (*.csv)")
        dialog.setDirectory(QDir(os.getcwd() + '/data'))

        if dialog.exec() == QFileDialog.Accepted:
            if dialog.selectedFiles():
                with open(dialog.selectedFiles()[0], mode='w', encoding='utf-8') as file:
                    # file.write('WIDTH;' + str(self.painting_widget.pixmap.width()) + '\n')
                    # file.write('HEIGHT;' + str(self.painting_widget.pixmap.height()) + '\n')
                    file.write('Pos;X;Y\n')
                    # Itera sobre las filas del archivo CSV
                    for pos in range(len(self.painting_widget.positions)):
                        # save as x, y
                        x = float(self.painting_widget.positions[pos][1])/float(self.image_width-1)
                        y = float(self.painting_widget.positions[pos][0]) / float(self.image_height - 1)
                        file.write(str(pos+1)+';'+str(x)+';'+str(y)+'\n')

                    file.close()

    def change_size(self):
        margins = self.layout_main.contentsMargins()
        space = self.layout_main.spacing()

        wm = margins.right() + margins.left()
        hm = margins.top() + margins.bottom()
        self.painting_widget.set_size(self.canvas_width, self.canvas_height)
        self.mhd_widget.set_size(self.canvas_width, self.canvas_height)
        self.differences_widget.set_size(self.canvas_width, self.canvas_height)
        self.main_widget.setFixedSize(3*self.canvas_width+self.tab_widget.width() + wm + 2*space,
                                      self.canvas_height+self.label_differences.height() + hm + 2*space)
        self.main_widget.adjustSize()
        self.adjustSize()
        self.setFixedSize(self.size())

    @Slot()
    def canvas_width_changed(self, value):
        self.canvas_width = value
        self.canvas_height = value
        self.change_size()
        self.tab2_numericlineedit_canvas_height.setValue(value)

    @Slot()
    def canvas_height_changed(self, value):
        self.canvas_height = value
        self.change_size()

    @Slot()
    def brush_size_changed(self, value):
        self.painting_widget.set_brush_size(value)

    @Slot()
    def num_clusters_changed(self, value):
        self.painting_widget.set_kmeans_num_clusters_value(value)
        self.update_painting_widgets()

    @Slot()
    def difference_threshold_changed(self, value):
        self.difference_threshold = value
        self.update_painting_widgets()


    @Slot()
    def set_show_positions_w1(self, state):
        if state == Qt.Checked:
            self.painting_widget.set_show_positions(True)
        elif state == Qt.Unchecked:
            self.painting_widget.set_show_positions(False)

    @Slot()
    def set_show_positions_w2(self, state):
        if state == Qt.Checked:
            self.mhd_widget.set_show_positions(True)
        elif state == Qt.Unchecked:
            self.mhd_widget.set_show_positions(False)

    @Slot()
    def change_color_smooth(self, index):
        self.painting_widget.set_color_smooth(index)
        self.update_painting_widgets()

    @Slot()
    def change_color_model(self, index):
        self.painting_widget.set_color_model(index)
        self.update_painting_widgets()

    @Slot()
    def change_compute_kmeans(self, state):
        if state == 2:
            self.painting_widget.set_compute_kmeans(True)
        elif state == 0:
            self.painting_widget.set_compute_kmeans(False)
        self.update_painting_widgets()

    @Slot()
    def change_compute_mhd_value(self, state):
        if state == 2: # enable
            self.compute_mhd_value = True
        elif state == 0:
            self.compute_mhd_value = False

            # disable differences
            if self.checkbox_compute_differences.isChecked() == True:
                self.compute_differences_value = False
                self.differences_widget.set_compute_differences_value(self.compute_differences_value)

                self.checkbox_compute_differences.blockSignals(True)
                self.checkbox_compute_differences.setChecked(False)
                self.checkbox_compute_differences.blockSignals(False)

                # self.differences_widget.reset_pixmap()

        self.mhd_widget.set_compute_mhd_value(self.compute_mhd_value)
        self.update_painting_widgets()

    @Slot()
    def change_compute_differences_value(self, state):
        if self.checkbox_compute_mhd.isChecked() == True:
            if state == 2:
                self.compute_differences_value = True
            elif state == 0:
                self.compute_differences_value = False

            self.differences_widget.set_compute_differences_value(self.compute_differences_value)
            self.update_painting_widgets()
        else:
            self.checkbox_compute_differences.blockSignals(True)
            self.checkbox_compute_differences.setChecked(False)
            self.checkbox_compute_differences.blockSignals(False)

    @Slot()
    def change_mhd_parameters(self):
        valid = False
        for pos in range(len(self.list_checkbox)):
            if self.list_checkbox[pos].isChecked():
                valid = True
                break

        checkbox = self.sender()
        if valid==True:
            pos = self.list_checkbox.index(checkbox)
            if checkbox.isChecked():
                self.mhd_parameters_values[pos] = True
            else:
                self.mhd_parameters_values[pos] = False

            self.painting_widget.set_mhd_parameters(self.mhd_parameters_values)
            self.mhd_widget.set_mhd_parameters(self.mhd_parameters_values)

            self.update_painting_widgets()
        else:
            checkbox.blockSignals(True)
            checkbox.setChecked(True)
            checkbox.blockSignals(False)

    @Slot()
    def update_painting_widgets(self):
        self.painting_widget.process_image()

        positions, colors, image_painting = self.painting_widget.get_values()
        # update the information for MHD
        if self.compute_mhd_value == True and len(positions)>0:
            self.mhd_widget.set_values(positions, colors, image_painting)
            self.mhd_widget.compute_mhd()

        if self.compute_differences_value == True:
            self.differences_widget.set_values(positions, colors, image_painting, self.mhd_widget.get_image_mhd(), self.difference_threshold)
            percentage = self.differences_widget.compute_differences()
            self.label_differences.setText('Differences ('+str(percentage)+'%)')

    @Slot()
    def on_clear(self):
        self.painting_widget.clear()
        self.update_painting_widgets()

    @Slot()
    def on_draw(self):
        self.mode_draw = not self.mode_draw
        self.add_positions_action.setChecked(False)
        self.remove_positions_action.setChecked(False)
        self.show_minimum_action.setChecked(False)
        self.painting_widget.set_mode_value(globals.MODE_DRAW)


    @Slot()
    def on_add_positions(self):
        self.mode_add_positions = not self.mode_add_positions
        if self.mode_add_positions == True:
            self.painting_widget.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        else:
            self.painting_widget.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

        self.draw_action.setChecked(False)
        self.remove_positions_action.setChecked(False)
        self.show_minimum_action.setChecked(False)
        self.painting_widget.set_mode_value(globals.MODE_ADD_POSITIONS)


    @Slot()
    def on_remove_positions(self):
        self.mode_remove_positions = not self.mode_remove_positions
        if self.mode_remove_positions == True:
            self.painting_widget.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        else:
            self.painting_widget.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.draw_action.setChecked(False)
        self.add_positions_action.setChecked(False)
        self.show_minimum_action.setChecked(False)
        self.painting_widget.set_mode_value(globals.MODE_REMOVE_POSITIONS)

    @Slot()
    def on_show_minimum(self):
        self.mode_show_minimum_distance = not self.mode_show_minimum_distance
        if self.mode_show_minimum_distance == True:
            self.painting_widget.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        else:
            self.painting_widget.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

        self.draw_action.setChecked(False)
        self.add_positions_action.setChecked(False)
        self.remove_positions_action.setChecked(False)
        self.painting_widget.set_mode_value(globals.MODE_MINIMUM)


    @Slot()
    def on_color_clicked(self):
        color = QColorDialog.getColor(self.brush_color, self)
        if color:
            self.set_color(color)

    def set_color(self, brush_color: QColor = Qt.black):
        self.brush_color = QColor(brush_color)
        # Create color icon
        pix_icon = QPixmap(32, 32)
        pix_icon.fill(self.brush_color)

        self.color_action.setIcon(QIcon(pix_icon))
        self.painting_widget.set_brush_color((self.brush_color.red(), self.brush_color.green(), self.brush_color.blue()))

    def convert_cv_mat_to_qt_pixmap(self, image):
        """Convertir de una imagen de OpenCV a QPixmap"""
        height, width, channels = image.shape
        bytes_per_line = channels * width
        qt_image = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(qt_image)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeDialogs, True)

    w = MainWindow()
    w.show()
    sys.exit(app.exec())
