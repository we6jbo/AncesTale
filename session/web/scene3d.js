/* AncesTale 3D journey system. Original procedural scenery; no external assets.
 * One continuous map with locations along +x. Free-roam: arrow keys / WASD walk,
 * mouse click raycasts to the ground and the camera walks there. Scene changes
 * trigger a real-time flyover to the next location, then land back in walk mode.
 * Fictional reconstruction; verified facts stay in the page text. */
import * as THREE from 'three';

const locations = [];
const updaters = [];

export function registerLocation(id, x, builder, focus) { locations.push({ id, x, builder, focus }); }

/* ---------- shared builders ---------- */
function ground(width, depth, seg, waterRanges) {
  const g = new THREE.PlaneGeometry(width, depth, seg, 24);
  g.rotateX(-Math.PI / 2);
  const pos = g.attributes.position, colors = [];
  const grass = new THREE.Color(0x6f8f4a), wheat = new THREE.Color(0xa8a05a), sand = new THREE.Color(0xcbb27a), water = new THREE.Color(0x2e5f7a);
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), z = pos.getZ(i);
    let h = Math.sin(x * 0.05 + z * 0.04) * 1.4 + Math.sin(x * 0.13 + z * 0.11) * 0.6;
    let c = grass.clone().lerp(wheat, 0.5 + 0.5 * Math.sin(x * 0.2 + z * 0.33));
    for (const [a, b] of waterRanges) if (x > a && x < b) { h = -0.4; c = water; }
    if (Math.abs(x - 90) < 14) c.lerp(sand, 0.6);
    pos.setY(i, h); colors.push(c.r, c.g, c.b);
  }
  g.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  g.computeVertexNormals();
  return g;
}

function hut(w, d, h, wallC, roofC) {
  const g = new THREE.Group();
  const walls = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), new THREE.MeshLambertMaterial({ color: wallC }));
  walls.position.y = h / 2; walls.castShadow = true; g.add(walls);
  const roof = new THREE.Mesh(new THREE.CylinderGeometry(0.01, d * 0.72, w * 0.9, 4, 1), new THREE.MeshLambertMaterial({ color: roofC }));
  roof.rotation.y = Math.PI / 4; roof.rotation.z = Math.PI / 2; roof.scale.z = 0.8;
  roof.position.y = h + w * 0.32; roof.castShadow = true; g.add(roof);
  return g;
}

function tree(h) {
  const t = new THREE.Group();
  const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.3, h, 8), new THREE.MeshLambertMaterial({ color: 0x6b4a2f }));
  trunk.position.y = h / 2; trunk.castShadow = true; t.add(trunk);
  const leaf = new THREE.MeshLambertMaterial({ color: 0x4d7a3a });
  for (let i = 0; i < 3; i++) {
    const b = new THREE.Mesh(new THREE.SphereGeometry(h * (0.55 - i * 0.13), 10, 8), leaf);
    b.position.y = h + i * h * 0.3; b.castShadow = true; t.add(b);
  }
  return t;
}

function cloud(scale) {
  const mat = new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.88 });
  const c = new THREE.Group();
  const n = 4 + Math.floor(Math.random() * 3);
  for (let i = 0; i < n; i++) {
    const s = new THREE.Mesh(new THREE.SphereGeometry(1, 10, 8), mat);
    s.position.set((i - n / 2) * 1.6, Math.random() * 0.5, Math.random() * 1.2 - 0.6);
    s.scale.set(1.6 + Math.random(), 0.7 + Math.random() * 0.4, 1 + Math.random() * 0.6);
    c.add(s);
  }
  c.scale.setScalar(scale); return c;
}

function bird() {
  const g = new THREE.Group();
  const mat = new THREE.MeshBasicMaterial({ color: 0x222831, side: THREE.DoubleSide });
  for (const s of [-1, 1]) {
    const w = new THREE.Mesh(new THREE.PlaneGeometry(0.7, 0.25), mat);
    w.rotation.z = s * 0.5; w.position.x = s * 0.35; g.add(w);
  }
  return g;
}

