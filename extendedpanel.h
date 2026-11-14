#pragma once
#include <QWidget>
class QPlainTextEdit;
class QLabel;
class QProcess;
class ExtendedPanel : public QWidget {
public:
 explicit ExtendedPanel(QWidget* parent=nullptr);
private:
 QPlainTextEdit* view_; QLabel* status_; QProcess* process_;
 void reload(); void collect();
};
