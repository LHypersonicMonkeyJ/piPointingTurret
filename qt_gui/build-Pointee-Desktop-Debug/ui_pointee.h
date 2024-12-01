/********************************************************************************
** Form generated from reading UI file 'pointee.ui'
**
** Created by: Qt User Interface Compiler version 5.15.3
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_POINTEE_H
#define UI_POINTEE_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QGroupBox>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QLabel>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_Pointee
{
public:
    QGroupBox *groupBox;
    QWidget *layoutWidget;
    QHBoxLayout *horizontalLayout_2;
    QLabel *label;
    QLabel *label_roomTemp;
    QWidget *horizontalLayoutWidget_3;
    QHBoxLayout *horizontalLayout_8;
    QLabel *label_7;
    QLabel *label_roomHumidity;
    QLabel *label_currentDate;
    QLabel *label_currentTime;
    QWidget *layoutWidget1;
    QHBoxLayout *horizontalLayout_4;
    QPushButton *button_Start;
    QPushButton *button_Pause;
    QPushButton *button_Resume;
    QPushButton *button_Stop;
    QLabel *label_4;
    QWidget *layoutWidget2;
    QHBoxLayout *horizontalLayout;
    QPushButton *target_Sun;
    QPushButton *target_Moon;
    QPushButton *target_Mars;
    QPushButton *target_ISS;
    QWidget *layoutWidget3;
    QHBoxLayout *horizontalLayout_3;
    QPushButton *button_MotorsOff;
    QPushButton *button_MotorsOn;
    QGroupBox *groupBox_2;
    QWidget *layoutWidget_2;
    QHBoxLayout *horizontalLayout_5;
    QLabel *label_2;
    QLabel *label_outdoorTemp;
    QWidget *horizontalLayoutWidget;
    QHBoxLayout *horizontalLayout_6;
    QLabel *label_5;
    QLabel *label_outdoorMaxTemp;
    QLabel *label_3;
    QLabel *label_outdoorMinTemp;
    QWidget *horizontalLayoutWidget_2;
    QHBoxLayout *horizontalLayout_7;
    QLabel *label_6;
    QLabel *label_outdoorHumidity;
    QPushButton *ExitButton;

    void setupUi(QWidget *Pointee)
    {
        if (Pointee->objectName().isEmpty())
            Pointee->setObjectName(QString::fromUtf8("Pointee"));
        Pointee->resize(804, 505);
        Pointee->setStyleSheet(QString::fromUtf8("background-color: rgb(61, 56, 70);"));
        groupBox = new QGroupBox(Pointee);
        groupBox->setObjectName(QString::fromUtf8("groupBox"));
        groupBox->setGeometry(QRect(440, 400, 351, 91));
        groupBox->setStyleSheet(QString::fromUtf8("color: rgb(220, 138, 221);"));
        layoutWidget = new QWidget(groupBox);
        layoutWidget->setObjectName(QString::fromUtf8("layoutWidget"));
        layoutWidget->setGeometry(QRect(10, 30, 194, 19));
        horizontalLayout_2 = new QHBoxLayout(layoutWidget);
        horizontalLayout_2->setObjectName(QString::fromUtf8("horizontalLayout_2"));
        horizontalLayout_2->setContentsMargins(0, 0, 0, 0);
        label = new QLabel(layoutWidget);
        label->setObjectName(QString::fromUtf8("label"));
        label->setStyleSheet(QString::fromUtf8("color: rgb(220, 138, 221);"));

        horizontalLayout_2->addWidget(label);

        label_roomTemp = new QLabel(layoutWidget);
        label_roomTemp->setObjectName(QString::fromUtf8("label_roomTemp"));
        label_roomTemp->setStyleSheet(QString::fromUtf8("color: rgb(220, 138, 221);"));

        horizontalLayout_2->addWidget(label_roomTemp);

        horizontalLayoutWidget_3 = new QWidget(groupBox);
        horizontalLayoutWidget_3->setObjectName(QString::fromUtf8("horizontalLayoutWidget_3"));
        horizontalLayoutWidget_3->setGeometry(QRect(10, 50, 162, 21));
        horizontalLayout_8 = new QHBoxLayout(horizontalLayoutWidget_3);
        horizontalLayout_8->setObjectName(QString::fromUtf8("horizontalLayout_8"));
        horizontalLayout_8->setContentsMargins(0, 0, 0, 0);
        label_7 = new QLabel(horizontalLayoutWidget_3);
        label_7->setObjectName(QString::fromUtf8("label_7"));
        label_7->setStyleSheet(QString::fromUtf8("color: rgb(220, 138, 221);"));

        horizontalLayout_8->addWidget(label_7);

        label_roomHumidity = new QLabel(horizontalLayoutWidget_3);
        label_roomHumidity->setObjectName(QString::fromUtf8("label_roomHumidity"));
        label_roomHumidity->setStyleSheet(QString::fromUtf8("color: rgb(220, 138, 221);"));

        horizontalLayout_8->addWidget(label_roomHumidity);

        label_currentDate = new QLabel(Pointee);
        label_currentDate->setObjectName(QString::fromUtf8("label_currentDate"));
        label_currentDate->setGeometry(QRect(10, 30, 81, 17));
        label_currentDate->setStyleSheet(QString::fromUtf8("color: rgb(220, 138, 221);"));
        label_currentTime = new QLabel(Pointee);
        label_currentTime->setObjectName(QString::fromUtf8("label_currentTime"));
        label_currentTime->setGeometry(QRect(10, 10, 61, 17));
        label_currentTime->setStyleSheet(QString::fromUtf8("color: rgb(220, 138, 221);"));
        layoutWidget1 = new QWidget(Pointee);
        layoutWidget1->setObjectName(QString::fromUtf8("layoutWidget1"));
        layoutWidget1->setGeometry(QRect(40, 290, 701, 71));
        horizontalLayout_4 = new QHBoxLayout(layoutWidget1);
        horizontalLayout_4->setSpacing(20);
        horizontalLayout_4->setObjectName(QString::fromUtf8("horizontalLayout_4"));
        horizontalLayout_4->setContentsMargins(0, 0, 0, 0);
        button_Start = new QPushButton(layoutWidget1);
        button_Start->setObjectName(QString::fromUtf8("button_Start"));
        button_Start->setMinimumSize(QSize(0, 40));
        QFont font;
        font.setPointSize(16);
        font.setBold(true);
        font.setWeight(75);
        button_Start->setFont(font);
        button_Start->setStyleSheet(QString::fromUtf8("background-color: rgb(222, 221, 218);"));

        horizontalLayout_4->addWidget(button_Start);

        button_Pause = new QPushButton(layoutWidget1);
        button_Pause->setObjectName(QString::fromUtf8("button_Pause"));
        button_Pause->setMinimumSize(QSize(0, 40));
        button_Pause->setFont(font);
        button_Pause->setStyleSheet(QString::fromUtf8("background-color: rgb(222, 221, 218);"));

        horizontalLayout_4->addWidget(button_Pause);

        button_Resume = new QPushButton(layoutWidget1);
        button_Resume->setObjectName(QString::fromUtf8("button_Resume"));
        button_Resume->setMinimumSize(QSize(0, 40));
        button_Resume->setFont(font);
        button_Resume->setStyleSheet(QString::fromUtf8("background-color: rgb(222, 221, 218);"));

        horizontalLayout_4->addWidget(button_Resume);

        button_Stop = new QPushButton(layoutWidget1);
        button_Stop->setObjectName(QString::fromUtf8("button_Stop"));
        button_Stop->setMinimumSize(QSize(0, 40));
        button_Stop->setFont(font);
        button_Stop->setStyleSheet(QString::fromUtf8("background-color: rgb(222, 221, 218);"));

        horizontalLayout_4->addWidget(button_Stop);

        label_4 = new QLabel(Pointee);
        label_4->setObjectName(QString::fromUtf8("label_4"));
        label_4->setGeometry(QRect(330, 30, 121, 31));
        QFont font1;
        font1.setPointSize(24);
        font1.setBold(true);
        font1.setWeight(75);
        label_4->setFont(font1);
        label_4->setStyleSheet(QString::fromUtf8("color: rgb(220, 138, 221);"));
        layoutWidget2 = new QWidget(Pointee);
        layoutWidget2->setObjectName(QString::fromUtf8("layoutWidget2"));
        layoutWidget2->setGeometry(QRect(40, 70, 701, 71));
        horizontalLayout = new QHBoxLayout(layoutWidget2);
        horizontalLayout->setSpacing(20);
        horizontalLayout->setObjectName(QString::fromUtf8("horizontalLayout"));
        horizontalLayout->setContentsMargins(0, 0, 0, 0);
        target_Sun = new QPushButton(layoutWidget2);
        target_Sun->setObjectName(QString::fromUtf8("target_Sun"));
        target_Sun->setEnabled(true);
        QSizePolicy sizePolicy(QSizePolicy::Minimum, QSizePolicy::Fixed);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(target_Sun->sizePolicy().hasHeightForWidth());
        target_Sun->setSizePolicy(sizePolicy);
        target_Sun->setMinimumSize(QSize(0, 40));
        target_Sun->setBaseSize(QSize(0, 0));
        target_Sun->setFont(font);
        target_Sun->setStyleSheet(QString::fromUtf8("background-color: rgb(222, 221, 218);"));
        target_Sun->setIconSize(QSize(16, 16));

        horizontalLayout->addWidget(target_Sun);

        target_Moon = new QPushButton(layoutWidget2);
        target_Moon->setObjectName(QString::fromUtf8("target_Moon"));
        target_Moon->setMinimumSize(QSize(0, 40));
        target_Moon->setFont(font);
        target_Moon->setStyleSheet(QString::fromUtf8("background-color: rgb(222, 221, 218);"));
        target_Moon->setIconSize(QSize(20, 4));

        horizontalLayout->addWidget(target_Moon);

        target_Mars = new QPushButton(layoutWidget2);
        target_Mars->setObjectName(QString::fromUtf8("target_Mars"));
        target_Mars->setMinimumSize(QSize(0, 40));
        target_Mars->setFont(font);
        target_Mars->setStyleSheet(QString::fromUtf8("background-color: rgb(222, 221, 218);"));

        horizontalLayout->addWidget(target_Mars);

        target_ISS = new QPushButton(layoutWidget2);
        target_ISS->setObjectName(QString::fromUtf8("target_ISS"));
        target_ISS->setMinimumSize(QSize(0, 40));
        target_ISS->setFont(font);
        target_ISS->setStyleSheet(QString::fromUtf8("background-color: rgb(222, 221, 218);"));

        horizontalLayout->addWidget(target_ISS);

        layoutWidget3 = new QWidget(Pointee);
        layoutWidget3->setObjectName(QString::fromUtf8("layoutWidget3"));
        layoutWidget3->setGeometry(QRect(200, 180, 371, 71));
        horizontalLayout_3 = new QHBoxLayout(layoutWidget3);
        horizontalLayout_3->setSpacing(20);
        horizontalLayout_3->setObjectName(QString::fromUtf8("horizontalLayout_3"));
        horizontalLayout_3->setContentsMargins(0, 0, 0, 0);
        button_MotorsOff = new QPushButton(layoutWidget3);
        button_MotorsOff->setObjectName(QString::fromUtf8("button_MotorsOff"));
        button_MotorsOff->setMinimumSize(QSize(0, 40));
        button_MotorsOff->setFont(font);
        button_MotorsOff->setStyleSheet(QString::fromUtf8("background-color: rgb(222, 221, 218);"));

        horizontalLayout_3->addWidget(button_MotorsOff);

        button_MotorsOn = new QPushButton(layoutWidget3);
        button_MotorsOn->setObjectName(QString::fromUtf8("button_MotorsOn"));
        button_MotorsOn->setMinimumSize(QSize(0, 40));
        button_MotorsOn->setFont(font);
        button_MotorsOn->setStyleSheet(QString::fromUtf8("background-color: rgb(222, 221, 218);"));

        horizontalLayout_3->addWidget(button_MotorsOn);

        groupBox_2 = new QGroupBox(Pointee);
        groupBox_2->setObjectName(QString::fromUtf8("groupBox_2"));
        groupBox_2->setGeometry(QRect(20, 400, 351, 101));
        groupBox_2->setStyleSheet(QString::fromUtf8("color: rgb(220, 138, 221);"));
        layoutWidget_2 = new QWidget(groupBox_2);
        layoutWidget_2->setObjectName(QString::fromUtf8("layoutWidget_2"));
        layoutWidget_2->setGeometry(QRect(10, 30, 194, 19));
        horizontalLayout_5 = new QHBoxLayout(layoutWidget_2);
        horizontalLayout_5->setObjectName(QString::fromUtf8("horizontalLayout_5"));
        horizontalLayout_5->setContentsMargins(0, 0, 0, 0);
        label_2 = new QLabel(layoutWidget_2);
        label_2->setObjectName(QString::fromUtf8("label_2"));
        label_2->setStyleSheet(QString::fromUtf8("color: rgb(220, 138, 221);"));

        horizontalLayout_5->addWidget(label_2);

        label_outdoorTemp = new QLabel(layoutWidget_2);
        label_outdoorTemp->setObjectName(QString::fromUtf8("label_outdoorTemp"));
        label_outdoorTemp->setStyleSheet(QString::fromUtf8("color: rgb(220, 138, 221);"));

        horizontalLayout_5->addWidget(label_outdoorTemp);

        horizontalLayoutWidget = new QWidget(groupBox_2);
        horizontalLayoutWidget->setObjectName(QString::fromUtf8("horizontalLayoutWidget"));
        horizontalLayoutWidget->setGeometry(QRect(10, 50, 332, 20));
        horizontalLayout_6 = new QHBoxLayout(horizontalLayoutWidget);
        horizontalLayout_6->setObjectName(QString::fromUtf8("horizontalLayout_6"));
        horizontalLayout_6->setContentsMargins(0, 0, 0, 0);
        label_5 = new QLabel(horizontalLayoutWidget);
        label_5->setObjectName(QString::fromUtf8("label_5"));

        horizontalLayout_6->addWidget(label_5);

        label_outdoorMaxTemp = new QLabel(horizontalLayoutWidget);
        label_outdoorMaxTemp->setObjectName(QString::fromUtf8("label_outdoorMaxTemp"));
        label_outdoorMaxTemp->setStyleSheet(QString::fromUtf8("color: rgb(220, 138, 221);"));

        horizontalLayout_6->addWidget(label_outdoorMaxTemp);

        label_3 = new QLabel(horizontalLayoutWidget);
        label_3->setObjectName(QString::fromUtf8("label_3"));

        horizontalLayout_6->addWidget(label_3);

        label_outdoorMinTemp = new QLabel(horizontalLayoutWidget);
        label_outdoorMinTemp->setObjectName(QString::fromUtf8("label_outdoorMinTemp"));
        label_outdoorMinTemp->setStyleSheet(QString::fromUtf8("color: rgb(220, 138, 221);"));

        horizontalLayout_6->addWidget(label_outdoorMinTemp);

        horizontalLayoutWidget_2 = new QWidget(groupBox_2);
        horizontalLayoutWidget_2->setObjectName(QString::fromUtf8("horizontalLayoutWidget_2"));
        horizontalLayoutWidget_2->setGeometry(QRect(10, 70, 162, 21));
        horizontalLayout_7 = new QHBoxLayout(horizontalLayoutWidget_2);
        horizontalLayout_7->setObjectName(QString::fromUtf8("horizontalLayout_7"));
        horizontalLayout_7->setContentsMargins(0, 0, 0, 0);
        label_6 = new QLabel(horizontalLayoutWidget_2);
        label_6->setObjectName(QString::fromUtf8("label_6"));
        label_6->setStyleSheet(QString::fromUtf8("color: rgb(220, 138, 221);"));

        horizontalLayout_7->addWidget(label_6);

        label_outdoorHumidity = new QLabel(horizontalLayoutWidget_2);
        label_outdoorHumidity->setObjectName(QString::fromUtf8("label_outdoorHumidity"));
        label_outdoorHumidity->setStyleSheet(QString::fromUtf8("color: rgb(220, 138, 221);"));

        horizontalLayout_7->addWidget(label_outdoorHumidity);

        ExitButton = new QPushButton(Pointee);
        ExitButton->setObjectName(QString::fromUtf8("ExitButton"));
        ExitButton->setGeometry(QRect(780, 10, 20, 20));
        ExitButton->setStyleSheet(QString::fromUtf8("border-radius: 10px; \n"
"background-color: rgb(255, 0, 0);"));

        retranslateUi(Pointee);

        QMetaObject::connectSlotsByName(Pointee);
    } // setupUi

    void retranslateUi(QWidget *Pointee)
    {
        Pointee->setWindowTitle(QCoreApplication::translate("Pointee", "Pointee", nullptr));
        groupBox->setTitle(QCoreApplication::translate("Pointee", "Room:", nullptr));
        label->setText(QCoreApplication::translate("Pointee", "Temperature:", nullptr));
        label_roomTemp->setText(QCoreApplication::translate("Pointee", "Loading ... ...", nullptr));
        label_7->setText(QCoreApplication::translate("Pointee", "Humidity: ", nullptr));
        label_roomHumidity->setText(QCoreApplication::translate("Pointee", "Loading ... ...", nullptr));
        label_currentDate->setText(QCoreApplication::translate("Pointee", "00/00/0000", nullptr));
        label_currentTime->setText(QCoreApplication::translate("Pointee", "00:00:00", nullptr));
        button_Start->setText(QCoreApplication::translate("Pointee", "Start", nullptr));
        button_Pause->setText(QCoreApplication::translate("Pointee", "Pause", nullptr));
        button_Resume->setText(QCoreApplication::translate("Pointee", "Resume", nullptr));
        button_Stop->setText(QCoreApplication::translate("Pointee", "Stop", nullptr));
        label_4->setText(QCoreApplication::translate("Pointee", "Targets", nullptr));
        target_Sun->setText(QCoreApplication::translate("Pointee", "Sun", nullptr));
        target_Moon->setText(QCoreApplication::translate("Pointee", "Moon", nullptr));
        target_Mars->setText(QCoreApplication::translate("Pointee", "Mars", nullptr));
        target_ISS->setText(QCoreApplication::translate("Pointee", "ISS", nullptr));
        button_MotorsOff->setText(QCoreApplication::translate("Pointee", "Motors Off", nullptr));
        button_MotorsOn->setText(QCoreApplication::translate("Pointee", "Motors On", nullptr));
        groupBox_2->setTitle(QCoreApplication::translate("Pointee", "Outdoor:", nullptr));
        label_2->setText(QCoreApplication::translate("Pointee", "Temperature:", nullptr));
        label_outdoorTemp->setText(QCoreApplication::translate("Pointee", "Loading ... ...", nullptr));
        label_5->setText(QCoreApplication::translate("Pointee", "Daily Max:", nullptr));
        label_outdoorMaxTemp->setText(QCoreApplication::translate("Pointee", "Loading ... ...", nullptr));
        label_3->setText(QCoreApplication::translate("Pointee", "Daily Min:", nullptr));
        label_outdoorMinTemp->setText(QCoreApplication::translate("Pointee", "Loading ... ...", nullptr));
        label_6->setText(QCoreApplication::translate("Pointee", "Humidity: ", nullptr));
        label_outdoorHumidity->setText(QCoreApplication::translate("Pointee", "Loading ... ...", nullptr));
        ExitButton->setText(QCoreApplication::translate("Pointee", "X", nullptr));
    } // retranslateUi

};

namespace Ui {
    class Pointee: public Ui_Pointee {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_POINTEE_H
