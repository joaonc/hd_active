# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'log_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QPushButton, QSizePolicy,
    QTextBrowser, QWidget)
from . import resources_rc

class Ui_LogDialog(object):
    def setupUi(self, LogDialog):
        if not LogDialog.objectName():
            LogDialog.setObjectName(u"LogDialog")
        LogDialog.resize(719, 411)
        icon = QIcon()
        icon.addFile(u":/images/hard_drive_icon.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        LogDialog.setWindowIcon(icon)
        self.ok_button = QPushButton(LogDialog)
        self.ok_button.setObjectName(u"ok_button")
        self.ok_button.setGeometry(QRect(630, 380, 75, 24))
        self.log_textBrowser = QTextBrowser(LogDialog)
        self.log_textBrowser.setObjectName(u"log_textBrowser")
        self.log_textBrowser.setGeometry(QRect(10, 10, 701, 361))

        self.retranslateUi(LogDialog)

        QMetaObject.connectSlotsByName(LogDialog)
    # setupUi

    def retranslateUi(self, LogDialog):
        LogDialog.setWindowTitle(QCoreApplication.translate("LogDialog", u"HD Active Log", None))
        self.ok_button.setText(QCoreApplication.translate("LogDialog", u"Ok", None))
    # retranslateUi

