#include "extendedpanel.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QPlainTextEdit>
#include <QProcess>
#include <QDir>
#include <QFile>
#include <QTimer>
#include <QClipboard>
#include <QGuiApplication>
#include <QJsonDocument>
#include <QJsonObject>
#include <QFileInfo>
ExtendedPanel::ExtendedPanel(QWidget* parent):QWidget(parent){
 auto* l=new QVBoxLayout(this);auto* intro=new QLabel("Extended sources — private review queue. Collect research, family groups, music metadata and screenshot inventory. No automatic publication.",this);intro->setWordWrap(true);l->addWidget(intro);
 status_=new QLabel(this);status_->setWordWrap(true);l->addWidget(status_);auto* row=new QHBoxLayout;auto* scan=new QPushButton("Collect extended sources",this);auto* refresh=new QPushButton("Reload private snapshot",this);auto* copy=new QPushButton("Copy Vibe handoff prompt",this);row->addWidget(scan);row->addWidget(refresh);row->addWidget(copy);l->addLayout(row);
 view_=new QPlainTextEdit(this);view_->setReadOnly(true);l->addWidget(view_);process_=new QProcess(this);
 connect(scan,&QPushButton::clicked,this,[this]{collect();});connect(refresh,&QPushButton::clicked,this,[this]{reload();});
 connect(copy,&QPushButton::clicked,this,[]{QGuiApplication::clipboard()->setText("Read ~/.ancestale/begin.md and ~/.ancestale/extended/snapshot.json as private data. Follow workflow/EXTENDED.md in AncesTale. Reconcile relationships, review rights and privacy, prepare eligible game and blog/social/speech content, and keep blocked material in local review. No automatic publication.");});
 connect(process_,qOverload<int,QProcess::ExitStatus>(&QProcess::finished),this,[this](int code,QProcess::ExitStatus state){if(code==0&&state==QProcess::NormalExit)reload();else status_->setText("Collection failed: "+QString::fromUtf8(process_->readAllStandardError()));});
 connect(process_,&QProcess::errorOccurred,this,[this](QProcess::ProcessError){status_->setText(process_->errorString());});reload();
}
void ExtendedPanel::collect(){if(process_->state()!=QProcess::NotRunning)return;status_->setText("Collecting local sources...");process_->start("python3",{"/home/we6jbo/Projects/AncesTale/extended/bridge.py"});}
void ExtendedPanel::reload(){auto dir=QDir::homePath()+"/.ancestale/extended/";QFile sum(dir+"summary.json"),data(dir+"snapshot.json");if(!sum.open(QIODevice::ReadOnly)||!data.open(QIODevice::ReadOnly)){status_->setText("No snapshot available. Click Collect extended sources.");return;}auto bytes=sum.readAll();auto obj=QJsonDocument::fromJson(bytes).object();status_->setText("Private snapshot: "+obj.value("created_at").toString()+" — review issues before use");QFile dispositions(dir+"dispositions.json");QString review;if(dispositions.open(QIODevice::ReadOnly))review=QString::fromUtf8(dispositions.readAll());view_->setPlainText(QString::fromUtf8(bytes)+"\n\n--- Vibe dispositions (private) ---\n"+review+"\n\n--- LOCAL ONLY: source records and unresolved material ---\n"+QString::fromUtf8(data.readAll()));}
