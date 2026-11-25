#!/usr/bin/env python3
"""Shared spoken-text normalizer for AncesTale narration.

Mirrors the JavaScript implementation embedded in session/web/narration.js
(window.AncesTaleSpeakText). Both must stay in sync; verify with:
    python3 voice/speaktext.py --selftest
Rules, in order:
  1. Strip provenance codes: [TG123456] / TG123456 -> removed.
  2. Dates "22 Jan 1826" / "11 June 1904" -> "the twenty-second of January, eighteen twenty-six,".
  3. Decades "1800s" / "1870s" -> "eighteen hundreds" / "eighteen seventies".
  4. Bare years 1000-2099 -> spoken year ("1904" -> "nineteen oh four").
  5. Remaining integers -> words; a short pause (" --") is added when a
     number word is followed by a lowercase word (e.g. "6 went" -> "six -- went").
Displayed text is never changed; only the text sent to speech.
"""
import re, sys, json, pathlib

ONES = ['zero','one','two','three','four','five','six','seven','eight','nine',
        'ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen',
        'seventeen','eighteen','nineteen']
TENS = ['','','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']
ORD1 = ['','first','second','third','fourth','fifth','sixth','seventh','eighth',
        'ninth','tenth','eleventh','twelfth','thirteenth','fourteenth','fifteenth',
        'sixteenth','seventeenth','eighteenth','nineteenth']
TENS_ORD = ['','','twentieth','thirtieth','fortieth','fiftieth','sixtieth',
            'seventieth','eightieth','ninetieth']
DECADE_TENS = {20:'twenties',30:'thirties',40:'forties',50:'fifties',60:'sixties',
               70:'seventies',80:'eighties',90:'nineties'}
MONTHS = {'jan':'January','feb':'February','mar':'March','apr':'April','may':'May',
          'jun':'June','jul':'July','aug':'August','sep':'September','oct':'October',
          'nov':'November','dec':'December'}
MONTH_RE = (r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|'
            r'Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)')


def num_words(n):
    n = int(n)
    if n < 0:
        return 'minus ' + num_words(-n)
    if n < 20:
        return ONES[n]
    if n < 100:
        t, o = divmod(n, 10)
        return TENS[t] + ('' if o == 0 else '-' + ONES[o])
    if n < 1000:
        h, r = divmod(n, 100)
        return ONES[h] + ' hundred' + ('' if r == 0 else ' ' + num_words(r))
    if n < 1000000:
        th, r = divmod(n, 1000)
        return num_words(th) + ' thousand' + ('' if r == 0 else ' ' + num_words(r))
    return str(n)


def ordinal(n):
    n = int(n)
    if 0 < n < 20:
        return ORD1[n]
    if n < 100:
        t, o = divmod(n, 10)
        if o == 0:
            return TENS_ORD[t]
        return TENS[t] + '-' + ORD1[o]
    return num_words(n) + 'th'


def year_words(y):
    y = int(y)
    if y == 2000:
        return 'two thousand'
    if 2000 < y <= 2099:
        yy = y - 2000
        return 'twenty' + ('' if yy == 0 else ' ' + ('oh ' + ONES[yy] if yy < 10 else num_words(yy)))
    if 1000 <= y <= 1999:
        c, yy = divmod(y, 100)
        if yy == 0:
            return num_words(c) + ' hundred'
        return num_words(c) + ' ' + ('oh ' + ONES[yy] if yy < 10 else num_words(yy))
    return num_words(y)


def decade_words(y):
    y = int(y)
    c, yy = divmod(y, 100)
    if yy == 0:
        return num_words(c) + ' hundreds'
    if yy in DECADE_TENS:
        return num_words(c) + ' ' + DECADE_TENS[yy]
    if yy < 20:
        return num_words(c) + ' ' + ONES[yy] + 's'
    t = yy // 10 * 10
    return num_words(c) + ' ' + DECADE_TENS.get(t, TENS[t])


def speak_text(t):
    t = str(t)
    t = re.sub(r'\[?\s*TG[0-9]{6}\s*\]?', ' ', t, flags=re.I)

    def date_sub(m):
        d, mon, y = m.group(1), m.group(2), m.group(3)
        tail = t[m.end():m.end() + 1]
        sep = '' if tail in ',.;:!?' else ','
        return 'the ' + ordinal(int(d)) + ' of ' + MONTHS[mon[:3].lower()] + ', ' + year_words(int(y)) + sep

    t = re.sub(r'\b([0-9]{1,2})(?:st|nd|rd|th)?\s+' + MONTH_RE + r'\s*,?\s+([0-9]{4})\b',
               date_sub, t, flags=re.I)
    t = re.sub(r'\b(1[0-9]{3})s\b', lambda m: decade_words(int(m.group(1))), t)
    t = re.sub(r'\b(1[0-9]{3}|20[0-9]{2})\b', lambda m: year_words(int(m.group(1))), t)

    def num_sub(m):
        s = m.group(0)
        rest = t[m.end():]
        return num_words(int(s)) + (' --' if re.match(r'^ [a-z]', rest) else '')

    t = re.sub(r'\b[0-9]+\b', num_sub, t)
    t = re.sub(r'\[\s*\]', '', t)
    t = re.sub(r'\s+([,.;:!?])', r'\1', t)
    t = re.sub(r'\s{2,}', ' ', t).strip()
    return t


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--selftest':
        cases = [
            ('Kiehlbauch [TG453802] was born 22 Jan 1826 in Neuberg',
             'Kiehlbauch was born the twenty-second of January, eighteen twenty-six, in Neuberg'),
            ('died 11 June 1904 in North Dakota',
             'died the eleventh of June, nineteen oh four, in North Dakota'),
            ('Neuberg, Kherson, early 1800s. the 1870s; mid-1800s',
             'Neuberg, Kherson, early eighteen hundreds. the eighteen seventies; mid-eighteen hundreds'),
            ('a Bremen 1873 manifest. 6 went to Tyndall',
             'a Bremen eighteen seventy-three manifest. six -- went to Tyndall'),
            ('Activity 1 — put the events in order', 'Activity one — put the events in order'),
            ('1850 → 1856 → 1880 → 1902', 'eighteen fifty → eighteen fifty-six → eighteen eighty → nineteen oh two'),
        ]
        ok = True
        for src, want in cases:
            got = speak_text(src)
            flag = 'OK ' if got == want else 'FAIL'
            if got != want:
                ok = False
            print(f'{flag} {src!r}\n     -> {got!r}')
        sys.exit(0 if ok else 1)
    lines = json.loads(pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else
                                  pathlib.Path(__file__).parent / 'narration-lines.json').read_text())
    print(json.dumps([speak_text(x) for x in lines], ensure_ascii=False, indent=1))
