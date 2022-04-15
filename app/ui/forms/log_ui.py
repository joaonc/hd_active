# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'log.ui'
##
## Created by: Qt User Interface Compiler version 6.2.4
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

class Ui_log_dialog(object):
    def setupUi(self, log_dialog):
        if not log_dialog.objectName():
            log_dialog.setObjectName(u"log_dialog")
        log_dialog.resize(719, 411)
        self.ok_button = QPushButton(log_dialog)
        self.ok_button.setObjectName(u"ok_button")
        self.ok_button.setGeometry(QRect(630, 380, 75, 24))
        self.log_textBrowser = QTextBrowser(log_dialog)
        self.log_textBrowser.setObjectName(u"log_textBrowser")
        self.log_textBrowser.setGeometry(QRect(10, 10, 701, 361))

        self.retranslateUi(log_dialog)

        QMetaObject.connectSlotsByName(log_dialog)
    # setupUi

    def retranslateUi(self, log_dialog):
        log_dialog.setWindowTitle(QCoreApplication.translate("log_dialog", u"HD Active Log", None))
        self.ok_button.setText(QCoreApplication.translate("log_dialog", u"Ok", None))
    # retranslateUi
