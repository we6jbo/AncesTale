#pragma once
#include <QMainWindow>
#include <QJsonArray>
class QTableWidget;
class QLabel;
class QPushButton;
class MainWindow: public QMainWindow {
public:
 explicit MainWindow(QWidget* parent=nullptr);
private:
 QTableWidget* table_=nullptr;
 QLabel* status_=nullptr;
 QPushButton* prepare_=nullptr;
 QJsonArray records_;
 bool signedDataReady_=false;
 void prepareResearch();
 void takeScreenshot();
 bool verifyAndLoad();
};
