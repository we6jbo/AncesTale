/* AncesTale zork-style adventure — original homage to the verb-noun text adventures
 * described in "Sufficiently Educated" (TextWarden inferred paras 20-27, 79, 168:
 * Zork's mailbox opening task, verb-noun commands, menu-driven programs, BBS door games).
 * All rooms, objects and text below are original; no Zork content is reproduced.
 * Button-driven only — there is no text input anywhere.
 * Narration via AncesTaleVoice: hosted WAVs when present, local browser voice otherwise.
 * ZSTR strings are kept in one place for Piper narration generation (voice/narration-lines.json). */
(() => {
'use strict';

const ZSTR = {
  title: "THE KIEHLBAUCH-BECK TRAIL",
  intro: "A button-driven adventure across the family trail, from a prairie mailbox to a Bremen ship manifest. Use the buttons to play. Everything you need is spoken aloud too.",
  help: "Use the buttons: Go directions, Examine or Read things, Take and Drop objects, Turn the lantern on or off, Inventory, Look, Help, or Quit.",
  quit: "You quit the adventure. The trail will wait for you.",
  go_no: "You cannot go that way from here.",
  inv_some: "You are carrying: ",
  inv_none: "You are carrying nothing.",
  drop_ok: "Dropped.",
  drop_no: "You are not carrying that.",
  take_no: "Taken.",
  take_cant: "You cannot take that.",
  open_ok: "You open the mailbox. Inside is a folded letter.",
  open_no: "You cannot open that.",
  close_ok: "Closed.",
  close_no: "You cannot close that.",
  turn_on: "The lantern is lit, throwing warm light.",
  turn_off: "The lantern is off.",
  turn_no_on: "You cannot turn that on.",
  turn_no_off: "You cannot turn that off.",
  read_no: "There is nothing to read here.",
  file_no: "There is nothing to file here.",
  file_ok: "You file the Bremen manifest lead in the genealogy society archive. The Kiehlbauch-Beck trail is complete — every name and date came from the signed records, and the rest is labelled imagination.",
  win_lantern: "With the lantern lit and the letter read, the record book makes sense: the family left from Bremen or Hamburg in the 1870s.",
  ex_default: "Nothing special about that.",
  room_mailbox: "West of the Mailbox",
  room_dirtroad: "The Dirt Road",
  room_porch: "The Porch",
  room_kitchen: "The Kitchen",
  room_study: "The Study",
  room_library: "The Library",
  room_attic: "The Attic",
  room_cellar: "The Cellar",
  room_barn: "The Barn",
  room_garden: "The Garden",
  room_riverbank: "The Riverbank",
  room_townsquare: "Tyndall Town Square",
  room_trainstation: "The Rail Depot",
  room_shipdock: "The Ship Dock",
  room_courthouse: "The Courthouse",
  room_archive: "The Genealogy Archive",
  desc_mailbox_closed_letter: "You stand west of a small prairie mailbox on a dirt road. The road runs north toward a farmhouse. The mailbox is closed, and something glints inside it.",
  desc_mailbox_closed_taken: "You stand west of a small prairie mailbox on a dirt road. The road runs north toward a farmhouse. The mailbox is closed.",
  desc_mailbox_open_letter: "You stand west of a small prairie mailbox on a dirt road. The mailbox is open, and something glints inside it.",
  desc_mailbox_open_taken: "You stand west of a small prairie mailbox on a dirt road. The mailbox is open. It is empty.",
  desc_dirtroad: "A rutted dirt road runs north to the farmhouse and east toward Tyndall. The mailbox waits to the south.",
  desc_porch: "A wooden porch wraps the farmhouse. A lantern hangs by the door. The kitchen door stands to the north; the road is south, the garden east, the barn west.",
  desc_kitchen: "A pine table, a wood stove, and a window looking west over the prairie. On the table sits a family record book. The porch is south, the study north, the cellar down.",
  desc_study: "A small study with a desk and a chair. On the desk lies a census page. The kitchen is south and the library north.",
  desc_library: "Shelves of books and ledgers line the walls. A locked-looking manifest box sits on the reading table. The study is south and the attic stairs go up.",
  desc_attic: "Dusty rafters and a cedar trunk. Old photographs are pinned to the wall. The stairs go down to the library.",
  desc_cellar_dark: "A dark cellar under the farmhouse. You can barely see the stairs up.",
  desc_cellar_lit: "Lantern light shows a dirt-floored cellar with potato bins and the stairs up to the kitchen.",
  desc_barn: "A barn smelling of hay. A wagon stands ready, and a horse watches from its stall. The porch is east.",
  desc_garden: "Roses by the fence and a stone well. The riverbank is north and the porch west.",
  desc_riverbank: "A grassy bank over a slow creek. The garden is south.",
  desc_townsquare: "Tyndall's square: a hotel, a general store, and a notice board. The courthouse is north, the rail depot east, the dirt road west.",
  desc_trainstation: "A wooden depot with a schedule board. Rails run north toward the ship dock at the river. The town square is west.",
  desc_shipdock: "Planks over the water, a crane, and a crate marked BREMEN. The depot is south.",
  desc_courthouse: "A brick courthouse with a records office inside. The archive is north and the square south.",
  desc_archive: "The genealogy society back room: filing cabinets, a microfilm reader, and a desk for new leads. The courthouse is south.",
  ex_mailbox_open: "The mailbox is open. ",
  ex_mailbox_closed: "A small prairie mailbox. Try: Open mailbox.",
  ex_letter_here: "A letter from the county genealogy society. Try: Read letter.",
  ex_letter_carried: "A letter from the county genealogy society. Try: Read letter.",
  ex_letter_none: "You do not see that here.",
  ex_lantern_lit: "A kerosene lantern. It is lit, throwing warm light.",
  ex_lantern_unlit: "A kerosene lantern. It is unlit. Try: Turn on lantern.",
  ex_door: "The kitchen door. It opens to the north.",
  ex_book: "A family record book. The pages list names and dates from the signed records. Try: Read book.",
  ex_stove: "A cast-iron wood stove, cold.",
  ex_window: "West over the prairie you can see the dirt road and, far off, the mailbox.",
  ex_census: "A census page: a household listed in Bon Homme County, South Dakota. Try: Read census.",
  ex_manifest_box: "A box marked SHIP MANIFESTS. Try: Take manifest.",
  ex_manifest_carried: "The Bremen manifest pages. Try: Read manifest, or carry them to the archive and File manifest.",
  ex_trunk: "A cedar trunk with old photographs pinned above it. Try: Examine photos.",
  ex_photos: "Photographs of a prairie farmhouse and a family group, all unlabelled.",
  ex_wagon: "A farm wagon, ready to roll.",
  ex_horse: "A bay horse, saddled and patient.",
  ex_well: "A stone well with a rope and bucket.",
  ex_roses: "Roses climbing the garden fence.",
  ex_creek: "The creek runs slow and brown over gravel.",
  ex_board: "A notice board. Try: Read board.",
  ex_schedule: "A rail schedule. Try: Read schedule.",
  ex_crate: "A crate stencilled BREMEN 1873.",
  ex_crane: "A dock crane for loading cargo.",
  ex_records: "Cabinets of county records. Try: Examine cabinets.",
  ex_cabinets: "Cabinet after cabinet of bound volumes.",
  read_letter_main: "The letter reads: \"Dear researcher, the Kiehlbauch-Beck file has a new lead: a ship manifest from Bremen, 1873. The society meets Thursday at the Tyndall library.\" You pocket the letter.",
  read_letter_again: "You re-read the letter: a Bremen 1873 manifest lead. The society meets Thursday at the Tyndall library.",
  read_book: "The record book lists Joseph Kiehlbauch [TG453802] of Neuberg, his wife Johanna [TG171824], and their son Josef [TG274361], born 1850, later of Chicago. A margin note says: embarked Bremen or Hamburg, 1870s. Try: Find the manifest.",
  read_census: "The census page lists a household in Bon Homme County with names matching the record book.",
  read_manifest: "The manifest lists passengers from the Black Sea German colonies, Bremen 1873, among them a Kiehlbauch family. Carry it to the archive and File manifest.",
  read_board: "The notice board: church supper Saturday; lost dog; county fair next month.",
  read_schedule: "The schedule: a morning train west to Chicago, an evening local to Yankton.",
};

const state = { room: 'mailbox', inv: [], mailboxOpen: false, letterRead: false, lanternLit: false, manifestTaken: false, filed: false, over: false };

const DIRS = { n: 'north', s: 'south', e: 'east', w: 'west', u: 'up', d: 'down', north: 'north', south: 'south', east: 'east', west: 'west', up: 'up', down: 'down' };

const rooms = {
  mailbox: {
    name: ZSTR.room_mailbox,
    desc: () => !state.mailboxOpen ? (state.inv.includes('letter') ? ZSTR.desc_mailbox_closed_taken : ZSTR.desc_mailbox_closed_letter)
      : (state.inv.includes('letter') ? ZSTR.desc_mailbox_open_taken : ZSTR.desc_mailbox_open_letter),
    exits: { north: 'dirtroad' },
    buttons: () => {
      const b = [];
      b.push([state.mailboxOpen ? 'Close mailbox' : 'Open mailbox', state.mailboxOpen ? 'close mailbox' : 'open mailbox']);
      if (state.mailboxOpen && !state.inv.includes('letter')) { b.push(['Read letter', 'read letter']); b.push(['Take letter', 'take letter']); }
      if (state.inv.includes('letter')) { b.push(['Read letter', 'read letter']); b.push(['Drop letter', 'drop letter']); }
      b.push(['Examine mailbox', 'examine mailbox']);
      return b;
    },
  },
  dirtroad: {
    name: ZSTR.room_dirtroad, desc: () => ZSTR.desc_dirtroad,
    exits: { south: 'mailbox', north: 'porch', east: 'townsquare' },
    buttons: () => [['Examine road', 'examine road']],
  },
  porch: {
    name: ZSTR.room_porch, desc: () => ZSTR.desc_porch,
    exits: { south: 'dirtroad', north: 'kitchen', east: 'garden', west: 'barn' },
    buttons: () => {
      const b = [];
      if (!state.inv.includes('lantern')) b.push(['Take lantern', 'take lantern']);
      else { b.push([state.lanternLit ? 'Turn off lantern' : 'Turn on lantern', state.lanternLit ? 'turn off lantern' : 'turn on lantern']); b.push(['Drop lantern', 'drop lantern']); }
      b.push(['Examine lantern', 'examine lantern'], ['Examine door', 'examine door']);
      return b;
    },
  },
  kitchen: {
    name: ZSTR.room_kitchen, desc: () => ZSTR.desc_kitchen,
    exits: { south: 'porch', north: 'study', down: 'cellar' },
    buttons: () => [['Read book', 'read book'], ['Examine book', 'examine book'], ['Examine stove', 'examine stove'], ['Examine window', 'examine window']],
  },
  study: {
    name: ZSTR.room_study, desc: () => ZSTR.desc_study,
    exits: { south: 'kitchen', north: 'library' },
    buttons: () => [['Read census', 'read census'], ['Examine census', 'examine census']],
  },
  library: {
    name: ZSTR.room_library, desc: () => ZSTR.desc_library,
    exits: { south: 'study', up: 'attic' },
    buttons: () => {
      const b = [];
      if (!state.manifestTaken) b.push(['Take manifest', 'take manifest']);
      if (state.inv.includes('manifest')) { b.push(['Read manifest', 'read manifest']); b.push(['Drop manifest', 'drop manifest']); }
      b.push(['Examine manifest box', 'examine manifest box']);
      return b;
    },
  },
  attic: {
    name: ZSTR.room_attic,
    desc: () => ZSTR.desc_attic,
    exits: { down: 'library' },
    buttons: () => [['Examine trunk', 'examine trunk'], ['Examine photos', 'examine photos']],
  },
  cellar: {
    name: ZSTR.room_cellar,
    desc: () => state.lanternLit ? ZSTR.desc_cellar_lit : ZSTR.desc_cellar_dark,
    exits: { up: 'kitchen' },
    buttons: () => [['Examine cellar', 'examine cellar']],
  },
  barn: {
    name: ZSTR.room_barn, desc: () => ZSTR.desc_barn,
    exits: { east: 'porch' },
    buttons: () => [['Examine wagon', 'examine wagon'], ['Examine horse', 'examine horse']],
  },
  garden: {
    name: ZSTR.room_garden, desc: () => ZSTR.desc_garden,
    exits: { west: 'porch', north: 'riverbank' },
    buttons: () => [['Examine well', 'examine well'], ['Examine roses', 'examine roses']],
  },
  riverbank: {
    name: ZSTR.room_riverbank, desc: () => ZSTR.desc_riverbank,
    exits: { south: 'garden' },
    buttons: () => [['Examine creek', 'examine creek']],
  },
  townsquare: {
    name: ZSTR.room_townsquare, desc: () => ZSTR.desc_townsquare,
    exits: { west: 'dirtroad', north: 'courthouse', east: 'trainstation' },
    buttons: () => [['Read board', 'read board'], ['Examine board', 'examine board']],
  },
  trainstation: {
    name: ZSTR.room_trainstation, desc: () => ZSTR.desc_trainstation,
    exits: { west: 'townsquare', north: 'shipdock' },
    buttons: () => [['Read schedule', 'read schedule'], ['Examine schedule', 'examine schedule']],
  },
  shipdock: {
    name: ZSTR.room_shipdock, desc: () => ZSTR.desc_shipdock,
    exits: { south: 'trainstation' },
    buttons: () => [['Examine crate', 'examine crate'], ['Examine crane', 'examine crane']],
  },
  courthouse: {
    name: ZSTR.room_courthouse, desc: () => ZSTR.desc_courthouse,
    exits: { south: 'townsquare', north: 'archive' },
    buttons: () => [['Examine records', 'examine records'], ['Examine cabinets', 'examine cabinets']],
  },
  archive: {
    name: ZSTR.room_archive, desc: () => ZSTR.desc_archive,
    exits: { south: 'courthouse' },
    buttons: () => {
      const b = [];
      if (state.inv.includes('manifest')) b.push(['File manifest', 'file manifest']);
      return b;
    },
  },
};

function out(log, text, cls) {
  const p = document.createElement('p');
  if (cls) p.className = cls;
  p.textContent = text;
  log.append(p);
  log.scrollTop = log.scrollHeight;
  if (cls !== 'zin' && window.AncesTaleVoice) window.AncesTaleVoice.speak(text, 'modern', true);
}

function describe(log) {
  const r = rooms[state.room];
  out(log, r.name, 'zroom');
  out(log, r.desc());
}

const EX = {
  mailbox: () => state.mailboxOpen ? ZSTR.ex_mailbox_open + (state.inv.includes('letter') ? 'It is empty.' : ZSTR.ex_letter_here) : ZSTR.ex_mailbox_closed,
  letter: () => state.inv.includes('letter') ? ZSTR.ex_letter_carried : (state.mailboxOpen && state.room === 'mailbox' ? ZSTR.ex_letter_here : ZSTR.ex_letter_none),
  lantern: () => state.lanternLit ? ZSTR.ex_lantern_lit : ZSTR.ex_lantern_unlit,
  door: () => ZSTR.ex_door,
  book: () => ZSTR.ex_book,
  stove: () => ZSTR.ex_stove,
  window: () => ZSTR.ex_window,
  census: () => ZSTR.ex_census,
  'manifest box': () => ZSTR.ex_manifest_box,
  manifest: () => state.inv.includes('manifest') ? ZSTR.ex_manifest_carried : ZSTR.ex_default,
  trunk: () => ZSTR.ex_trunk,
  photos: () => ZSTR.ex_photos,
  wagon: () => ZSTR.ex_wagon,
  horse: () => ZSTR.ex_horse,
  well: () => ZSTR.ex_well,
  roses: () => ZSTR.ex_roses,
  creek: () => ZSTR.ex_creek,
  board: () => ZSTR.ex_board,
  schedule: () => ZSTR.ex_schedule,
  crate: () => ZSTR.ex_crate,
  crane: () => ZSTR.ex_crane,
  records: () => ZSTR.ex_records,
  cabinets: () => ZSTR.ex_cabinets,
  road: () => 'The road is rutted but firm.',
  cellar: () => state.lanternLit ? ZSTR.desc_cellar_lit : ZSTR.desc_cellar_dark,
};

const READ = {
  letter: () => {
    if (state.inv.includes('letter') || (state.mailboxOpen && state.room === 'mailbox')) {
      if (!state.letterRead) { state.letterRead = true; return ZSTR.read_letter_main; }
      return ZSTR.read_letter_again;
    }
    return ZSTR.ex_letter_none;
  },
  book: () => state.room === 'kitchen' ? ZSTR.read_book : ZSTR.read_no,
  census: () => state.room === 'study' ? ZSTR.read_census : ZSTR.read_no,
  manifest: () => state.inv.includes('manifest') ? ZSTR.read_manifest : ZSTR.read_no,
  board: () => state.room === 'townsquare' ? ZSTR.read_board : ZSTR.read_no,
  schedule: () => state.room === 'trainstation' ? ZSTR.read_schedule : ZSTR.read_no,
};

const TAKE = {
  letter: () => {
    if (state.mailboxOpen && state.room === 'mailbox' && !state.inv.includes('letter')) { state.inv.push('letter'); return ZSTR.take_no; }
    return ZSTR.take_cant;
  },
  lantern: () => {
    if (state.room === 'porch' && !state.inv.includes('lantern')) { state.inv.push('lantern'); return ZSTR.take_no; }
    return ZSTR.take_cant;
  },
  manifest: () => {
    if (state.room === 'library' && !state.manifestTaken) { state.manifestTaken = true; state.inv.push('manifest'); return ZSTR.take_no; }
    return ZSTR.take_cant;
  },
};

function go(log, d) {
  const r = rooms[state.room];
  if (r.exits[d]) { state.room = r.exits[d]; describe(log); }
  else out(log, ZSTR.go_no);
}

function handle(log, cmd) {
  if (state.over && cmd !== 'quit') return;
  const c = cmd.trim().toLowerCase();
  const sp = c.indexOf(' ');
  const verb = sp === -1 ? c : c.slice(0, sp);
  const rest = sp === -1 ? '' : c.slice(sp + 1).trim();
  switch (verb) {
    case 'look': case 'l': describe(log); break;
    case 'examine': case 'x': out(log, EX[rest] ? EX[rest]() : ZSTR.ex_default); break;
    case 'read': out(log, READ[rest] ? READ[rest]() : ZSTR.read_no); break;
    case 'open': if (rest === 'mailbox' && state.room === 'mailbox') { state.mailboxOpen = true; out(log, ZSTR.open_ok); } else out(log, ZSTR.open_no); break;
    case 'close': if (rest === 'mailbox' && state.room === 'mailbox') { state.mailboxOpen = false; out(log, ZSTR.close_ok); } else out(log, ZSTR.close_no); break;
    case 'take': case 'get': out(log, TAKE[rest] ? TAKE[rest]() : ZSTR.take_cant); break;
    case 'drop': if (state.inv.includes(rest)) { state.inv.splice(state.inv.indexOf(rest), 1); out(log, ZSTR.drop_ok); } else out(log, ZSTR.drop_no); break;
    case 'inventory': case 'i': out(log, state.inv.length ? ZSTR.inv_some + state.inv.join(', ') + '.' : ZSTR.inv_none); break;
    case 'turn': {
      const on = !/off/.test(rest);
      const noun = (rest.replace(/^(on|off)\s*/, '') || '').trim();
      if (noun === 'lantern' && state.inv.includes('lantern')) {
        state.lanternLit = on;
        out(log, on ? ZSTR.turn_on : ZSTR.turn_off);
        if (on && state.letterRead && !state.filed) out(log, ZSTR.win_lantern, 'zwin');
      } else out(log, on ? ZSTR.turn_no_on : ZSTR.turn_no_off);
      break;
    }
    case 'file': if (rest === 'manifest' && state.room === 'archive' && state.inv.includes('manifest')) { state.filed = true; state.over = true; out(log, ZSTR.file_ok, 'zwin'); } else out(log, ZSTR.file_no); break;
    case 'go': { const d = DIRS[rest]; if (!d) { out(log, ZSTR.go_no); break; } go(log, d); break; }
    case 'north': case 'south': case 'east': case 'west': case 'up': case 'down': case 'n': case 's': case 'e': case 'w': case 'u': case 'd': go(log, DIRS[verb]); break;
    case 'help': out(log, ZSTR.help); break;
    case 'quit': state.over = true; out(log, ZSTR.quit, 'zwin'); break;
    default: out(log, 'I do not understand. Use the buttons.');
  }
}

function buttonRow(panel, log, refresh) {
  const bar = document.createElement('div');
  bar.className = 'zbtns';
  bar.style.cssText = 'display:flex;flex-wrap:wrap;gap:8px;margin-top:8px';
  const mk = (label, cmd) => {
    const b = document.createElement('button');
    b.type = 'button'; b.textContent = label;
    b.style.cssText = 'background:#233b40;color:#f7e8c7;border:1px solid #a6b5a1;border-radius:7px;padding:9px 13px;font:inherit;cursor:pointer';
    b.onclick = () => { out(log, '> ' + cmd, 'zin'); handle(log, cmd); refresh(); };
    bar.append(b);
  };
  mk('Look', 'look'); mk('Inventory', 'inventory'); mk('Help', 'help'); mk('Quit', 'quit');
  const r = rooms[state.room];
  for (const d of Object.keys(r.exits)) mk('Go ' + d, 'go ' + d);
  for (const [label, cmd] of r.buttons()) mk(label, cmd);
  panel.append(bar);
  return bar;
}

window.AncesTaleZork = {
  start(panel) {
    panel.innerHTML = '';
    const log = document.createElement('div');
    log.className = 'zlog';
    log.style.cssText = 'height:46vh;overflow-y:auto;background:#0c161b;border:1px solid #b9ae7d66;border-radius:8px;padding:10px 12px;font:14px/1.5 monospace;color:#e8dfc8;margin-bottom:8px';
    panel.append(log);
    let bar = null;
    const refresh = () => { if (bar) bar.remove(); bar = buttonRow(panel, log, refresh); };
    out(log, ZSTR.title, 'zwin');
    out(log, ZSTR.intro);
    describe(log);
    refresh();
  },
};
})();
