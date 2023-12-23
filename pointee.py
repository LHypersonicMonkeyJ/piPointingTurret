# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pointee.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Pointee(object):
    def setupUi(self, Pointee):
        Pointee.setObjectName("Pointee")
        Pointee.resize(900, 600)
        self.groupBox = QtWidgets.QGroupBox(Pointee)
        self.groupBox.setGeometry(QtCore.QRect(490, 400, 301, 91))
        self.groupBox.setObjectName("groupBox")
        self.layoutWidget = QtWidgets.QWidget(self.groupBox)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 20, 194, 19))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.label_roomTemp = QtWidgets.QLabel(self.layoutWidget)
        self.label_roomTemp.setObjectName("label_roomTemp")
        self.horizontalLayout_2.addWidget(self.label_roomTemp)
        self.label_currentDate = QtWidgets.QLabel(Pointee)
        self.label_currentDate.setGeometry(QtCore.QRect(710, 10, 81, 17))
        self.label_currentDate.setObjectName("label_currentDate")
        self.label_currentTime = QtWidgets.QLabel(Pointee)
        self.label_currentTime.setGeometry(QtCore.QRect(10, 10, 61, 17))
        self.label_currentTime.setObjectName("label_currentTime")
        self.layoutWidget1 = QtWidgets.QWidget(Pointee)
        self.layoutWidget1.setGeometry(QtCore.QRect(40, 290, 701, 71))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(20)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.button_Start = QtWidgets.QPushButton(self.layoutWidget1)
        self.button_Start.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.button_Start.setFont(font)
        self.button_Start.setObjectName("button_Start")
        self.horizontalLayout_4.addWidget(self.button_Start)
        self.button_Pause = QtWidgets.QPushButton(self.layoutWidget1)
        self.button_Pause.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.button_Pause.setFont(font)
        self.button_Pause.setObjectName("button_Pause")
        self.horizontalLayout_4.addWidget(self.button_Pause)
        self.button_Resume = QtWidgets.QPushButton(self.layoutWidget1)
        self.button_Resume.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.button_Resume.setFont(font)
        self.button_Resume.setObjectName("button_Resume")
        self.horizontalLayout_4.addWidget(self.button_Resume)
        self.button_Stop = QtWidgets.QPushButton(self.layoutWidget1)
        self.button_Stop.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.button_Stop.setFont(font)
        self.button_Stop.setObjectName("button_Stop")
        self.horizontalLayout_4.addWidget(self.button_Stop)
        self.label_4 = QtWidgets.QLabel(Pointee)
        self.label_4.setGeometry(QtCore.QRect(330, 30, 121, 31))
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.layoutWidget2 = QtWidgets.QWidget(Pointee)
        self.layoutWidget2.setGeometry(QtCore.QRect(40, 70, 701, 71))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget2)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.target_Sun = QtWidgets.QPushButton(self.layoutWidget2)
        self.target_Sun.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.target_Sun.sizePolicy().hasHeightForWidth())
        self.target_Sun.setSizePolicy(sizePolicy)
        self.target_Sun.setMinimumSize(QtCore.QSize(0, 40))
        self.target_Sun.setBaseSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.target_Sun.setFont(font)
        self.target_Sun.setIconSize(QtCore.QSize(16, 16))
        self.target_Sun.setObjectName("target_Sun")
        self.horizontalLayout.addWidget(self.target_Sun)
        self.target_Moon = QtWidgets.QPushButton(self.layoutWidget2)
        self.target_Moon.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.target_Moon.setFont(font)
        self.target_Moon.setIconSize(QtCore.QSize(20, 4))
        self.target_Moon.setObjectName("target_Moon")
        self.horizontalLayout.addWidget(self.target_Moon)
        self.target_Mars = QtWidgets.QPushButton(self.layoutWidget2)
        self.target_Mars.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.target_Mars.setFont(font)
        self.target_Mars.setObjectName("target_Mars")
        self.horizontalLayout.addWidget(self.target_Mars)
        self.target_ISS = QtWidgets.QPushButton(self.layoutWidget2)
        self.target_ISS.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.target_ISS.setFont(font)
        self.target_ISS.setObjectName("target_ISS")
        self.horizontalLayout.addWidget(self.target_ISS)
        self.layoutWidget3 = QtWidgets.QWidget(Pointee)
        self.layoutWidget3.setGeometry(QtCore.QRect(200, 180, 371, 71))
        self.layoutWidget3.setObjectName("layoutWidget3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.layoutWidget3)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(20)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.button_MotorsOff = QtWidgets.QPushButton(self.layoutWidget3)
        self.button_MotorsOff.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.button_MotorsOff.setFont(font)
        self.button_MotorsOff.setObjectName("button_MotorsOff")
        self.horizontalLayout_3.addWidget(self.button_MotorsOff)
        self.button_MotorsOn = QtWidgets.QPushButton(self.layoutWidget3)
        self.button_MotorsOn.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.button_MotorsOn.setFont(font)
        self.button_MotorsOn.setObjectName("button_MotorsOn")
        self.horizontalLayout_3.addWidget(self.button_MotorsOn)

        self.retranslateUi(Pointee)
        QtCore.QMetaObject.connectSlotsByName(Pointee)

    def retranslateUi(self, Pointee):
        _translate = QtCore.QCoreApplication.translate
        Pointee.setWindowTitle(_translate("Pointee", "Pointee"))
        self.groupBox.setTitle(_translate("Pointee", "Room:"))
        self.label.setText(_translate("Pointee", "Temperature:"))
        self.label_roomTemp.setText(_translate("Pointee", "Loading ... ..."))
        self.label_currentDate.setText(_translate("Pointee", "00/00/0000"))
        self.label_currentTime.setText(_translate("Pointee", "00:00:00"))
        self.button_Start.setText(_translate("Pointee", "Start"))
        self.button_Pause.setText(_translate("Pointee", "Pause"))
        self.button_Resume.setText(_translate("Pointee", "Resume"))
        self.button_Stop.setText(_translate("Pointee", "Stop"))
        self.label_4.setText(_translate("Pointee", "Targets"))
        self.target_Sun.setText(_translate("Pointee", "Sun"))
        self.target_Moon.setText(_translate("Pointee", "Moon"))
        self.target_Mars.setText(_translate("Pointee", "Mars"))
        self.target_ISS.setText(_translate("Pointee", "ISS"))
        self.button_MotorsOff.setText(_translate("Pointee", "Motors Off"))
        self.button_MotorsOn.setText(_translate("Pointee", "Motors On"))