function ship(big) {
  const g = new THREE.Group();
  const hullMat = new THREE.MeshLambertMaterial({ color: 0x5a3d24 });
  const hull = new THREE.Mesh(new THREE.BoxGeometry(big ? 9 : 6, 1.4, 2.6), hullMat);
  hull.position.y = 0.7; hull.castShadow = true; g.add(hull);
  const bow = new THREE.Mesh(new THREE.ConeGeometry(1.3, 2.4, 4), hullMat);
  bow.rotation.z = -Math.PI / 2; bow.rotation.y = Math.PI / 4; bow.position.set((big ? 9 : 6) / 2 + 1, 0.7, 0); g.add(bow);
  const mastMat = new THREE.MeshLambertMaterial({ color: 0x3c2a18 });
  const sailMat = new THREE.MeshLambertMaterial({ color: 0xf2ead2, side: THREE.DoubleSide });
  const masts = big ? 3 : 2;
  for (let i = 0; i < masts; i++) {
    const mast = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.12, big ? 7 : 5.5, 6), mastMat);
    mast.position.set((i - (masts - 1) / 2) * (big ? 3 : 2.4), (big ? 7 : 5.5) / 2 + 1.4, 0); g.add(mast);
    const sail = new THREE.Mesh(new THREE.PlaneGeometry(big ? 2.6 : 2, big ? 3.4 : 2.6), sailMat);
    sail.position.set((i - (masts - 1) / 2) * (big ? 3 : 2.4), big ? 5 : 4, 0); g.add(sail);
  }
  return g;
}

/* ---------- locations ---------- */
registerLocation('neuberg', 0, (g) => {
  for (let i = 0; i < 5; i++) {
    const h = hut(2.2, 2.6, 1.8, 0xd8c9a3, 0x8a2f2b);
    h.position.set(-8 + i * 4, 0, -6 + (i % 2) * 3); h.rotation.y = (i % 2 ? 0.2 : -0.15); g.add(h);
  }
  const field = new THREE.Mesh(new THREE.PlaneGeometry(26, 14), new THREE.MeshLambertMaterial({ color: 0xb3a45e }));
  field.rotation.x = -Math.PI / 2; field.position.set(0, 0.05, 8); field.receiveShadow = true; g.add(field);
  for (const [x, z] of [[-12, -12], [10, -10], [14, 2], [-6, 12]]) { const t = tree(3 + Math.random() * 2); t.position.set(x, 0, z); g.add(t); }
}, new THREE.Vector3(0, 2, -4));

registerLocation('odessa', 90, (g) => {
  const dock = new THREE.Mesh(new THREE.BoxGeometry(14, 0.4, 3), new THREE.MeshLambertMaterial({ color: 0x8a6f4d }));
  dock.position.set(6, 0.2, 0); dock.castShadow = true; g.add(dock);
  const s = ship(false); s.position.set(10, -0.2, 0); g.add(s);
  const crane = new THREE.Group();
  const post = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.2, 6, 6), new THREE.MeshLambertMaterial({ color: 0x444c52 }));
  post.position.y = 3; crane.add(post);
  const arm = new THREE.Mesh(new THREE.BoxGeometry(5, 0.2, 0.2), post.material);
  arm.position.set(2.4, 5.8, 0); crane.add(arm);
  crane.position.set(0, 0, 0); g.add(crane);
  for (let i = 0; i < 4; i++) {
    const c = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.8, 0.8), new THREE.MeshLambertMaterial({ color: 0x9a7b4f }));
    c.position.set(-4 + i * 1.1, 0.4, 2); c.castShadow = true; g.add(c);
  }
  const ware = hut(5, 4, 3, 0xb8a888, 0x5a4632); ware.position.set(-8, 0, -3); g.add(ware);
}, new THREE.Vector3(90, 2, -2));

registerLocation('atlantic', 180, (g) => {
  const s = ship(true); s.position.set(0, 0, 0); g.add(s);
  updaters.push((t) => { s.position.y = Math.sin(t * 0.8) * 0.25; s.rotation.z = Math.sin(t * 0.6) * 0.04; s.position.x = Math.sin(t * 0.05) * 3; });
}, new THREE.Vector3(180, 3, 0));

