################################################################################
## Form generated from reading UI file 'settings.ui'
##
## Created by: Qt User Interface Compiler version 6.2.2
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
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(436, 348)
        self.cancel_button = QPushButton(Dialog)
        self.cancel_button.setObjectName(u"cancel_button")
        self.cancel_button.setGeometry(QRect(350, 310, 75, 24))
        self.ok_button = QPushButton(Dialog)
        self.ok_button.setObjectName(u"ok_button")
        self.ok_button.setGeometry(QRect(260, 310, 75, 24))
        self.drives_line_edit = QLineEdit(Dialog)
        self.drives_line_edit.setObjectName(u"drives_line_edit")
        self.drives_line_edit.setGeometry(QRect(90, 30, 113, 21))
        self.drives_label = QLabel(Dialog)
        self.drives_label.setObjectName(u"drives_label")
        self.drives_label.setGeometry(QRect(30, 30, 49, 16))
        self.wait_label = QLabel(Dialog)
        self.wait_label.setObjectName(u"wait_label")
        self.wait_label.setGeometry(QRect(30, 70, 49, 16))
        self.wait_line_edit = QLineEdit(Dialog)
        self.wait_line_edit.setObjectName(u"wait_line_edit")
        self.wait_line_edit.setGeometry(QRect(90, 70, 113, 21))
        self.change_state_button = QPushButton(Dialog)
        self.change_state_button.setObjectName(u"change_state_button")
        self.change_state_button.setGeometry(QRect(300, 220, 101, 41))
        QWidget.setTabOrder(self.drives_line_edit, self.wait_line_edit)
        QWidget.setTabOrder(self.wait_line_edit, self.change_state_button)
        QWidget.setTabOrder(self.change_state_button, self.ok_button)
        QWidget.setTabOrder(self.ok_button, self.cancel_button)

        self.retranslateUi(Dialog)

        self.cancel_button.setDefault(False)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.cancel_button.setText(QCoreApplication.translate("Dialog", u"Cancel", None))
        self.ok_button.setText(QCoreApplication.translate("Dialog", u"Ok", None))
        self.drives_label.setText(QCoreApplication.translate("Dialog", u"Drives", None))
        self.wait_label.setText(QCoreApplication.translate("Dialog", u"Wait", None))
        self.change_state_button.setText(QCoreApplication.translate("Dialog", u"Start/Stop", None))
    # retranslateUi
