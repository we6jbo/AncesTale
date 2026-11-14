#pragma once
#include <QWidget>
#include <QJsonObject>
class QTableWidget; class QLineEdit; class QComboBox; class QLabel; class QPlainTextEdit;
class ContinuedResearchPanel : public QWidget {
public:
 explicit ContinuedResearchPanel(QWidget* parent=nullptr);
private:
 QTableWidget *table; QLineEdit *search; QComboBox *filter; QLabel *status; QPlainTextEdit *detail;
 QJsonObject data; QByteArray snapshot; bool valid=false;
 void refresh(bool force=false); void render(); void copyPrompt(); void addPerson(); void resolve(bool resolved);
 bool save(const QJsonObject& next); QList<int> selected() const;
};