registerLocation('chicago', 280, (g) => {
  const cols = [0x8a4a3a, 0x9a5a40, 0x7a4a52, 0x6b4a3a];
  for (let i = 0; i < 9; i++) {
    const h = 4 + Math.random() * 9;
    const b = new THREE.Mesh(new THREE.BoxGeometry(3 + Math.random() * 2, h, 3 + Math.random() * 2),
      new THREE.MeshLambertMaterial({ color: cols[i % cols.length] }));
    b.position.set(-14 + (i % 5) * 7, h / 2, -8 + Math.floor(i / 5) * 8);
    b.castShadow = true; g.add(b);
  }
  const railMat = new THREE.MeshLambertMaterial({ color: 0x555c62 });
  for (const z of [-1, 1]) { const r = new THREE.Mesh(new THREE.BoxGeometry(30, 0.1, 0.15), railMat); r.position.set(0, 0.08, z); g.add(r); }
  const train = new THREE.Group();
  const loco = new THREE.Mesh(new THREE.BoxGeometry(3, 2.2, 1.6), new THREE.MeshLambertMaterial({ color: 0x2c3e50 }));
  loco.position.y = 1.2; loco.castShadow = true; train.add(loco);
  for (let i = 0; i < 3; i++) {
    const car = new THREE.Mesh(new THREE.BoxGeometry(3.4, 2, 1.6), new THREE.MeshLambertMaterial({ color: 0x7a3b2e }));
    car.position.set(-4.2 - i * 3.8, 1.1, 0); car.castShadow = true; train.add(car);
  }
  train.position.set(0, 0, 0); g.add(train);
  updaters.push((t) => { train.position.x = -14 + ((t * 6) % 28); });
}, new THREE.Vector3(280, 4, -6));

registerLocation('tyndall', 380, (g) => {
  const home = hut(6, 4, 3, 0xd8c9a3, 0x8a2f2b); home.position.set(0, 0, -6); g.add(home);
  const door = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 2), new THREE.MeshLambertMaterial({ color: 0x4a3320 }));
  door.position.set(0, 1, -3.99); g.add(door);
  const mill = new THREE.Group();
  const tower = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.9, 7, 8, 1, true), new THREE.MeshLambertMaterial({ color: 0x9aa3a8, wireframe: true }));
  tower.position.y = 3.5; tower.castShadow = true; mill.add(tower);
  const hub = new THREE.Group(); hub.position.set(0, 7.2, 0.7); mill.add(hub);
  const bm = new THREE.MeshLambertMaterial({ color: 0xe8e4d8, side: THREE.DoubleSide });
  for (let i = 0; i < 8; i++) {
    const w = new THREE.Group(); w.rotation.z = (i / 8) * Math.PI * 2;
    const b = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 3.2), bm); b.position.y = 1.8; w.add(b); hub.add(w);
  }
  mill.position.set(7, 0, -10); g.add(mill);
  updaters.push((t) => { hub.rotation.z = t * 0.9; });
  const fence = new THREE.Group();
  const fm = new THREE.MeshLambertMaterial({ color: 0x8a6f4d });
  for (let i = 0; i <= 8; i++) {
    const p = new THREE.Mesh(new THREE.BoxGeometry(0.12, 1.1, 0.12), fm); p.position.set(i * 1.2 - 4.8, 0.55, 0); p.castShadow = true; fence.add(p);
    if (i < 8) { const r = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.08, 0.05), fm); r.position.set(i * 1.2 - 4.2, 0.85, 0); fence.add(r); }
  }
  fence.position.set(-2, 0, 2.5); g.add(fence);
  const wagon = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.7, 1.3), new THREE.MeshLambertMaterial({ color: 0x7a4a2a }));
  body.position.y = 0.9; body.castShadow = true; wagon.add(body);
  const wm = new THREE.MeshLambertMaterial({ color: 0x3a2c1c });
  for (const [x, z] of [[-0.9, 0.75], [0.9, 0.75], [-0.9, -0.75], [0.9, -0.75]]) {
    const w = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.55, 0.12, 14), wm);
    w.rotation.x = Math.PI / 2; w.position.set(x, 0.55, z); w.castShadow = true; wagon.add(w);
  }
  wagon.position.set(4.5, 0, 3); wagon.rotation.y = -0.3; g.add(wagon);
  for (const [x, z, h] of [[-9, -14, 4.5], [11, -4, 5.5], [-13, 6, 3.8]]) { const t = tree(h); t.position.set(x, 0, z); g.add(t); }
}, new THREE.Vector3(380, 2.5, -4));

/* ---------- world / renderer / controls ---------- */
let renderer = null, camera = null, scene = null, raf = 0;
let camPos = new THREE.Vector3(200, 2.4, 16), focusWorld = new THREE.Vector3(200, 2.5, -10), traveling = null;
const WORLD_W = 460, WORLD_OFF = WORLD_W / 2 - 30, WATER = [[150, 222]];
const EYE = 2.4;

