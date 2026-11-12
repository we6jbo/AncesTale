#pragma once
#include <QMainWindow>
class QTableWidget;
class MainWindow: public QMainWindow {
public:
  explicit MainWindow(QWidget* parent=nullptr);
private:
  QTableWidget* table_;
};
