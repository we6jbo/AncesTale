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
#include <QProcess>
#include <QMessageBox>
#include <QDesktopServices>
#include <QTimeZone>
#include <QMediaDevices>
#include <QAudioDevice>
namespace {const QString root="/home/we6jbo/Projects/AncesTale"; const QString local=root+"/.session-local";}
SessionPanel::SessionPanel(QWidget* parent):QWidget(parent){
 auto* l=new QVBoxLayout(this);status_=new QLabel("Not connected. Arm to enable audio.");countdown_=new QLabel("--:--");song_=new QLabel("No session");
 for(auto* x:{status_,countdown_,song_}){x->setTextFormat(Qt::PlainText);x->setWordWrap(true);l->addWidget(x);}
 url_=new QLineEdit("http://192.168.5.215:8081/nov-game/ancestale-session.json");url_->setReadOnly(true);l->addWidget(url_);
 auto* arm=new QPushButton("Arm session audio");l->addWidget(arm);auto* stop=new QPushButton("Disarm audio");l->addWidget(stop);
 auto* takeover=new QPushButton("Activate emergency adventure (rails)");l->addWidget(takeover);
 auto* monitor=new QPushButton("Arm fallback monitor for today");l->addWidget(monitor);
 auto* cancel=new QPushButton("Disarm fallback monitor");l->addWidget(cancel);
 auto* recovery=new QLabel("Emergency mode: November 21–29 only; no automatic mail or Git operations.");recovery->setWordWrap(true);l->addWidget(recovery);
 auto* job=new QProcess(this);job->setWorkingDirectory(root);job->setProcessChannelMode(QProcess::MergedChannels);
 auto run=[=](const QString& arg){if(job->state()!=QProcess::NotRunning)return;job->start("python3",{root+"/fallback/controller.py",arg});};
 connect(job,&QProcess::finished,this,[=](int,QProcess::ExitStatus){auto t=QString::fromUtf8(job->readAll());if(!t.trimmed().isEmpty())recovery->setText(t.trimmed());});
 connect(takeover,&QPushButton::clicked,this,[=]{if(QMessageBox::question(this,"Emergency takeover","Replace the live game with today's prepared recovery chapter? Vibe must stop writing the live site. No mail or Git operation will run.")==QMessageBox::Yes)run("takeover");});
 connect(monitor,&QPushButton::clicked,this,[=]{if(QMessageBox::question(this,"Arm emergency monitor","Authorize today's fallback if the Vibe lease becomes stale for five minutes? The live Vibe workflow must use the lease. No email or Git operation will run.")==QMessageBox::Yes)run("arm");});
 connect(cancel,&QPushButton::clicked,this,[=]{run("disarm");});
 auto* watch=new QTimer(this);watch->setInterval(60000);connect(watch,&QTimer::timeout,this,[=]{run("check");});watch->start();
 l->addStretch();
 blog_=new QWidget;auto* b=new QVBoxLayout(blog_);auto* note=new QLabel("Local drafts only. Review before publishing.");b->addWidget(note);draft_=new QTextEdit;draft_->setReadOnly(true);b->addWidget(draft_);auto* copy=new QPushButton("Copy draft");b->addWidget(copy);connect(copy,&QPushButton::clicked,this,[this]{QApplication::clipboard()->setText(draft_->toPlainText());});
 auto* urlInput=new QLineEdit;urlInput->setPlaceholderText("Paste published https://j03.page/ article URL");b->addWidget(urlInput);
 auto* refresh=new QPushButton("Reload latest blog draft");b->addWidget(refresh);connect(refresh,&QPushButton::clicked,this,[this]{loadDraft();});
 connect(urlInput,&QLineEdit::textChanged,this,[this](const QString& v){auto u=QUrl(v);blogUrl_=(u.isValid()&&u.scheme()=="https"&&u.host()=="j03.page"&&u.path().size()>1&&!u.hasFragment()&&u.userInfo().isEmpty())?v:QString();});
 for(const auto& field:{"title","blog","facebook","linkedin","speech"}){auto key=QString::fromLatin1(field);auto* btn=new QPushButton(key=="blog"?"Copy WordPress-ready HTML":"Copy "+key);b->addWidget(btn);connect(btn,&QPushButton::clicked,this,[this,key]{loadDraft();QString value=draftObject_.value(key).toString();if((key=="facebook"||key=="linkedin")&&!blogUrl_.isEmpty())value.replace("[BLOG_URL]",blogUrl_);if(!value.isEmpty())QApplication::clipboard()->setText(value);});}
 net_=new QNetworkAccessManager(this);player_=new QMediaPlayer(this);chime_=new QMediaPlayer(this);audio_=new QAudioOutput(this);chimeAudio_=new QAudioOutput(this);player_->setAudioOutput(audio_);chime_->setAudioOutput(chimeAudio_);audio_->setVolume(.65);chimeAudio_->setVolume(.6);
 auto* devices=new QMediaDevices(this);auto updateDevices=[this]{auto d=QMediaDevices::defaultAudioOutput();if(!d.isNull()){if(audio_->device()!=d){player_->stop();audio_->setDevice(d);}if(chimeAudio_->device()!=d){chime_->stop();chimeAudio_->setDevice(d);}}};connect(devices,&QMediaDevices::audioOutputsChanged,this,updateDevices);updateDevices();
 connect(arm,&QPushButton::clicked,this,[this]{armed_=true;status_->setText("Audio armed; waiting for session");tick();});connect(stop,&QPushButton::clicked,this,[this]{armed_=false;player_->stop();chime_->stop();active_.clear();status_->setText("Audio disarmed");});
 connect(player_,&QMediaPlayer::playbackStateChanged,this,[this](QMediaPlayer::PlaybackState s){if(s==QMediaPlayer::PlayingState)log("Local music playback started: "+active_);});
 connect(player_,&QMediaPlayer::errorOccurred,this,[this](QMediaPlayer::Error,const QString& e){status_->setText("Audio error: "+e);log("Audio error: "+e);});
 timer_=new QTimer(this);timer_->setInterval(1000);connect(timer_,&QTimer::timeout,this,[this]{tick();loadDraft();static int n=0;if(++n%3==0)poll();});timer_->start();poll();
}
void SessionPanel::log(const QString& s){if(!QDir().mkpath(local))return;QFile f(local+"/session.log");if(f.open(QIODevice::Append))f.write((QDateTime::currentDateTimeUtc().toString(Qt::ISODate)+" "+s+"\n").toUtf8());}
void SessionPanel::poll(){if(busy_)return;busy_=true;QNetworkRequest req{QUrl(url_->text())};req.setTransferTimeout(2500);req.setAttribute(QNetworkRequest::RedirectPolicyAttribute,QNetworkRequest::ManualRedirectPolicy);req.setRawHeader("Cache-Control","no-cache");auto* r=net_->get(req);connect(r,&QNetworkReply::readyRead,this,[r]{if(r->bytesAvailable()>65536)r->abort();});connect(r,&QNetworkReply::finished,this,[this,r]{busy_=false;auto bytes=r->readAll();if(r->error()==QNetworkReply::NoError&&bytes.size()<=65536){auto d=QJsonDocument::fromJson(bytes);auto o=d.object();auto id=o.value("id").toString();auto start=QDateTime::fromString(o.value("start").toString(),Qt::ISODate);auto end=QDateTime::fromString(o.value("end").toString(),Qt::ISODate);auto file=o.value("file").toString();if(o.value("schema").toString()=="ancestale.session.v1"&&QRegularExpression("^[A-Za-z0-9_-]{1,80}$").match(id).hasMatch()&&start.isValid()&&end.isValid()&&start.secsTo(end)>0&&start.secsTo(end)<=23400&&QRegularExpression("^[A-Za-z0-9][A-Za-z0-9_. -]{0,150}\\.(mp3|ogg|wav|flac|m4a)$",QRegularExpression::CaseInsensitiveOption).match(file).hasMatch()&&!file.contains("..")){QFile approved(local+"/ancestale-session.json");if(approved.open(QIODevice::ReadOnly)&&approved.size()<=65536&&QJsonDocument::fromJson(approved.readAll()).object()==o){state_=o;lastOk_=QDateTime::currentSecsSinceEpoch();}else{status_->setText("Remote session has not been locally approved");}}}r->deleteLater();tick();});}
void SessionPanel::tick(){if(state_.isEmpty())return;auto now=QDateTime::currentDateTimeUtc();auto start=QDateTime::fromString(state_.value("start").toString(),Qt::ISODate);auto end=QDateTime::fromString(state_.value("end").toString(),Qt::ISODate);QString id=state_.value("id").toString();qint64 left=now.secsTo(end);if(now>=end){countdown_->setText("00:00 — Session ended");player_->stop();if(armed_&&active_==id&&ended_!=id){ended_=id;chime_->setSource(QUrl::fromLocalFile(root+"/session/chime.wav"));chime_->play();log("Session ended: "+id);}active_.clear();return;}if(now.toSecsSinceEpoch()-lastOk_>15){player_->stop();active_.clear();status_->setText("Connection stale; audio stopped");return;}countdown_->setText(QString("%1:%2 remaining").arg(left/60,2,10,QChar('0')).arg(left%60,2,10,QChar('0')));song_->setText(state_.value("title").toString()+" | "+state_.value("license").toString()+"\nWebsite requested track: 192.168.5.215:8081 (browser playback not independently verified)");if(now<start){player_->stop();active_.clear();countdown_->setText("Starts at "+start.toLocalTime().toString("hh:mm:ss"));return;}if(!armed_)return;if(active_!=id&&!played_.contains(id)){player_->stop();auto path=root+"/Music/"+state_.value("file").toString();QFileInfo f(path);if(!f.isFile()||f.isSymLink()||f.canonicalPath()!=QFileInfo(root+"/Music").absoluteFilePath()){status_->setText("Missing or unsafe local music file");return;}QFile track(path);QCryptographicHash digest(QCryptographicHash::Sha256);if(!track.open(QIODevice::ReadOnly)||!digest.addData(&track)||QString::fromLatin1(digest.result().toHex())!=state_.value("sha256").toString()){status_->setText("Local track hash mismatch");return;}active_=id;played_.insert(id);player_->setSource(QUrl::fromLocalFile(path));player_->setLoops(1);player_->play();status_->setText("Local playback requested; see player state");}}
void SessionPanel::loadDraft(){
 const auto day=QDateTime::currentDateTimeUtc().toTimeZone(QTimeZone("America/Los_Angeles")).date();
 QStringList paths={local+"/blog.json",QDir::homePath()+"/emergency-notes/"+day.toString("yyyy-MM-dd")+"-draft.json"};
 if(day==QDate(2026,11,14))paths.prepend(QDir::homePath()+"/.ancestale/alpha-blog.json");
 QJsonObject best;QDateTime newest;
 for(const auto& path:paths){QFile f(path);QFileInfo info(f);if(!info.isFile()||info.isSymLink()||!f.open(QIODevice::ReadOnly)||f.size()>131072)continue;auto o=QJsonDocument::fromJson(f.readAll()).object();QString sid=o.value("session_id").toString();if(sid.isEmpty())continue;
 bool matching=(sid==state_.value("id").toString())||(day==QDate(2026,11,14)&&sid=="alpha-20261114")||(sid=="backup-"+day.toString("yyyy-MM-dd"))||(o.value("date").toString()==day.toString("yyyy-MM-dd"));if(!matching)continue;
 bool valid=true;for(const auto& k:{"title","blog","facebook","linkedin","speech"})if(o.value(k).toString().isEmpty())valid=false;if(!valid)continue;
 if(!newest.isValid()||info.lastModified()>newest){newest=info.lastModified();best=o;}}
 if(best.isEmpty())return;draftObject_=best;QString text;for(const auto& k:{"title","blog","facebook","linkedin","speech"})text+=QString::fromLatin1(k).toUpper()+"\n"+best.value(k).toString()+"\n\n";
 if(text!=loadedDraft_){loadedDraft_=text;draft_->setPlainText(text);}
}
