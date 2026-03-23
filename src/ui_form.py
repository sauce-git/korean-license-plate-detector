# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLayout,
                               QPushButton, QSizePolicy, QTextEdit, QVBoxLayout,
                               QWidget, QLineEdit)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(800, 600)
        self.verticalLayoutWidget = QWidget(Widget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, 0, 101, 461))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setSpacing(50)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(0, 50, 0, 50)
        self.chooseDir = QPushButton(self.verticalLayoutWidget)
        self.chooseDir.setObjectName(u"chooseDir")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chooseDir.sizePolicy().hasHeightForWidth())
        self.chooseDir.setSizePolicy(sizePolicy)
        self.chooseDir.setMinimumSize(QSize(0, 50))

        self.verticalLayout.addWidget(self.chooseDir)

        self.chooseFile = QPushButton(self.verticalLayoutWidget)
        self.chooseFile.setObjectName(u"chooseFile")
        sizePolicy.setHeightForWidth(self.chooseFile.sizePolicy().hasHeightForWidth())
        self.chooseFile.setSizePolicy(sizePolicy)
        self.chooseFile.setMinimumSize(QSize(0, 50))

        self.verticalLayout.addWidget(self.chooseFile)

        self.execute = QPushButton(self.verticalLayoutWidget)
        self.execute.setObjectName(u"execute")
        sizePolicy.setHeightForWidth(self.execute.sizePolicy().hasHeightForWidth())
        self.execute.setSizePolicy(sizePolicy)
        self.execute.setMinimumSize(QSize(0, 50))

        self.verticalLayout.addWidget(self.execute)

        self.verticalLayoutWidget_2 = QWidget(Widget)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(100, 0, 701, 461))
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.Image = QLabel(self.verticalLayoutWidget_2)
        self.Image.setObjectName(u"Image")
        self.Image.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.Image)

        self.verticalLayoutWidget_3 = QWidget(Widget)
        self.verticalLayoutWidget_3.setObjectName(u"verticalLayoutWidget_3")
        self.verticalLayoutWidget_3.setGeometry(QRect(640, 460, 160, 141))
        self.verticalLayout_3 = QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.confirm = QPushButton(self.verticalLayoutWidget_3)
        self.confirm.setObjectName(u"confirm")

        self.verticalLayout_3.addWidget(self.confirm)

        self.horizontalLayoutWidget = QWidget(Widget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(0, 460, 361, 141))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.horizontalLayoutWidget)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.label.setMargin(10)

        self.horizontalLayout.addWidget(self.label)

        self.car_num = QLineEdit(Widget)
        self.car_num.setObjectName(u"car_num")
        self.car_num.setGeometry(QRect(400, 510, 201, 41))
        self.label_2 = QLabel(Widget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(400, 480, 58, 16))
#if QT_CONFIG(shortcut)
        self.label_2.setBuddy(self.car_num)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.chooseDir, self.chooseFile)
        QWidget.setTabOrder(self.chooseFile, self.execute)
        QWidget.setTabOrder(self.execute, self.confirm)
        QWidget.setTabOrder(self.confirm, self.car_num)

        self.retranslateUi(Widget)

        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"Widget", None))
        self.chooseDir.setText(QCoreApplication.translate("Widget", u"\ud3f4\ub354 \uc120\ud0dd", None))
        self.chooseFile.setText(QCoreApplication.translate("Widget", u"\ud30c\uc77c \uc120\ud0dd", None))
        self.execute.setText(QCoreApplication.translate("Widget", u"\ubcc0\ud658", None))
        self.Image.setText(QCoreApplication.translate("Widget", u"Image", None))
        self.confirm.setText(QCoreApplication.translate("Widget", u"\ud655\uc778", None))
        self.label.setText(QCoreApplication.translate("Widget", u"\ub300\uae30\uc911", None))
        self.label_2.setText(QCoreApplication.translate("Widget", u"&\ucc28\ub7c9\ubc88\ud638", None))
    # retranslateUi