function buildWorld() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xbfd9e8);
  scene.fog = new THREE.Fog(0xbfd9e8, 120, 380);
  scene.add(new THREE.HemisphereLight(0xcfe8ff, 0x7a8a5a, 0.95));
  const sun = new THREE.DirectionalLight(0xffe3b3, 1.5);
  sun.position.set(60, 60, -40); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.left = -240; sun.shadow.camera.right = 240;
  sun.shadow.camera.top = 120; sun.shadow.camera.bottom = -120;
  scene.add(sun);
  const g = new THREE.Mesh(ground(WORLD_W, 160, 90, WATER), new THREE.MeshLambertMaterial({ vertexColors: true }));
  g.position.x = WORLD_OFF; g.receiveShadow = true; scene.add(g);
  const clouds = [];
  for (let i = 0; i < 10; i++) {
    const c = cloud(3 + Math.random() * 4);
    c.position.set(Math.random() * WORLD_W + WORLD_OFF, 26 + Math.random() * 12, (Math.random() - 0.5) * 120);
    scene.add(c); clouds.push(c);
  }
  const birds = [];
  for (let i = 0; i < 6; i++) {
    const b = bird(); scene.add(b);
    birds.push({ m: b, r: 18 + i * 5, h: 16 + i * 2, s: 0.1 + i * 0.02, off: i * 1.7, cx: WORLD_OFF + Math.random() * WORLD_W });
  }
  for (const loc of locations) {
    const grp = new THREE.Group(); grp.position.x = loc.x + WORLD_OFF;
    loc.builder(grp); scene.add(grp);
  }
  updaters.push((t) => {
    clouds.forEach((c, i) => { c.position.x += 0.008 * (1 + i * 0.15); if (c.position.x > WORLD_OFF + WORLD_W + 30) c.position.x = WORLD_OFF - 30; });
    for (const b of birds) {
      const a = t * b.s + b.off;
      b.m.position.set(b.cx + Math.cos(a) * b.r, b.h + Math.sin(t * 0.7 + b.off), Math.sin(a) * b.r * 0.4);
      b.m.rotation.y = -a;
    }
  });
}

function locFocus(i) { return locations[Math.max(0, Math.min(locations.length - 1, i))]; }

function animate() {
  raf = requestAnimationFrame(animate);
  const t = performance.now() / 1000;
  for (const u of updaters) u(t);
  if (traveling) {
    const p = Math.min(1, (performance.now() - traveling.t0) / traveling.dur);
    const e = p * p * (3 - 2 * p);
    camPos.lerpVectors(traveling.from, traveling.to, e);
    camPos.y = EYE + Math.sin(Math.PI * e) * 26;
    camera.position.copy(camPos);
    camera.lookAt(traveling.focus);
    if (p >= 1) { focusWorld.copy(traveling.focus); camPos.copy(traveling.to); camPos.y = EYE; traveling = null; }
  } else {
    camera.position.set(camPos.x + Math.sin(t * 0.12) * 2.2, EYE + Math.sin(t * 0.3) * 0.12, camPos.z + Math.cos(t * 0.1) * 1.2);
    camera.lookAt(focusWorld);
  }
  renderer.render(scene, camera);
}

export function mount(canvas, startLoc = 0) {
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  camera = new THREE.PerspectiveCamera(60, 1, 0.1, 600);
  buildWorld();
  const f = locFocus(startLoc).focus;
  camPos.set(f.x + WORLD_OFF, EYE, 16);
  focusWorld.set(f.x + WORLD_OFF, 2.5, f.z - 6);
  const resize = () => {
    const w = canvas.clientWidth || 600, h = canvas.clientHeight || 300;
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
  };
  window.addEventListener('resize', resize); resize();
  cancelAnimationFrame(raf); animate();
  return { dispose() { cancelAnimationFrame(raf); window.removeEventListener('resize', resize); renderer.dispose(); } };
}

export function travelTo(locIndex, dur = 5200) {
  if (!locations.length) return;
  const f = locFocus(locIndex).focus;
  traveling = { from: camPos.clone(), to: new THREE.Vector3(f.x + WORLD_OFF, EYE, 16), focus: new THREE.Vector3(f.x + WORLD_OFF, 2.5, f.z - 6), t0: performance.now(), dur };
}

window.AncesTaleScene3D = { register: registerLocation, mount, travelTo };

document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('scene3d');
  if (canvas) { try { window.AncesTaleScene3D.mount(canvas, 0); } catch (e) { canvas.style.display = 'none'; } }
});
