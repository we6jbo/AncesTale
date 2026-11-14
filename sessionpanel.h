#pragma once
#include <QWidget>
#include <QJsonObject>
#include <QDateTime>
class QLabel; class QTextEdit; class QNetworkAccessManager; class QMediaPlayer; class QAudioOutput; class QTimer; class QLineEdit;
class SessionPanel : public QWidget {
public:
 explicit SessionPanel(QWidget* parent=nullptr);
 QWidget* blogTab() const { return blog_; }
private:
 QWidget* blog_; QTextEdit* draft_; QLabel *status_,*countdown_,*song_; QLineEdit* url_;
 QNetworkAccessManager* net_; QMediaPlayer *player_,*chime_; QAudioOutput *audio_,*chimeAudio_; QTimer* timer_;
 QJsonObject state_; QString active_,ended_,loadedDraft_; bool busy_=false,armed_=false; qint64 lastOk_=0;
 void poll(); void tick(); void log(const QString&); void loadDraft();
};
