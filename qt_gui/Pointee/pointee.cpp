#include "pointee.h"
#include "ui_pointee.h"

Pointee::Pointee(QWidget *parent)
    : QWidget(parent)
    , ui(new Ui::Pointee)
{
    ui->setupUi(this);
}

Pointee::~Pointee()
{
    delete ui;
}

