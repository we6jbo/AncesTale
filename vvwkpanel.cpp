#include "vvwkpanel.h"
#include <QVBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QPlainTextEdit>
#include <QTextCursor>
#include <QProcess>
#include <QDesktopServices>
#include <QUrl>
#include <QFile>
#include <QMessageBox>
VVWKPanel::VVWKPanel(QWidget *parent): QWidget(parent) {
 auto *layout=new QVBoxLayout(this);
 layout->addWidget(new QLabel("VVWK | Chromebook compatibility and consent-based enrollment",this));
 auto *open=new QPushButton("Open VVWK website",this);layout->addWidget(open);
 auto *note=new QLabel("New enrollment is closed by the v0.5 server update. Existing cookies remain valid. Use Player to inspect presence. Do not redeploy the old enrollment backend.",this);note->setWordWrap(true);layout->addWidget(note);layout->addStretch();
 connect(open,&QPushButton::clicked,this,[]{QDesktopServices::openUrl(QUrl("http://192.168.5.215:8081/nov-game/VVWK/"));});
}
