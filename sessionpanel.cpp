#include "sessionpanel.h"
#include <QLabel>
#include <QTextEdit>
#include <QLineEdit>
#include <QPushButton>
#include <QVBoxLayout>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QNetworkRequest>
#include <QMediaPlayer>
#include <QAudioOutput>
#include <QTimer>
#include <QFile>
#include <QFileInfo>
#include <QDir>
#include <QJsonDocument>
#include <QCryptographicHash>
#include <QRegularExpression>
#include <QUrl>
#include <QDateTime>
#include <QApplication>
#include <QStringList>
#include <QClipboard>
#include <QSaveFile>
namespace {const QString root="/home/we6jbo/Projects/AncesTale"; const QString local=root+"/.session-local";}
SessionPanel::SessionPanel(QWidget* parent):QWidget(parent){
 auto* l=new QVBoxLayout(this);status_=new QLabel("Not connected. Arm to enable audio.");countdown_=new QLabel("--:--");song_=new QLabel("No session");
 for(auto* x:{status_,countdown_,song_}){x->setTextFormat(Qt::PlainText);x->setWordWrap(true);l->addWidget(x);}
 url_=new QLineEdit("http://192.168.5.215:8081/nov-game/ancestale-session.json");url_->setReadOnly(true);l->addWidget(url_);
 auto* arm=new QPushButton("Arm session audio");l->addWidget(arm);auto* stop=new QPushButton("Disarm audio");l->addWidget(stop);l->addStretch();
 blog_=new QWidget;auto* b=new QVBoxLayout(blog_);auto* note=new QLabel("Local drafts only. Review before publishing.");b->addWidget(note);draft_=new QTextEdit;draft_->setReadOnly(true);b->addWidget(draft_);auto* copy=new QPushButton("Copy draft");b->addWidget(copy);connect(copy,&QPushButton::clicked,this,[this]{QApplication::clipboard()->setText(draft_->toPlainText());});
 net_=new QNetworkAccessManager(this);player_=new QMediaPlayer(this);chime_=new QMediaPlayer(this);audio_=new QAudioOutput(this);chimeAudio_=new QAudioOutput(this);player_->setAudioOutput(audio_);chime_->setAudioOutput(chimeAudio_);audio_->setVolume(.65);chimeAudio_->setVolume(.6);
 connect(arm,&QPushButton::clicked,this,[this]{armed_=true;status_->setText("Audio armed; waiting for session");tick();});connect(stop,&QPushButton::clicked,this,[this]{armed_=false;player_->stop();chime_->stop();active_.clear();status_->setText("Audio disarmed");});
 connect(player_,&QMediaPlayer::playbackStateChanged,this,[this](QMediaPlayer::PlaybackState s){if(s==QMediaPlayer::PlayingState)log("Local music playback started: "+active_);});
 connect(player_,&QMediaPlayer::errorOccurred,this,[this](QMediaPlayer::Error,const QString& e){status_->setText("Audio error: "+e);log("Audio error: "+e);});
 timer_=new QTimer(this);timer_->setInterval(1000);connect(timer_,&QTimer::timeout,this,[this]{tick();loadDraft();static int n=0;if(++n%3==0)poll();});timer_->start();poll();
}
void SessionPanel::log(const QString& s){if(!QDir().mkpath(local))return;QFile f(local+"/session.log");if(f.open(QIODevice::Append))f.write((QDateTime::currentDateTimeUtc().toString(Qt::ISODate)+" "+s+"\n").toUtf8());}
void SessionPanel::poll(){if(busy_)return;busy_=true;QNetworkRequest req{QUrl(url_->text())};req.setTransferTimeout(2500);req.setAttribute(QNetworkRequest::RedirectPolicyAttribute,QNetworkRequest::ManualRedirectPolicy);req.setRawHeader("Cache-Control","no-cache");auto* r=net_->get(req);connect(r,&QNetworkReply::readyRead,this,[r]{if(r->bytesAvailable()>65536)r->abort();});connect(r,&QNetworkReply::finished,this,[this,r]{busy_=false;auto bytes=r->readAll();if(r->error()==QNetworkReply::NoError&&bytes.size()<=65536){auto d=QJsonDocument::fromJson(bytes);auto o=d.object();auto id=o.value("id").toString();auto start=QDateTime::fromString(o.value("start").toString(),Qt::ISODate);auto end=QDateTime::fromString(o.value("end").toString(),Qt::ISODate);auto file=o.value("file").toString();if(o.value("schema").toString()=="ancestale.session.v1"&&QRegularExpression("^[A-Za-z0-9_-]{1,80}$").match(id).hasMatch()&&start.isValid()&&end.isValid()&&start.secsTo(end)==600&&QRegularExpression("^[A-Za-z0-9][A-Za-z0-9_. -]{0,150}\\.(mp3|ogg|wav|flac|m4a)$",QRegularExpression::CaseInsensitiveOption).match(file).hasMatch()&&!file.contains("..")){QFile approved(local+"/ancestale-session.json");if(approved.open(QIODevice::ReadOnly)&&approved.size()<=65536&&QJsonDocument::fromJson(approved.readAll()).object()==o){state_=o;lastOk_=QDateTime::currentSecsSinceEpoch();}else{status_->setText("Remote session has not been locally approved");}}}r->deleteLater();tick();});}
void SessionPanel::tick(){if(state_.isEmpty())return;auto now=QDateTime::currentDateTimeUtc();auto start=QDateTime::fromString(state_.value("start").toString(),Qt::ISODate);auto end=QDateTime::fromString(state_.value("end").toString(),Qt::ISODate);QString id=state_.value("id").toString();qint64 left=now.secsTo(end);if(now>=end){countdown_->setText("00:00 — Session ended");player_->stop();if(armed_&&active_==id&&ended_!=id){ended_=id;chime_->setSource(QUrl::fromLocalFile(root+"/session/chime.wav"));chime_->play();log("Session ended: "+id);}active_.clear();return;}if(now.toSecsSinceEpoch()-lastOk_>15){player_->stop();active_.clear();status_->setText("Connection stale; audio stopped");return;}countdown_->setText(QString("%1:%2 remaining").arg(left/60,2,10,QChar('0')).arg(left%60,2,10,QChar('0')));song_->setText(state_.value("title").toString()+" | "+state_.value("license").toString()+"\nWebsite requested track: 192.168.5.215:8081 (browser playback not independently verified)");if(now<start){player_->stop();active_.clear();countdown_->setText("Starts at "+start.toLocalTime().toString("hh:mm:ss"));return;}if(!armed_)return;if(active_!=id){player_->stop();auto path=root+"/Music/"+state_.value("file").toString();QFileInfo f(path);if(!f.isFile()||f.isSymLink()||f.canonicalPath()!=QFileInfo(root+"/Music").absoluteFilePath()){status_->setText("Missing or unsafe local music file");return;}QFile track(path);QCryptographicHash digest(QCryptographicHash::Sha256);if(!track.open(QIODevice::ReadOnly)||!digest.addData(&track)||QString::fromLatin1(digest.result().toHex())!=state_.value("sha256").toString()){status_->setText("Local track hash mismatch");return;}active_=id;player_->setSource(QUrl::fromLocalFile(path));player_->setLoops(QMediaPlayer::Infinite);player_->play();status_->setText("Local playback requested; see player state");}}
void SessionPanel::loadDraft(){QFile f(local+"/blog.json");if(!f.open(QIODevice::ReadOnly)||f.size()>131072)return;auto bytes=f.readAll();auto d=QJsonDocument::fromJson(bytes);auto o=d.object();if(o.value("session_id").toString()!=state_.value("id").toString()||o.value("session_id").toString().isEmpty())return;QString text;for(const auto& key:{"title","blog","facebook","linkedin","speech"}){auto v=o.value(key).toString();if(v.isEmpty())return;text+=QString::fromLatin1(key).toUpper()+"\n"+v+"\n\n";}if(text!=loadedDraft_){loadedDraft_=text;draft_->setPlainText(text);}}
