/* Only game pages that explicitly include this script report presence. */
(()=>{'use strict';if(!location.pathname.startsWith('/nov-game/')||location.pathname.startsWith('/nov-game/VVWK/'))return;
const note=document.createElement('p');note.textContent='Returning-player connection check is active for previously enrolled browsers. Last game page and IP are saved locally.';document.body.append(note);
let busy=false;async function beat(){if(busy||document.hidden)return;busy=true;try{const r=await fetch('/nov-game/VVWK/api/enrollment',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:'heartbeat',page:location.pathname})});if(r.status===403){note.textContent='No valid existing enrollment. Enrollment is closed.';return;}if(!r.ok)throw Error();const d=await r.json();note.textContent='Recognized player: '+d.name+' (local game presence active)';}catch(e){note.textContent='Player recognition unavailable.';}finally{busy=false;}}
beat();setInterval(beat,30000);document.addEventListener('visibilitychange',beat);
})();
