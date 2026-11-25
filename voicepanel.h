#pragma once
#include <QWidget>
#include <QMap>
#include <QList>
#include <QStringList>
#include <QVBoxLayout>
#include <QFormLayout>
#include <QScrollArea>
#include <QComboBox>
#include <QSpinBox>
#include <QCheckBox>
#include <QPushButton>
#include <QLabel>
#include <QFile>
#include <QSaveFile>
#include <QDir>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QClipboard>
#include <QApplication>
#include <QProcess>
#include <QFileInfo>
#include <QStandardPaths>
#include <QDesktopServices>
#include <QUrl>
class VoicePanel : public QWidget {
public:
 static QJsonObject readObject(const QString& path){QFile f(path);if(!f.open(QIODevice::ReadOnly))return {};return QJsonDocument::fromJson(f.readAll()).object();}
 static QString root(){return "/home/we6jbo/Projects/AncesTale";}
 static QString settings(){return QDir::homePath()+"/.ancestale/text-to-voice.json";}
 explicit VoicePanel(QWidget* parent=nullptr):QWidget(parent){
 auto* outer=new QVBoxLayout(this);auto* scroll=new QScrollArea(this);scroll->setWidgetResizable(true);outer->addWidget(scroll);auto* body=new QWidget;scroll->setWidget(body);auto* form=new QFormLayout(body);
 auto* intro=new QLabel("Configure the player’s audible setup. Green confirms the synthetic Welcome, red retries, purple reopens setup. Recorded prompts are separate from TTS. Save before preparing the Vibe handoff.");intro->setWordWrap(true);form->addRow(intro);
 auto defaults=readObject(root()+"/voice/defaults.json");auto stored=readObject(settings());for(auto it=stored.begin();it!=stored.end();++it)defaults.insert(it.key(),it.value());auto clips=readObject(root()+"/voice/clips.json");
 auto engineValues=QStringList{"hosted","local-en","local-en-US","local-en-GB","local-default","manual-extension","skip"};auto engineLabels=QStringList{"Hosted Piper / generated audio","Browser English voice","Browser US English","Browser UK English","Browser default English","Manual Chrome extension check (operator only)","Skip"};
 auto eng=defaults.value("engines").toArray();for(int i=0;i<10;i++){auto* c=new QComboBox(body);for(int j=0;j<engineValues.size();j++)c->addItem(engineLabels[j],engineValues[j]);c->setCurrentIndex(qMax(0,c->findData(i<eng.size()?eng.at(i).toString():QString("skip"))));engines.append(c);form->addRow(QString("Engine attempt %1").arg(i+1),c);}
 auto spin=[&](const QString& label,const QString& key,int low,int high){auto* s=new QSpinBox(body);s->setRange(low,high);s->setValue(defaults.value(key).toInt(low));numbers.insert(key,s);form->addRow(label,s);};spin("Maximum engine attempts","max_attempts",1,10);spin("Troubleshooting limit (seconds)","troubleshooting_seconds",30,1800);spin("Reading check (seconds)","reading_seconds",60,7200);spin("Idle check (seconds)","idle_seconds",30,3600);spin("Reading difficulty reports before check","frustration_count",1,20);
 allow=new QCheckBox("Offer green / purple / red fallback options",body);allow->setChecked(defaults.value("allow_reading").toBool(true));form->addRow(allow);success=new QCheckBox("Use recorded success message (only after listening and verifying wording)",body);success->setChecked(defaults.value("use_success_recording").toBool(false));form->addRow(success);
 auto mapping=defaults.value("prompt_map").toObject();for(auto it=clips.begin();it!=clips.end();++it){auto* c=new QComboBox(body);c->addItem("No recording","");for(auto jt=clips.begin();jt!=clips.end();++jt)c->addItem(jt.key()+" — "+jt.value().toObject().value("file").toString(),jt.key());c->setCurrentIndex(qMax(0,c->findData(mapping.value(it.key()).toString(it.key()))));prompts.insert(it.key(),c);form->addRow(it.key(),c);}
 auto* preview=new QPushButton("Listen to selected recording",body);auto* choice=new QComboBox(body);for(auto it=clips.begin();it!=clips.end();++it)choice->addItem(it.key(),it.value().toObject().value("file").toString());form->addRow(choice,preview);connect(preview,&QPushButton::clicked,this,[=]{QDesktopServices::openUrl(QUrl::fromLocalFile(root()+"/voice-clips/"+choice->currentData().toString()));});
 auto* save=new QPushButton("Save Text to Voice settings",body);form->addRow(save);auto* status=new QLabel(body);status->setWordWrap(true);form->addRow(status);connect(save,&QPushButton::clicked,this,[=]{QJsonObject o;QJsonArray a;for(auto* c:engines)a.append(c->currentData().toString());o.insert("engines",a);for(auto it=numbers.begin();it!=numbers.end();++it)o.insert(it.key(),it.value()->value());QJsonObject m;for(auto it=prompts.begin();it!=prompts.end();++it)m.insert(it.key(),it.value()->currentData().toString());o.insert("prompt_map",m);o.insert("allow_reading",allow->isChecked());o.insert("use_success_recording",success->isChecked());QDir().mkpath(QDir::homePath()+"/.ancestale");QSaveFile f(settings());auto bytes=QJsonDocument(o).toJson();if(f.open(QIODevice::WriteOnly)){f.setPermissions(QFileDevice::ReadOwner|QFileDevice::WriteOwner);if(f.write(bytes)==bytes.size()&&f.commit()){status->setText("Saved. Prepare the signed Vibe handoff to include these settings.");return;}}status->setText("Could not save settings.");});
 int available=0;for(auto it=clips.begin();it!=clips.end();++it)if(QFileInfo::exists(root()+"/voice-clips/"+it.value().toObject().value("file").toString()))available++;status->setText(QString("%1 of %2 local clips detected (audio content not verified).").arg(available).arg(clips.size()));
 }
private: QList<QComboBox*> engines;QMap<QString,QSpinBox*> numbers;QMap<QString,QComboBox*> prompts;QCheckBox *allow,*success;
};
