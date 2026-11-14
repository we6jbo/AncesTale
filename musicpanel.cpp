#include "musicpanel.h"
#include <QAudioOutput>
#include <QMediaPlayer>
#include <QListWidget>
#include <QPlainTextEdit>
#include <QLabel>
#include <QPushButton>
#include <QProcess>
#include <QJsonDocument>
#include <QJsonArray>
#include <QJsonObject>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QSlider>
#include <QUrl>
#include <QSignalBlocker>
#include <QMessageBox>
#include <QFileInfo>
#include <QFile>
#include <QDir>
#include <QComboBox>
#include <QTime>
#include <QLineEdit>
#include <QSpinBox>
#include <QFormLayout>
#include <QMediaDevices>
#include <QAudioDevice>
#include <memory>
namespace {
const QString root="/home/we6jbo/Projects/AncesTale";
const QString helper=root+"/music/catalog.py";
QString clockText(qint64 ms){return QString("%1:%2").arg(ms/60000).arg((ms/1000)%60,2,10,QChar('0'));}
}
MusicPanel::MusicPanel(QWidget *parent):QWidget(parent){
 auto *layout=new QVBoxLayout(this);
 auto *intro=new QLabel("Preview local tracks and save scene notes for Vibe. Music is not approved for web distribution simply because it appears here. No automatic Pi changes.");intro->setWordWrap(true);layout->addWidget(intro);
 auto *row=new QHBoxLayout;layout->addLayout(row);auto *scan=new QPushButton("Refresh music catalog");auto *remote=new QPushButton("Check Pi filenames (SSH)");row->addWidget(scan);row->addWidget(remote);
 auto *split=new QHBoxLayout;layout->addLayout(split,1);auto *list=new QListWidget;split->addWidget(list,1);
 auto *detail=new QVBoxLayout;split->addLayout(detail,2);auto *metadata=new QPlainTextEdit;metadata->setReadOnly(true);detail->addWidget(metadata,1);auto *role=new QComboBox;role->addItems({"Unassigned","Intro","Beginning","Middle","Outro","Other scene","Do not use"});detail->addWidget(role);
 auto *form=new QFormLayout;detail->addLayout(form);
 auto *titleEdit=new QLineEdit;auto *sourceEdit=new QLineEdit;auto *creditEdit=new QLineEdit;auto *days=new QLineEdit;auto *repeat=new QLineEdit;auto *quarter=new QComboBox;
 for(auto *e:{titleEdit,sourceEdit,creditEdit})e->setReadOnly(true);
 quarter->addItems({"Intro","1/4","2/4","3/4","Outro","Unassigned"});
 form->addRow("Track title",titleEdit);form->addRow("Source URL",sourceEdit);form->addRow("Credit / license",creditEdit);form->addRow("Game sessions (days)",days);form->addRow("Cue",quarter);form->addRow("Repeat rule",repeat);
 auto *notes=new QPlainTextEdit;notes->setPlaceholderText("When should this track play? Describe scene, mood, historical setting, and any licensing or playback restrictions.");detail->addWidget(notes,1);auto *save=new QPushButton("Save track notes");detail->addWidget(save);
 auto *timingRow=new QHBoxLayout;layout->addLayout(timingRow);auto *q2=new QSpinBox;auto *q3=new QSpinBox;for(auto *s:{q2,q3}){s->setRange(1,99);s->setSuffix("%");}q2->setValue(50);q3->setValue(75);auto *saveTiming=new QPushButton("Save cue timing");timingRow->addWidget(new QLabel("2/4 offset"));timingRow->addWidget(q2);timingRow->addWidget(new QLabel("3/4 offset"));timingRow->addWidget(q3);timingRow->addWidget(saveTiming);
 auto *controls=new QHBoxLayout;layout->addLayout(controls);auto *play=new QPushButton("Play");auto *pause=new QPushButton("Pause");auto *stop=new QPushButton("Stop");controls->addWidget(play);controls->addWidget(pause);controls->addWidget(stop);auto *seek=new QSlider(Qt::Horizontal);seek->setRange(0,1000);controls->addWidget(seek,1);auto *elapsed=new QLabel("0:00 / 0:00");controls->addWidget(elapsed);auto *volume=new QSlider(Qt::Horizontal);volume->setRange(0,100);volume->setValue(50);controls->addWidget(new QLabel("Volume"));controls->addWidget(volume);
 auto *status=new QLabel;status->setTextFormat(Qt::PlainText);status->setWordWrap(true);layout->addWidget(status);
 auto *player=new QMediaPlayer(this);auto *audio=new QAudioOutput(this);audio->setVolume(.5f);player->setAudioOutput(audio);
 auto *devices=new QMediaDevices(this);auto *output=new QComboBox;auto *refreshAudio=new QPushButton("Refresh audio devices");auto *audioRow=new QHBoxLayout;layout->addLayout(audioRow);audioRow->addWidget(new QLabel("Audio output"));audioRow->addWidget(output,1);audioRow->addWidget(refreshAudio);
 auto refreshDevices=[=]{auto old=output->currentData().toByteArray();QSignalBlocker blocker(output);output->clear();output->addItem("System default",QByteArray());for(const auto &d:QMediaDevices::audioOutputs())output->addItem(d.description(),d.id());int i=output->findData(old);output->setCurrentIndex(i<0?0:i);auto wanted=output->currentData().toByteArray();auto selected=QMediaDevices::defaultAudioOutput();for(const auto &d:QMediaDevices::audioOutputs())if(!wanted.isEmpty()&&d.id()==wanted)selected=d;if(audio->device()!=selected){player->stop();audio->setDevice(selected);}if(selected.isNull())status->setText("No audio output available");};
 connect(devices,&QMediaDevices::audioOutputsChanged,this,refreshDevices);connect(refreshAudio,&QPushButton::clicked,this,refreshDevices);connect(output,&QComboBox::currentIndexChanged,this,[=](int){refreshDevices();});refreshDevices();
 auto *job=new QProcess(this);auto catalog=std::make_shared<QJsonArray>();auto dirty=std::make_shared<bool>(false);auto loading=std::make_shared<bool>(false);auto previous=std::make_shared<int>(-1);auto action=std::make_shared<QString>();
 auto selection=[=](int i){return i>=0&&i<catalog->size()?catalog->at(i).toObject():QJsonObject{};};
 auto show=[=](int i){*loading=true;*previous=i;player->stop();auto o=selection(i);auto n=o.value("annotation").toObject();notes->setPlainText(n.value("notes").toString());titleEdit->setText(n.value("title").toString());sourceEdit->setText(n.value("source_url").toString());creditEdit->setText(n.value("credit").toString());days->setText(n.value("days").toString());repeat->setText(n.value("repeat").toString());int qi=quarter->findText(n.value("quarter").toString());quarter->setCurrentIndex(qi<0?5:qi);int j=role->findText(n.value("role").toString());role->setCurrentIndex(j<0?0:j); QJsonObject display=o;display.remove("annotation");metadata->setPlainText(QString::fromUtf8(QJsonDocument(display).toJson(QJsonDocument::Indented)));*dirty=false;*loading=false;};
 auto confirm=[=](){return !*dirty||QMessageBox::question(this,"Unsaved music notes","Discard unsaved changes to this track?",QMessageBox::Discard|QMessageBox::Cancel,QMessageBox::Cancel)==QMessageBox::Discard;};
 connect(notes,&QPlainTextEdit::textChanged,this,[=]{if(!*loading)*dirty=true;});connect(role,&QComboBox::currentIndexChanged,this,[=](int){if(!*loading)*dirty=true;});
 for(auto *e:{titleEdit,sourceEdit,creditEdit,days,repeat})connect(e,&QLineEdit::textChanged,this,[=](const QString&){if(!*loading)*dirty=true;});connect(quarter,&QComboBox::currentIndexChanged,this,[=](int){if(!*loading)*dirty=true;});
 connect(list,&QListWidget::currentRowChanged,this,[=](int i){if(*loading)return;if(!confirm()){QSignalBlocker b(list);list->setCurrentRow(*previous);return;}show(i);});
 auto busy=[=](bool active){scan->setEnabled(!active);remote->setEnabled(!active);save->setEnabled(!active);list->setEnabled(!active);notes->setEnabled(!active);role->setEnabled(!active);for(auto *e:{titleEdit,sourceEdit,creditEdit,days,repeat})e->setEnabled(!active);quarter->setEnabled(!active);saveTiming->setEnabled(!active);q2->setEnabled(!active);q3->setEnabled(!active);};
 auto launch=[=](QString cmd,QByteArray data){if(job->state()!=QProcess::NotRunning)return;*action=cmd;busy(true);status->setText("Working: "+cmd);job->setProgram("python3");job->setArguments({helper,cmd});job->start();if(!data.isEmpty())job->write(data);job->closeWriteChannel();};
 connect(job,&QProcess::errorOccurred,this,[=](QProcess::ProcessError e){if(e==QProcess::FailedToStart){busy(false);status->setText("Cannot start catalog helper: "+job->errorString());}});
 connect(job,&QProcess::finished,this,[=](int code,QProcess::ExitStatus exit){auto out=job->readAllStandardOutput();auto err=job->readAllStandardError();busy(false);if(code||exit!=QProcess::NormalExit){status->setText("Catalog operation failed: "+QString::fromUtf8(err).left(1000));return;}QJsonParseError parse;auto doc=QJsonDocument::fromJson(out,&parse);if(parse.error!=QJsonParseError::NoError||!doc.isObject()||!doc.object().value("tracks").isArray()){status->setText("Invalid catalog response");return;}auto selected=selection(list->currentRow()).value("filename").toString();*loading=true;*catalog=doc.object().value("tracks").toArray();auto timing=doc.object().value("timing").toObject();q2->setValue(timing.value("quarter2_percent").toInt(50));q3->setValue(timing.value("quarter3_percent").toInt(75));list->clear();int next=-1;for(int i=0;i<catalog->size();++i){auto o=selection(i);auto name=o.value("filename").toString();list->addItem(name);if(name==selected)next=i;}list->setCurrentRow(next>=0?next:(catalog->isEmpty()?-1:0));*loading=false;show(list->currentRow());status->setText(QString("%1 tracks. Catalog saved privately for Vibe. %2").arg(catalog->size()).arg(doc.object().value("warning").toString()));});
 connect(scan,&QPushButton::clicked,this,[=]{if(confirm())launch("scan",{});});connect(remote,&QPushButton::clicked,this,[=]{if(confirm())launch("check-pi",{});});
 connect(save,&QPushButton::clicked,this,[=]{auto o=selection(list->currentRow());if(o.isEmpty())return;launch("save",QJsonDocument(QJsonObject{{"filename",o.value("filename")},{"role",role->currentText()},{"notes",notes->toPlainText()},{"title",titleEdit->text()},{"source_url",sourceEdit->text()},{"credit",creditEdit->text()},{"days",days->text()},{"quarter",quarter->currentText()},{"repeat",repeat->text()}}).toJson(QJsonDocument::Compact));});
 connect(saveTiming,&QPushButton::clicked,this,[=]{if(q2->value()>=q3->value()){status->setText("2/4 must precede 3/4");return;}if(confirm())launch("save-timing",QJsonDocument(QJsonObject{{"quarter2_percent",q2->value()},{"quarter3_percent",q3->value()}}).toJson(QJsonDocument::Compact));});
 connect(play,&QPushButton::clicked,this,[=]{auto o=selection(list->currentRow());auto path=root+"/Music/"+o.value("filename").toString();if(o.isEmpty()||!QFileInfo(path).isFile()||QFileInfo(path).isSymLink())return;refreshDevices();if(audio->device().isNull()){status->setText("No audio output available");return;}auto url=QUrl::fromLocalFile(path);if(player->source()!=url)player->setSource(url);player->play();});connect(pause,&QPushButton::clicked,player,&QMediaPlayer::pause);connect(stop,&QPushButton::clicked,player,&QMediaPlayer::stop);
 connect(volume,&QSlider::valueChanged,this,[=](int v){audio->setVolume(v/100.f);});connect(seek,&QSlider::sliderMoved,this,[=](int v){if(player->isSeekable())player->setPosition(player->duration()*v/1000);});
 auto progress=[=]{if(!seek->isSliderDown())seek->setValue(player->duration()>0?int(player->position()*1000/player->duration()):0);elapsed->setText(clockText(player->position())+" / "+clockText(player->duration()));};connect(player,&QMediaPlayer::positionChanged,this,[=](qint64){progress();});connect(player,&QMediaPlayer::durationChanged,this,[=](qint64){progress();});connect(player,&QMediaPlayer::errorOccurred,this,[=](QMediaPlayer::Error,const QString &s){status->setText("Playback unavailable: "+s+". MIDI may need a separate renderer.");});
 // Refresh explicitly: avoids probing the library at every application startup.
 status->setText("Click Refresh music catalog to load tracks and notes.");
}
