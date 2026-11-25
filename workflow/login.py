#!/usr/bin/env python3
import datetime,pathlib,os
from zoneinfo import ZoneInfo
if datetime.datetime.now(ZoneInfo('America/Los_Angeles')).date()<datetime.date(2026,11,21):raise SystemExit(0)
p=pathlib.Path('/home/we6jbo/Projects/AncesTale/build/Desktop_Debug/AncesTale')
if p.is_file():os.chdir(p.parents[2]);os.execv(str(p),[str(p)])
