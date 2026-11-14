#include "playerpanel.h"
#include <QVBoxLayout>
#include <QLabel>
#include <QPlainTextEdit>
#include <QPushButton>
#include <QProcess>
#include <QTimer>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QDateTime>
PlayerPanel::PlayerPanel(QWidget *parent):QWidget(parent){
 auto *l=new QVBoxLayout(this);auto *status=new QLabel("Unknown — click Refresh players");status->setWordWrap(true);status->setTextFormat(Qt::PlainText);l->addWidget(status);
 auto *refresh=new QPushButton("Refresh players (SSH)");l->addWidget(refresh);
 auto *view=new QPlainTextEdit;view->setReadOnly(true);l->addWidget(view);
 auto *p=new QProcess(this);auto *timeout=new QTimer(this);timeout->setSingleShot(true);
 connect(refresh,&QPushButton::clicked,this,[=]{if(p->state()!=QProcess::NotRunning)return;view->clear();status->setText("Checking Pi — presence unknown");refresh->setEnabled(false);p->start("python3",{"/home/we6jbo/Projects/AncesTale/vvwk/read_players.py"});timeout->start(20000);});
 connect(timeout,&QTimer::timeout,this,[=]{p->kill();});
 connect(p,&QProcess::errorOccurred,this,[=](QProcess::ProcessError){timeout->stop();refresh->setEnabled(true);status->setText("Unknown — SSH query failed");});
 connect(p,qOverload<int,QProcess::ExitStatus>(&QProcess::finished),this,[=](int code,QProcess::ExitStatus exit){timeout->stop();refresh->setEnabled(true);auto bytes=p->readAllStandardOutput();auto d=QJsonDocument::fromJson(bytes);auto o=d.object();if(code||exit!=QProcess::NormalExit||o.value("schema").toString()!="ancestale.players.v1"){status->setText("Unknown — query failed; check SSH from terminal");return;} status->setText("Snapshot at "+QDateTime::currentDateTime().toString(Qt::ISODate)+" — refresh for current status");QString text;for(auto val:o.value("players").toArray()){auto a=val.toObject();text+=QString("Player: %1\nLast IP: %2\nMasked token ID: %3\nLast game page: %4\nLast seen: %5\nStatus: %6\nExpires: %7\n\n").arg(a.value("name").toString(),a.value("ip").toString(),a.value("player_id").toString(),a.value("page").toString(),a.value("last_seen").toString(),a.value("status").toString(),a.value("expires").toString());}view->setPlainText(text.isEmpty()?"No active enrollment records":text);});
}
