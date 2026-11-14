#!/usr/bin/env python3
"""Local invitations. No network operation except explicit send --game-ready."""
import argparse, datetime, email.message, fcntl, getpass, json, os, pathlib, re, smtplib, ssl, stat, sys, tempfile, warnings
from zoneinfo import ZoneInfo
ROOT=pathlib.Path.home()/'.ancestale-invitations'
SENDER='master@we6jbobbs.org'
REPLY='we6jbo+decisiontree@gmail.com'
URL='http://192.168.5.215:8081/nov-game/'

def private_dir():
    os.umask(0o077)
    ROOT.mkdir(mode=0o700,exist_ok=True)
    s=ROOT.lstat()
    if not stat.S_ISDIR(s.st_mode) or s.st_uid!=os.getuid() or s.st_mode & 0o077: raise ValueError('Unsafe private directory; require owner and mode 700')

def read(name, default=None):
    p=ROOT/name
    try: fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    except FileNotFoundError: return default
    with os.fdopen(fd,'r',encoding='utf-8') as f:
        s=os.fstat(f.fileno())
        if not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid() or s.st_mode & 0o077 or s.st_nlink!=1: raise ValueError('Unsafe private file')
        return f.read(1000001)

def write(name,data):
    p=ROOT/name
    # Refuse unsafe preexisting paths rather than following them.
    read(name)
    fd,tmp=tempfile.mkstemp(dir=ROOT,prefix='.tmp-')
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            f.write(data);f.flush();os.fsync(f.fileno())
        os.replace(tmp,p)
        d=os.open(ROOT,os.O_DIRECTORY);os.fsync(d);os.close(d)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def validate(rows):
    if not isinstance(rows,list) or len(rows)>3:raise ValueError('Expected up to three recipient slots')
    out=[];seen=set()
    for r in rows:
        if not isinstance(r,dict) or set(r)!={'name','email'}:raise ValueError('Invalid slot')
        n,e=r['name'],r['email']
        if not isinstance(n,str) or not isinstance(e,str):raise ValueError('Invalid slot')
        n,e=n.strip(),e.strip()
        if not n and not e:continue
        if not n or len(n)>100 or any(ord(c)<32 or ord(c)==127 for c in n) or len(e)>254 or not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+",e):raise ValueError('Complete valid name and email required')
        if e.lower() in seen:raise ValueError('Duplicate email')
        seen.add(e.lower());out.append({'name':n,'email':e})
    return out

def recipients():return validate(json.loads(read('recipients.json','[]')))

def send(entry_root=False):
    url="http://192.168.5.215:8081/" if entry_root else URL
    day=datetime.datetime.now(ZoneInfo('America/Los_Angeles')).date().isoformat()
    rows=recipients()
    if not rows:raise ValueError('No saved recipients')
    # One batch per Pacific day, even if recipient list changes. Persist reservation before sending.
    ledger=json.loads(read('daily-ledger.json','{}'))
    if day in ledger:
        print('No mail sent: daily invitation batch already reserved or attempted.');return
    password=read('smtp-password')
    if not password:raise ValueError('Set up SMTP password first')
    password=password.removesuffix('\n')
    if not password or '\n' in password or '\r' in password:raise ValueError('Invalid password file')
    # Do not reserve until SMTP authentication succeeds; no messages sent before reservation.
    with smtplib.SMTP('mail.privateemail.com',587,timeout=20) as smtp:
        smtp.ehlo();smtp.starttls(context=ssl.create_default_context());smtp.ehlo();smtp.login(SENDER,password)
        ledger[day]={'state':'reserved','recipients':[{'email':r['email'],'state':'pending'} for r in rows]}
        write('daily-ledger.json',json.dumps(ledger,indent=2)+'\n')
        for i,r in enumerate(rows):
            item=ledger[day]['recipients'][i];item['state']='attempting';write('daily-ledger.json',json.dumps(ledger,indent=2)+'\n')
            msg=email.message.EmailMessage();msg['From']=SENDER;msg['To']=r['email'];msg['Reply-To']=REPLY;msg['Subject']='Would you like to play AncesTale today?'
            msg.set_content(f"Hi {r['name']},\n\nWould you like to play AncesTale today?\n\n{url}\n\nJeremiah O'Neal\n\nAutomated invitation sent on Jeremiah's behalf by AncesTale. The game link requires access to the local network.\n")
            try:
                refused=smtp.send_message(msg,from_addr=SENDER,to_addrs=[r['email']]);item['state']='refused' if refused else 'accepted_by_smtp'
            except Exception:
                item['state']='failed_or_uncertain'
                write('daily-ledger.json',json.dumps(ledger,indent=2)+'\n');raise RuntimeError('SMTP attempt failed or uncertain; no automatic retry') from None
            write('daily-ledger.json',json.dumps(ledger,indent=2)+'\n')
        ledger[day]['state']='finished';write('daily-ledger.json',json.dumps(ledger,indent=2)+'\n')
        print('Daily batch completed. SMTP accepted '+str(sum(x['state']=='accepted_by_smtp' for x in ledger[day]['recipients']))+' message(s); inbox delivery not verified.')

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['load','save','setup','send']);p.add_argument('--game-ready',action='store_true');p.add_argument('--entry-root',action='store_true',help='Use root only after live game entry is verified by operator');a=p.parse_args()
    if a.action=='send' and not a.game_ready:p.error('Explicit --game-ready required')
    private_dir()
    fd=os.open(ROOT/'lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW|os.O_NONBLOCK,0o600)
    with os.fdopen(fd,'w') as lock:
        s=os.fstat(lock.fileno())
        if not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid() or s.st_mode & 0o077 or s.st_nlink!=1:raise ValueError('Unsafe lock')
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if a.action=='load':print(json.dumps(recipients()))
        elif a.action=='save':write('recipients.json',json.dumps(validate(json.loads(sys.stdin.read(16384))),indent=2)+'\n')
        elif a.action=='setup':
            if not sys.stdin.isatty():raise ValueError('Interactive terminal required')
            with warnings.catch_warnings():
                warnings.simplefilter('error',getpass.GetPassWarning)
                pw=getpass.getpass('CONFIDENTIAL !!! WOO WOO WOO !!! CONFIDENTIAL !!! What is the password (Ctrl V): ')
            if not pw or '\n' in pw or '\r' in pw:raise ValueError('Enter a nonempty single-line password')
            write('smtp-password',pw+'\n');print('Password saved privately (mode 600). No email sent.')
        else:send(a.entry_root)
if __name__=='__main__':
    try:main()
    except (Exception,KeyboardInterrupt) as e:
        print('Invitation operation failed: '+type(e).__name__,file=sys.stderr);sys.exit(1)
