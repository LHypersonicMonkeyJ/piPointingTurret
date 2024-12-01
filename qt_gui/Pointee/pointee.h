#ifndef POINTEE_H
#define POINTEE_H

#include <QWidget>

QT_BEGIN_NAMESPACE
namespace Ui { class Pointee; }
QT_END_NAMESPACE

class Pointee : public QWidget
{
    Q_OBJECT

public:
    Pointee(QWidget *parent = nullptr);
    ~Pointee();

private:
    Ui::Pointee *ui;
};
#endif // POINTEE_H
