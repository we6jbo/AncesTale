#include "invitationpanel.h"
#include <QFormLayout>
#include <QVBoxLayout>
#include <QLineEdit>
#include <QLabel>
#include <QPushButton>
#include <QProcess>
#include <QJsonArray>
#include <QJsonObject>
#include <QJsonDocument>
#include <array>
namespace {
const QString helper="/home/we6jbo/Projects/AncesTale/invitations/invite.py";
bool run(const QString &action,const QByteArray &input,QByteArray &output){
 QProcess p; p.start("python3",{helper,action});
 if(!p.waitForStarted(2000))return false;
 if(!input.isEmpty())p.write(input);
 p.closeWriteChannel();
 if(!p.waitForFinished(3000)){p.kill();p.waitForFinished();return false;}
 output=p.readAllStandardOutput();return p.exitStatus()==QProcess::NormalExit && p.exitCode()==0;
}
}
InvitationPanel::InvitationPanel(QWidget *parent):QWidget(parent){
 auto *layout=new QVBoxLayout(this);
 auto *intro=new QLabel("Save up to three consenting invitation recipients. Saving never sends email. Vibe sends only after your explicit game-ready instruction, at most once each Pacific day.");intro->setWordWrap(true);layout->addWidget(intro);
 auto *form=new QFormLayout;layout->addLayout(form);
 std::array<QLineEdit*,3> names{},emails{};
 for(int i=0;i<3;++i){names[i]=new QLineEdit;emails[i]=new QLineEdit;names[i]->setMaxLength(100);emails[i]->setMaxLength(254);form->addRow(QString("Name %1").arg(i+1),names[i]);form->addRow(QString("Email %1").arg(i+1),emails[i]);}
 auto *status=new QLabel;status->setTextFormat(Qt::PlainText);status->setWordWrap(true);
 auto *save=new QPushButton("Save recipients locally");auto *reload=new QPushButton("Reload recipients");layout->addWidget(save);layout->addWidget(reload);layout->addWidget(status);layout->addStretch();
 auto load=[=]{QByteArray out;if(!run("load",{},out)){status->setText("Could not read private recipients. Saving disabled until reload succeeds.");save->setEnabled(false);return;}
 QJsonParseError err;auto doc=QJsonDocument::fromJson(out,&err);if(err.error!=QJsonParseError::NoError||!doc.isArray()){status->setText("Invalid recipient response.");save->setEnabled(false);return;}
 auto a=doc.array();for(int i=0;i<3;++i){auto o=i<a.size()?a.at(i).toObject():QJsonObject{};names[i]->setText(o.value("name").toString());emails[i]->setText(o.value("email").toString());}save->setEnabled(true);status->setText("Loaded private recipients. No email sent.");};
 connect(reload,&QPushButton::clicked,this,load);
 connect(save,&QPushButton::clicked,this,[=]{QJsonArray a;for(int i=0;i<3;++i)a.append(QJsonObject{{"name",names[i]->text().trimmed()},{"email",emails[i]->text().trimmed()}});QByteArray out;if(run("save",QJsonDocument(a).toJson(QJsonDocument::Compact),out))status->setText("Recipients saved privately. No email sent.");else status->setText("Save failed. Use complete name/email pairs and unique valid email addresses; check private file permissions.");});
 load();
}
