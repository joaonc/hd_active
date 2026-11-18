# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'log_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QPlainTextEdit, QSizePolicy, QVBoxLayout, QWidget)
from . import resources_rc

class Ui_LogDialog(object):
    def setupUi(self, LogDialog):
        if not LogDialog.objectName():
            LogDialog.setObjectName(u"LogDialog")
        LogDialog.resize(720, 410)
        icon = QIcon()
        icon.addFile(u":/images/hard_drive_icon.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        LogDialog.setWindowIcon(icon)
        self.vertical_layout = QVBoxLayout(LogDialog)
        self.vertical_layout.setObjectName(u"vertical_layout")
        self.log_text_edit = QPlainTextEdit(LogDialog)
        self.log_text_edit.setObjectName(u"log_text_edit")
        self.log_text_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setMaximumBlockCount(1000)

        self.vertical_layout.addWidget(self.log_text_edit)

        self.button_box = QDialogButtonBox(LogDialog)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setStandardButtons(QDialogButtonBox.StandardButton.Close)

        self.vertical_layout.addWidget(self.button_box)


        self.retranslateUi(LogDialog)
        self.button_box.rejected.connect(LogDialog.reject)

        QMetaObject.connectSlotsByName(LogDialog)
    # setupUi

    def retranslateUi(self, LogDialog):
        LogDialog.setWindowTitle(QCoreApplication.translate("LogDialog", u"HD Active Log", None))
    # retranslateUi

