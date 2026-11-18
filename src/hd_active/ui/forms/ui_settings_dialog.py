# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.12.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QCheckBox,
    QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout,
    QFrame, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)
from . import resources_rc

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName(u"SettingsDialog")
        SettingsDialog.resize(420, 320)
        icon = QIcon()
        icon.addFile(u":/images/hard_drive_icon.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        SettingsDialog.setWindowIcon(icon)
        self.vertical_layout = QVBoxLayout(SettingsDialog)
        self.vertical_layout.setObjectName(u"vertical_layout")
        self.drives_label = QLabel(SettingsDialog)
        self.drives_label.setObjectName(u"drives_label")

        self.vertical_layout.addWidget(self.drives_label)

        self.drives_layout = QHBoxLayout()
        self.drives_layout.setObjectName(u"drives_layout")
        self.drives_list = QListWidget(SettingsDialog)
        self.drives_list.setObjectName(u"drives_list")
        self.drives_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.drives_layout.addWidget(self.drives_list)

        self.drives_buttons_layout = QVBoxLayout()
        self.drives_buttons_layout.setObjectName(u"drives_buttons_layout")
        self.add_drive_button = QPushButton(SettingsDialog)
        self.add_drive_button.setObjectName(u"add_drive_button")

        self.drives_buttons_layout.addWidget(self.add_drive_button)

        self.remove_drive_button = QPushButton(SettingsDialog)
        self.remove_drive_button.setObjectName(u"remove_drive_button")
        self.remove_drive_button.setEnabled(False)

        self.drives_buttons_layout.addWidget(self.remove_drive_button)

        self.drives_buttons_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.drives_buttons_layout.addItem(self.drives_buttons_spacer)


        self.drives_layout.addLayout(self.drives_buttons_layout)


        self.vertical_layout.addLayout(self.drives_layout)

        self.form_layout = QFormLayout()
        self.form_layout.setObjectName(u"form_layout")
        self.wait_label = QLabel(SettingsDialog)
        self.wait_label.setObjectName(u"wait_label")

        self.form_layout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.wait_label)

        self.wait_spin_box = QDoubleSpinBox(SettingsDialog)
        self.wait_spin_box.setObjectName(u"wait_spin_box")
        self.wait_spin_box.setDecimals(1)
        self.wait_spin_box.setMinimum(0.100000000000000)
        self.wait_spin_box.setMaximum(86400.000000000000000)
        self.wait_spin_box.setValue(60.000000000000000)

        self.form_layout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.wait_spin_box)

        self.run_on_start_check_box = QCheckBox(SettingsDialog)
        self.run_on_start_check_box.setObjectName(u"run_on_start_check_box")

        self.form_layout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.run_on_start_check_box)


        self.vertical_layout.addLayout(self.form_layout)

        self.line = QFrame(SettingsDialog)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.vertical_layout.addWidget(self.line)

        self.state_layout = QHBoxLayout()
        self.state_layout.setObjectName(u"state_layout")
        self.status_label = QLabel(SettingsDialog)
        self.status_label.setObjectName(u"status_label")

        self.state_layout.addWidget(self.status_label)

        self.state_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.state_layout.addItem(self.state_spacer)

        self.log_button = QPushButton(SettingsDialog)
        self.log_button.setObjectName(u"log_button")
        self.log_button.setAutoDefault(False)

        self.state_layout.addWidget(self.log_button)

        self.change_state_button = QPushButton(SettingsDialog)
        self.change_state_button.setObjectName(u"change_state_button")
        self.change_state_button.setAutoDefault(False)

        self.state_layout.addWidget(self.change_state_button)


        self.vertical_layout.addLayout(self.state_layout)

        self.button_box = QDialogButtonBox(SettingsDialog)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.vertical_layout.addWidget(self.button_box)

#if QT_CONFIG(shortcut)
        self.drives_label.setBuddy(self.drives_list)
        self.wait_label.setBuddy(self.wait_spin_box)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.drives_list, self.add_drive_button)
        QWidget.setTabOrder(self.add_drive_button, self.remove_drive_button)
        QWidget.setTabOrder(self.remove_drive_button, self.wait_spin_box)
        QWidget.setTabOrder(self.wait_spin_box, self.run_on_start_check_box)
        QWidget.setTabOrder(self.run_on_start_check_box, self.log_button)
        QWidget.setTabOrder(self.log_button, self.change_state_button)

        self.retranslateUi(SettingsDialog)
        self.button_box.accepted.connect(SettingsDialog.accept)
        self.button_box.rejected.connect(SettingsDialog.reject)

        QMetaObject.connectSlotsByName(SettingsDialog)
    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"HD Active", None))
        self.drives_label.setText(QCoreApplication.translate("SettingsDialog", u"&Drives", None))
        self.add_drive_button.setText(QCoreApplication.translate("SettingsDialog", u"&Add...", None))
        self.remove_drive_button.setText(QCoreApplication.translate("SettingsDialog", u"&Remove", None))
        self.wait_label.setText(QCoreApplication.translate("SettingsDialog", u"&Wait between writes", None))
        self.wait_spin_box.setSuffix(QCoreApplication.translate("SettingsDialog", u" s", None))
        self.run_on_start_check_box.setText(QCoreApplication.translate("SettingsDialog", u"&Start writing when HD Active starts", None))
        self.status_label.setText(QCoreApplication.translate("SettingsDialog", u"Stopped", None))
        self.log_button.setText(QCoreApplication.translate("SettingsDialog", u"&Log", None))
        self.change_state_button.setText(QCoreApplication.translate("SettingsDialog", u"Start", None))
    # retranslateUi

