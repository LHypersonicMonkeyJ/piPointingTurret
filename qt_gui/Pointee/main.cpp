#include "pointee.h"

#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    Pointee w;
    w.show();
    return a.exec();
}
