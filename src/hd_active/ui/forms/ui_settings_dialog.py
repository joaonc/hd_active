# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
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
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QHBoxLayout,
    QLabel, QLayout, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(300, 151)
        Dialog.setMinimumSize(QSize(300, 150))
        Dialog.setMaximumSize(QSize(800, 300))
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.drives_label = QLabel(Dialog)
        self.drives_label.setObjectName(u"drives_label")

        self.gridLayout.addWidget(self.drives_label, 0, 0, 1, 1)

        self.drives_line_edit = QLineEdit(Dialog)
        self.drives_line_edit.setObjectName(u"drives_line_edit")

        self.gridLayout.addWidget(self.drives_line_edit, 0, 1, 1, 1)

        self.wait_label = QLabel(Dialog)
        self.wait_label.setObjectName(u"wait_label")

        self.gridLayout.addWidget(self.wait_label, 1, 0, 1, 1)

        self.wait_line_edit = QLineEdit(Dialog)
        self.wait_line_edit.setObjectName(u"wait_line_edit")
        self.wait_line_edit.setMaximumSize(QSize(40, 16777215))

        self.gridLayout.addWidget(self.wait_line_edit, 1, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.log_button = QPushButton(Dialog)
        self.log_button.setObjectName(u"log_button")

        self.horizontalLayout_2.addWidget(self.log_button)

        self.change_state_button = QPushButton(Dialog)
        self.change_state_button.setObjectName(u"change_state_button")

        self.horizontalLayout_2.addWidget(self.change_state_button)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.ok_button = QPushButton(Dialog)
        self.ok_button.setObjectName(u"ok_button")

        self.horizontalLayout.addWidget(self.ok_button)

        self.cancel_button = QPushButton(Dialog)
        self.cancel_button.setObjectName(u"cancel_button")

        self.horizontalLayout.addWidget(self.cancel_button)


        self.verticalLayout.addLayout(self.horizontalLayout)

#if QT_CONFIG(shortcut)
        self.drives_label.setBuddy(self.drives_line_edit)
        self.wait_label.setBuddy(self.wait_line_edit)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.drives_line_edit, self.wait_line_edit)
        QWidget.setTabOrder(self.wait_line_edit, self.log_button)
        QWidget.setTabOrder(self.log_button, self.change_state_button)
        QWidget.setTabOrder(self.change_state_button, self.ok_button)
        QWidget.setTabOrder(self.ok_button, self.cancel_button)

        self.retranslateUi(Dialog)

        self.ok_button.setDefault(True)
        self.cancel_button.setDefault(False)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"HD Active", None))
        self.drives_label.setText(QCoreApplication.translate("Dialog", u"Drives", None))
        self.wait_label.setText(QCoreApplication.translate("Dialog", u"Wait", None))
        self.log_button.setText(QCoreApplication.translate("Dialog", u"Log", None))
        self.change_state_button.setText(QCoreApplication.translate("Dialog", u"Start/Stop", None))
        self.ok_button.setText(QCoreApplication.translate("Dialog", u"Ok", None))
        self.cancel_button.setText(QCoreApplication.translate("Dialog", u"Cancel", None))
    # retranslateUi

