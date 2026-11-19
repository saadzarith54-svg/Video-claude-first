// HTK & Piala Pengarah Ragbi — 3D announcement (deterministic: renderAt(t) draws the frame at time t seconds)
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const q = new URLSearchParams(location.search);
const W = +(q.get('w') || 540), H = +(q.get('h') || 960);
const DURATION = 20;

// ---------- easing / helpers ----------
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const prog = (t, a, b) => clamp((t - a) / (b - a));
const lerp = (a, b, k) => a + (b - a) * k;
const eInOut = k => k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
const eOut = k => 1 - Math.pow(1 - k, 3);
const eOut5 = k => 1 - Math.pow(1 - k, 5);
const eIn = k => k * k * k;
const eExpo = k => k === 1 ? 1 : 1 - Math.pow(2, -10 * k);
const eBack = (k, s = 1.9) => 1 + (s + 1) * Math.pow(k - 1, 3) + s * Math.pow(k - 1, 2);
const v3 = (x, y, z) => new THREE.Vector3(x, y, z);
let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;

// ---------- palette ----------
const C = { navy: '#0A1A44', deep: '#050D26', royal: '#1846C8', royal2: '#0E2E8E', gold: '#F2B630', goldL: '#FFD66B', white: '#FFFFFF', mute: '#9DB2E8', ink: '#0B1D52' };

// ---------- renderer ----------
const stage = document.getElementById('stage');
stage.style.width = W + 'px'; stage.style.height = H + 'px';
stage.style.setProperty('--u', (W / 1080) + 'px');
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H);
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
stage.prepend(renderer.domElement);

const camera = new THREE.PerspectiveCamera(35, W / H, 0.05, 600);
const pmrem = new THREE.PMREMGenerator(renderer);

// ======================================================================
//  CANVAS TEXT HELPERS
// ======================================================================
const F = (w, s) => `${w} ${s}px IDX`;
function rrect(g, x, y, w, h, r) { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); }
function fitText(g, text, weight, size, maxW) { let s = size; g.font = F(weight, s); while (g.measureText(text).width > maxW && s > 8) { s -= 2; g.font = F(weight, s); } return s; }
function makeCanvas(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
function texFrom(c) { const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; }

// ======================================================================
//  STADIUM SCENE
// ======================================================================
const stadium = new THREE.Scene();
stadium.background = new THREE.Color('#02050f');
stadium.fog = new THREE.FogExp2('#030a22', 0.0075);

// night env map for reflections (floodlight strips on dark)
(function () {
  const es = new THREE.Scene(); es.background = new THREE.Color('#03060f');
  const em = new THREE.MeshBasicMaterial({ color: new THREE.Color(6, 5.6, 4.8) });
  for (const [x, y, z] of [[-30, 25, -30], [30, 25, -30], [-30, 25, 30], [30, 25, 30]]) { const b = new THREE.Mesh(new THREE.BoxGeometry(14, 5, 1), em); b.position.set(x, y, z); b.lookAt(0, 0, 0); es.add(b); }
  const fl = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), new THREE.MeshBasicMaterial({ color: '#0c2010' })); fl.rotation.x = -Math.PI / 2; fl.position.y = -5; es.add(fl);
  const sky = new THREE.Mesh(new THREE.SphereGeometry(150, 32, 16), new THREE.MeshBasicMaterial({ color: '#0a1638', side: THREE.BackSide })); es.add(sky);
  stadium.environment = pmrem.fromScene(es, 0.02).texture;
})();

// field texture (70 x 100 m)
function fieldTexture() {
  const c = makeCanvas(1400, 2000), g = c.getContext('2d');
  const k = 20; // px per metre
  for (let i = 0; i < 20; i++) { g.fillStyle = i % 2 ? '#164a1f' : '#1c5826'; g.fillRect(0, i * 100, 1400, 100); }
  seed = 3; for (let i = 0; i < 60000; i++) { g.fillStyle = `rgba(${rnd() < .5 ? '0,0,0' : '120,170,90'},${.05 + rnd() * .06})`; g.fillRect(rnd() * 1400, rnd() * 2000, 2, 3); }
  g.strokeStyle = 'rgba(250,250,245,.95)'; g.lineWidth = 5;
  const X = m => 700 + m * k, Z = m => 1000 + m * k;
  g.strokeRect(X(-34), Z(-48), 68 * k, 96 * k);
  const line = (z, dash) => { g.setLineDash(dash || []); g.beginPath(); g.moveTo(X(-34), Z(z)); g.lineTo(X(34), Z(z)); g.stroke(); };
  line(0); line(-38); line(38); line(-10, [24, 18]); line(10, [24, 18]); line(-43, [12, 22]); line(43, [12, 22]);
  g.setLineDash([16, 16]); for (const x of [-29, -19, 19, 29]) { g.beginPath(); g.moveTo(X(x), Z(-48)); g.lineTo(X(x), Z(48)); g.stroke(); }
  g.setLineDash([]);
  const t = texFrom(c); return t;
}
const field = new THREE.Mesh(new THREE.PlaneGeometry(70, 100), new THREE.MeshStandardMaterial({ map: fieldTexture(), roughness: .95, metalness: 0 }));
field.rotation.x = -Math.PI / 2; field.receiveShadow = true; stadium.add(field);
const apron = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshStandardMaterial({ color: '#0b1a12', roughness: 1 }));
apron.rotation.x = -Math.PI / 2; apron.position.y = -0.02; apron.receiveShadow = true; stadium.add(apron);

// goal posts (H)
const postMat = new THREE.MeshStandardMaterial({ color: '#f4f4f0', roughness: .45, metalness: .1 });
for (const z of [-48, 48]) {
  const grp = new THREE.Group();
  for (const x of [-2.8, 2.8]) { const p = new THREE.Mesh(new THREE.CylinderGeometry(.09, .09, 14, 12), postMat); p.position.set(x, 7, 0); p.castShadow = true; grp.add(p);
    const pad = new THREE.Mesh(new THREE.CylinderGeometry(.32, .32, 2, 16), new THREE.MeshStandardMaterial({ color: '#1846C8', roughness: .6 })); pad.position.set(x, 1, 0); grp.add(pad); }
  const bar = new THREE.Mesh(new THREE.CylinderGeometry(.08, .08, 5.6, 12), postMat); bar.rotation.z = Math.PI / 2; bar.position.y = 3; grp.add(bar);
  grp.position.z = z; stadium.add(grp);
}
// stands (dark tiers) around
const standMat = new THREE.MeshStandardMaterial({ color: '#060a16', roughness: 1 });
function stand(w, d, x, z, ry) { const g = new THREE.Group(); for (let i = 0; i < 9; i++) { const b = new THREE.Mesh(new THREE.BoxGeometry(w, 1.1 * (i + 1), d / 9), standMat); b.position.set(0, .55 * (i + 1), i * d / 9); g.add(b); } g.position.set(x, 0, z); g.rotation.y = ry; stadium.add(g); }
stand(90, 16, 0, -60, 0); stand(90, 16, 0, 60, Math.PI); stand(120, 16, -46, 0, Math.PI / 2); stand(120, 16, 46, 0, -Math.PI / 2);

// floodlight towers
const beamAlpha = (() => { const c = makeCanvas(4, 256), g = c.getContext('2d'); const gr = g.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(.75, 'rgba(255,255,255,.55)'); gr.addColorStop(1, 'rgba(255,255,255,1)'); g.fillStyle = gr; g.fillRect(0, 0, 4, 256); return new THREE.CanvasTexture(c); })();
const flareTex = (() => { const c = makeCanvas(256, 256), g = c.getContext('2d'); const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(.12, 'rgba(255,245,220,.8)'); gr.addColorStop(.4, 'rgba(255,220,160,.18)'); gr.addColorStop(1, 'rgba(255,200,120,0)'); g.fillStyle = gr; g.fillRect(0, 0, 256, 256); return new THREE.CanvasTexture(c); })();
const towers = [];
const BEAM_VS = `varying vec3 vN; varying vec3 vV; varying vec2 vUv; void main(){ vUv = uv; vec4 mv = modelViewMatrix * vec4(position,1.); vV = -mv.xyz; vN = normalMatrix * normal; gl_Position = projectionMatrix * mv; }`;
const BEAM_FS = `uniform float opacity; uniform vec3 color; varying vec3 vN; varying vec3 vV; varying vec2 vUv; void main(){ float e = abs(dot(normalize(vN), normalize(vV))); e = pow(e, 2.5); float l = pow(vUv.y, 1.8); gl_FragColor = vec4(color * e * l * opacity, 1.); }`;
function tower(x, z, ign) {
  const top = v3(x, 34, z), target = v3(x * .25, 0, z > -50 ? z * .35 : -20);
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(.35, .6, 34, 8), new THREE.MeshStandardMaterial({ color: '#141c2e', roughness: .7 })); pole.position.set(x, 17, z); stadium.add(pole);
  const head = new THREE.Group(); head.position.copy(top); head.lookAt(target); stadium.add(head);
  const lampMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(0, 0, 0) });
  const frame = new THREE.Mesh(new THREE.BoxGeometry(8.6, 4.2, .5), new THREE.MeshStandardMaterial({ color: '#1a2233' })); frame.position.z = -.3; head.add(frame);
  for (let i = 0; i < 4; i++) for (let j = 0; j < 3; j++) { const l = new THREE.Mesh(new THREE.PlaneGeometry(1.7, 1.05), lampMat); l.position.set(-3.15 + i * 2.1, -1.3 + j * 1.3, .01); head.add(l); }
  const flare = new THREE.Sprite(new THREE.SpriteMaterial({ map: flareTex, color: '#fff2d8', blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, opacity: 0, fog: false }));
  flare.position.copy(top); flare.scale.set(30, 30, 1); stadium.add(flare);
  const spot = new THREE.SpotLight('#fff1dc', 0, 160, .42, .55, 1.2); spot.position.copy(top); spot.target.position.copy(target); stadium.add(spot, spot.target);
  const len = top.distanceTo(target);
  const cone = new THREE.Mesh(new THREE.CylinderGeometry(.6, 7.5, len, 48, 1, true), new THREE.ShaderMaterial({ uniforms: { opacity: { value: 0 }, color: { value: new THREE.Color('#ffe6bd') } }, vertexShader: BEAM_VS, fragmentShader: BEAM_FS, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }));
  cone.position.copy(top).add(target).multiplyScalar(.5); cone.quaternion.setFromUnitVectors(v3(0, 1, 0), top.clone().sub(target).normalize()); stadium.add(cone);
  towers.push({ lampMat, flare, spot, cone, ign });
}
tower(-11, -62, 0.20); tower(11, -62, 0.45); tower(-40, 40, 0.72); tower(40, 40, 0.90);
towers[0].spot.castShadow = true; towers[0].spot.shadow.mapSize.set(1024, 1024);
stadium.add(new THREE.HemisphereLight('#2a3d78', '#04080f', 0.18));

// dust in the beams
const dust = (() => { seed = 11; const n = 900, p = new Float32Array(n * 3); for (let i = 0; i < n; i++) { p[i * 3] = (rnd() - .5) * 60; p[i * 3 + 1] = rnd() * 22; p[i * 3 + 2] = (rnd() - .5) * 90; }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(p, 3));
  const m = new THREE.PointsMaterial({ size: .12, map: flareTex, color: '#ffe4b0', transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }); const pts = new THREE.Points(g, m); stadium.add(pts); return pts; })();

// ---------- rugby ball ----------
function ballTexture() {
  const c = makeCanvas(1024, 512), g = c.getContext('2d');
  g.fillStyle = '#f3f1ea'; g.fillRect(0, 0, 1024, 512);
  // navy & gold panel graphics (u = around, v = along)
  for (let p = 0; p < 4; p++) {
    const x0 = p * 256;
    g.fillStyle = p % 2 ? '#0E2E8E' : '#0A1A44';
    g.beginPath(); g.moveTo(x0 + 40, 0); g.bezierCurveTo(x0 + 10, 180, x0 + 10, 330, x0 + 40, 512); g.lineTo(x0 + 120, 512); g.bezierCurveTo(x0 + 70, 330, x0 + 70, 180, x0 + 120, 0); g.closePath(); g.fill();
    g.fillStyle = '#E9A92A'; g.beginPath(); g.moveTo(x0 + 128, 0); g.bezierCurveTo(x0 + 100, 180, x0 + 100, 330, x0 + 128, 512); g.lineTo(x0 + 150, 512); g.bezierCurveTo(x0 + 122, 330, x0 + 122, 180, x0 + 150, 0); g.fill();
  }
  g.strokeStyle = 'rgba(40,30,20,.75)'; g.lineWidth = 6; for (let p = 0; p < 4; p++) { g.beginPath(); g.moveTo(p * 256 + 2, 0); g.lineTo(p * 256 + 2, 512); g.stroke(); }
  // lace on one seam
  g.fillStyle = '#ffffff'; for (let i = 0; i < 8; i++) { rrect(g, -6, 190 + i * 17, 20, 9, 4); g.fill(); }
  return texFrom(c);
}
function bumpTexture() { const c = makeCanvas(1024, 512), g = c.getContext('2d'); g.fillStyle = '#808080'; g.fillRect(0, 0, 1024, 512); seed = 5; for (let i = 0; i < 26000; i++) { const x = rnd() * 1024, y = rnd() * 512; g.fillStyle = 'rgba(255,255,255,.55)'; g.beginPath(); g.arc(x, y, 1.6, 0, 7); g.fill(); } g.strokeStyle = '#202020'; g.lineWidth = 5; for (let p = 0; p < 4; p++) { g.beginPath(); g.moveTo(p * 256 + 2, 0); g.lineTo(p * 256 + 2, 512); g.stroke(); } return new THREE.CanvasTexture(c); }
function ballGeometry(L = .145, R = .097) { const pts = []; for (let i = 0; i <= 64; i++) { const y = -L + 2 * L * i / 64; const r = R * Math.pow(Math.max(0, 1 - (y / L) ** 2), .72); pts.push(new THREE.Vector2(Math.max(r, .0005), y)); } return new THREE.LatheGeometry(pts, 96); }
const ballMat = new THREE.MeshPhysicalMaterial({ map: ballTexture(), bumpMap: bumpTexture(), bumpScale: .6, roughness: .55, clearcoat: .35, clearcoatRoughness: .4, envMapIntensity: .8 });
const ball = new THREE.Mesh(ballGeometry(), ballMat); ball.castShadow = true; stadium.add(ball);
const heroKey = new THREE.SpotLight('#fff3e0', 0, 12, .5, .6, 1.5); stadium.add(heroKey, heroKey.target);
const heroRim = new THREE.SpotLight('#ffcf6a', 0, 12, .6, .6, 1.5); stadium.add(heroRim, heroRim.target);

// ---------- trophy ----------
const gold = new THREE.MeshPhysicalMaterial({ color: '#E7B14A', metalness: 1, roughness: .16, clearcoat: .4, clearcoatRoughness: .12, envMapIntensity: .75 });
const blackGloss = new THREE.MeshPhysicalMaterial({ color: '#07090f', roughness: .25, metalness: .2, clearcoat: 1, clearcoatRoughness: .05 });
const trophy = new THREE.Group();
(function () {
  const s = (r, h, y, m) => { const c = new THREE.Mesh(new THREE.CylinderGeometry(r, r * 1.04, h, 64), m); c.position.y = y; c.castShadow = c.receiveShadow = true; trophy.add(c); };
  s(.36, .08, .04, blackGloss); s(.29, .34, .25, blackGloss); s(.31, .03, .27, gold); s(.25, .05, .445, blackGloss);
  const prof = [[0, 0], [.17, 0], [.17, .025], [.13, .045], [.11, .065], [.055, .11], [.036, .15], [.03, .3], [.048, .33], [.04, .36], [.065, .385], [.16, .44], [.215, .52], [.245, .62], [.255, .72], [.27, .755], [.258, .77], [.24, .73], [.225, .63], [.19, .54], [.09, .47], [0, .46]].map(([x, y]) => new THREE.Vector2(x, y));
  const cup = new THREE.Mesh(new THREE.LatheGeometry(prof, 96), gold); cup.position.y = .47; cup.castShadow = true; trophy.add(cup);
  for (const sx of [-1, 1]) { const h = new THREE.Mesh(new THREE.TorusGeometry(.12, .017, 16, 48, Math.PI * 1.15), gold); h.position.set(sx * .245, .47 + .6, 0); h.rotation.z = sx > 0 ? -Math.PI * .58 : Math.PI * 1.58; h.castShadow = true; trophy.add(h); }
  const lid = new THREE.Mesh(new THREE.SphereGeometry(.24, 64, 24, 0, Math.PI * 2, 0, Math.PI * .32), gold); lid.position.y = .47 + .62; trophy.add(lid);
  const fin = new THREE.Mesh(ballGeometry(.075, .05), gold); fin.position.y = .47 + .9; fin.rotation.z = .5; trophy.add(fin);
  const band = new THREE.Mesh(new THREE.TorusGeometry(.256, .012, 12, 96), gold); band.rotation.x = Math.PI / 2; band.position.y = .47 + .7; trophy.add(band);
})();
trophy.position.set(0, 0, 0); trophy.scale.setScalar(1.6); stadium.add(trophy);
const teeBall = new THREE.Mesh(ballGeometry(), ballMat); teeBall.castShadow = true; teeBall.position.set(.95, .17, .55); teeBall.rotation.set(.1, .6, .28); stadium.add(teeBall);
const tee = new THREE.Mesh(new THREE.CylinderGeometry(.06, .1, .07, 24), new THREE.MeshStandardMaterial({ color: '#E9A92A', roughness: .5 })); tee.position.set(.95, .035, .55); stadium.add(tee);
const trophySpot = new THREE.SpotLight('#fff4e2', 0, 20, .32, .5, 1.2); trophySpot.position.set(1.5, 8, 2); trophySpot.target.position.set(0, .8, 0); trophySpot.castShadow = true; trophySpot.shadow.mapSize.set(1024, 1024); trophySpot.shadow.bias = -.0005; stadium.add(trophySpot, trophySpot.target);
const trophyRim = new THREE.SpotLight('#9cb6ff', 0, 20, .5, .6, 1.2); trophyRim.position.set(-3, 3, -4); trophyRim.target.position.set(0, 1, 0); stadium.add(trophyRim, trophyRim.target);
const sparkles = (() => { seed = 21; const n = 160, p = new Float32Array(n * 3), ph = []; for (let i = 0; i < n; i++) { const a = rnd() * 6.28, r = .6 + rnd() * 2.2; p[i * 3] = Math.cos(a) * r; p[i * 3 + 1] = .2 + rnd() * 3; p[i * 3 + 2] = Math.sin(a) * r; ph.push(rnd() * 6.28); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(p, 3)); const m = new THREE.PointsMaterial({ size: .06, map: flareTex, color: '#ffd77a', transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }); const s = new THREE.Points(g, m); s.userData.base = p.slice(); s.userData.ph = ph; stadium.add(s); return s; })();

// ======================================================================
//  BOARD SCENE (bento cards)
// ======================================================================
const board = new THREE.Scene();
board.environment = pmrem.fromScene(new RoomEnvironment(renderer), 0.04).texture;
board.background = (() => { const c = makeCanvas(540, 960), g = c.getContext('2d'); const gr = g.createRadialGradient(270, 400, 20, 270, 470, 720); gr.addColorStop(0, '#1a3478'); gr.addColorStop(.45, '#0b1a44'); gr.addColorStop(1, '#030816'); g.fillStyle = gr; g.fillRect(0, 0, 540, 960); return texFrom(c); })();
board.add(new THREE.HemisphereLight('#c8d6ff', '#0a1430', .55));
const key = new THREE.DirectionalLight('#ffffff', 2.2); key.position.set(-8, 14, 16); key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
Object.assign(key.shadow.camera, { left: -14, right: 14, top: 14, bottom: -14, near: 1, far: 60 }); key.shadow.radius = 6; key.shadow.bias = -.0004; board.add(key);
const boardG = new THREE.Group(); boardG.rotation.set(-0.40, 0, 0.035); board.add(boardG);
const shadowCatcher = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.ShadowMaterial({ opacity: .45 })); shadowCatcher.position.z = -.35; shadowCatcher.receiveShadow = true; boardG.add(shadowCatcher);
// gold dust behind board
const bokeh = (() => { seed = 31; const n = 120, p = new Float32Array(n * 3); for (let i = 0; i < n; i++) { p[i * 3] = (rnd() - .5) * 40; p[i * 3 + 1] = (rnd() - .5) * 50; p[i * 3 + 2] = -3 - rnd() * 12; }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(p, 3)); const m = new THREE.PointsMaterial({ size: .22, map: flareTex, color: '#f2c45a', transparent: true, opacity: .35, blending: THREE.AdditiveBlending, depthWrite: false }); const s = new THREE.Points(g, m); boardG.add(s); return s; })();

const PX = 200; // canvas px per board unit
const cards = {};
function card(name, w, h, x, y, slabColor, draw) {
  const grp = new THREE.Group(); grp.position.set(x, y, 0);
  const slabMat = new THREE.MeshPhysicalMaterial({ color: slabColor, roughness: .38, clearcoat: 1, clearcoatRoughness: .18, transparent: true });
  const slab = new THREE.Mesh(new RoundedBoxGeometry(w, h, .26, 6, .3), slabMat); slab.castShadow = true; grp.add(slab);
  const cv = makeCanvas(Math.round(w * PX), Math.round(h * PX)); const tex = texFrom(cv);
  const faceMat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, toneMapped: false });
  const face = new THREE.Mesh(new THREE.PlaneGeometry(w - .02, h - .02), faceMat); face.position.z = .131; grp.add(face);
  boardG.add(grp);
  cards[name] = { grp, slabMat, faceMat, cv, g: cv.getContext('2d'), tex, w, h, draw };
}
// layout (board units). columns 4.85 wide, gap .3
card('header', 10, 1.7, 0, 5.2, '#0E2E8E', drawHeader);
card('cal', 4.85, 5.8, -2.575, 1.2, '#123BB0', drawCal);
card('info', 4.85, 5.8, 2.575, 1.2, '#F4F6FB', drawInfo);
card('map', 10, 4.4, 0, -4.15, '#0A1A44', drawMap);

function faceBG(cd, top, bot) { const { g, cv } = cd; g.clearRect(0, 0, cv.width, cv.height); const gr = g.createLinearGradient(0, 0, cv.width * .4, cv.height); gr.addColorStop(0, top); gr.addColorStop(1, bot); g.fillStyle = gr; rrect(g, 0, 0, cv.width, cv.height, 60); g.fill();
  const sh = g.createLinearGradient(0, 0, 0, cv.height * .5); sh.addColorStop(0, 'rgba(255,255,255,.10)'); sh.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = sh; rrect(g, 0, 0, cv.width, cv.height, 60); g.fill(); }
function shine(cd, k) { if (k <= 0 || k >= 1) return; const { g, cv } = cd; const x = lerp(-cv.width * .5, cv.width * 1.5, k); g.save(); rrect(g, 0, 0, cv.width, cv.height, 60); g.clip(); const gr = g.createLinearGradient(x - 160, 0, x + 160, cv.height * .3); gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(.5, 'rgba(255,255,255,.22)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, cv.width, cv.height); g.restore(); }

function drawHeader(cd, t) {
  faceBG(cd, '#1F4FD6', '#0A2275'); const { g, cv } = cd;
  const a = eOut(prog(t, 16.55, 16.95)), b = eOut(prog(t, 16.75, 17.1));
  g.textAlign = 'center'; g.textBaseline = 'middle';
  if (a > 0) { g.globalAlpha = a; const s = fitText(g, 'HTK & PIALA PENGARAH RAGBI', 800, 104, cv.width - 160); const gr = g.createLinearGradient(0, 70, 0, 200); gr.addColorStop(0, '#FFF1BF'); gr.addColorStop(.4, '#FFD66B'); gr.addColorStop(1, '#D6951C'); g.fillStyle = gr; g.font = F(800, s); g.fillText('HTK & PIALA PENGARAH RAGBI', cv.width / 2, 140 + (1 - a) * 20); }
  if (b > 0) { g.globalAlpha = b; g.fillStyle = '#E8EEFF'; g.font = F(600, 40); g.fillText('21 NOVEMBER 2026  ·  IPG KAMPUS PERLIS', cv.width / 2, 255 + (1 - b) * 14); }
  g.globalAlpha = 1;
}
// November 2026 — Monday-first grid (I S R K J S A). 1 Nov 2026 = Ahad (Sunday) → column 7.
const DAYS = ['I', 'S', 'R', 'K', 'J', 'S', 'A'];
function calCells() { const out = []; let col = 6, row = 0; for (let d = 1; d <= 30; d++) { out.push({ d, col, row }); col++; if (col > 6) { col = 0; row++; } } return out; }
const CELLS = calCells();
function drawCal(cd, t) {
  faceBG(cd, '#2253DB', '#0B2780'); const { g, cv } = cd; const W0 = cv.width, padX = 70;
  const head = eOut(prog(t, 4.25, 4.55)), wk = eOut(prog(t, 4.4, 4.7));
  g.textBaseline = 'alphabetic';
  if (head > 0) { g.globalAlpha = head; g.fillStyle = '#fff'; g.textAlign = 'left'; g.font = F(700, 66); g.fillText('NOVEMBER 2026', padX, 120 + (1 - head) * 16);
    g.fillStyle = C.gold; g.beginPath(); g.arc(W0 - padX - 8, 98, 11, 0, 7); g.fill(); }
  const colW = (W0 - padX * 2) / 7, cx = i => padX + colW * (i + .5);
  if (wk > 0) { g.globalAlpha = wk; g.strokeStyle = 'rgba(255,255,255,.25)'; g.lineWidth = 2; g.beginPath(); g.moveTo(padX, 228); g.lineTo(W0 - padX, 228); g.stroke();
    g.textAlign = 'center'; for (let i = 0; i < 7; i++) { const sab = i === 5; const hl = sab ? eOut(prog(t, 5.15, 5.4)) : 0; g.font = F(sab && hl > 0 ? 800 : 600, 34); g.fillStyle = hl > 0 ? `rgba(255,214,107,${.55 + .45 * hl})` : 'rgba(200,214,255,.75)'; g.fillText(DAYS[i], cx(i), 205);
      if (sab && hl > 0) { g.fillStyle = C.gold; g.fillRect(cx(i) - 22 * hl, 216, 44 * hl, 5); } } }
  const rowY = r => 320 + r * 132;
  // Sabtu column glow
  const colHL = prog(t, 5.15, 5.45) * (1 - .5 * prog(t, 6.6, 7.2));
  if (colHL > 0) { g.globalAlpha = colHL * .9; const gr = g.createLinearGradient(0, 240, 0, rowY(5)); gr.addColorStop(0, 'rgba(255,214,107,.20)'); gr.addColorStop(1, 'rgba(255,214,107,.02)'); g.fillStyle = gr; rrect(g, cx(5) - colW * .46, 240, colW * .92, rowY(4) - 190, 34); g.fill(); }
  for (const c of CELLS) {
    const k = eOut(prog(t, 4.5 + c.row * .07 + c.col * .015, 4.85 + c.row * .07 + c.col * .015)); if (k <= 0) continue;
    const x = cx(c.col), y = rowY(c.row);
    if (c.d === 21) {
      const pop = prog(t, 5.45, 5.75), s = pop > 0 ? eBack(pop, 2.4) : 0;
      if (s > 0) { // glow + badge
        const pulse = prog(t, 5.6, 6.4); if (pulse > 0 && pulse < 1) { g.globalAlpha = (1 - pulse) * .8; g.strokeStyle = C.goldL; g.lineWidth = 6; g.beginPath(); g.arc(x, y - 16, 56 + pulse * 70, 0, 7); g.stroke(); }
        g.globalAlpha = 1; g.save(); g.shadowColor = 'rgba(255,200,70,.95)'; g.shadowBlur = 50 + 14 * Math.sin(t * 5); const gr = g.createRadialGradient(x - 14, y - 34, 6, x, y - 16, 60); gr.addColorStop(0, '#FFF0B8'); gr.addColorStop(.5, '#FFC93E'); gr.addColorStop(1, '#D9930F'); g.fillStyle = gr; g.beginPath(); g.arc(x, y - 16, 56 * s, 0, 7); g.fill(); g.restore();
        g.globalAlpha = clamp(s); g.fillStyle = C.ink; g.textAlign = 'center'; g.font = F(800, 54); g.fillText('21', x, y + 2); continue; }
    }
    g.globalAlpha = k * (c.d === 21 ? 1 : 1 - .45 * prog(t, 5.5, 5.9)); g.fillStyle = '#fff'; g.textAlign = 'center'; g.font = F(400, 52); g.fillText(String(c.d), x, y + (1 - k) * 18);
  }
  // pill: SABTU · 21 NOVEMBER 2026 (row 6, beside "30")
  const pl = eOut(prog(t, 5.95, 6.3));
  if (pl > 0) { g.globalAlpha = pl; const px = cx(1) - colW * .35, pw = (W0 - padX) - px, py = rowY(5) - 62; g.fillStyle = 'rgba(242,182,48,.16)'; rrect(g, px, py + (1 - pl) * 14, pw, 82, 41); g.fill(); g.strokeStyle = C.gold; g.lineWidth = 3; g.stroke();
    g.fillStyle = C.goldL; g.textAlign = 'center'; const s = fitText(g, 'SABTU · 21 NOVEMBER 2026', 800, 36, pw - 40); g.font = F(800, s); g.fillText('SABTU · 21 NOVEMBER 2026', px + pw / 2, py + 54 + (1 - pl) * 14); }
  g.globalAlpha = 1; shine(cd, prog(t, 6.5, 7.0));
}
function icoCal(g, x, y, s) { g.strokeStyle = C.gold; g.lineWidth = s * .09; rrect(g, x, y + s * .12, s, s * .86, s * .16); g.stroke(); g.fillStyle = C.gold; g.fillRect(x, y + s * .12, s, s * .24); g.fillRect(x + s * .22, y, s * .1, s * .26); g.fillRect(x + s * .68, y, s * .1, s * .26); }
function icoPin(g, x, y, s) { g.fillStyle = C.gold; g.beginPath(); g.arc(x + s / 2, y + s * .38, s * .36, Math.PI * .85, Math.PI * 2.15); g.lineTo(x + s / 2, y + s); g.closePath(); g.fill(); g.fillStyle = '#fff'; g.beginPath(); g.arc(x + s / 2, y + s * .38, s * .14, 0, 7); g.fill(); }
function drawInfo(cd, t) {
  faceBG(cd, '#F2F4FA', '#DCE2EF'); const { g, cv } = cd; const padX = 80, W0 = cv.width;
  // faint ball line-art
  g.save(); g.globalAlpha = .06 * prog(t, 7.9, 8.4); g.translate(W0 - 170, 210); g.rotate(-.5); g.strokeStyle = C.ink; g.lineWidth = 8; g.beginPath(); g.ellipse(0, 0, 170, 105, 0, 0, 7); g.stroke(); g.beginPath(); g.moveTo(-60, 0); g.lineTo(60, 0); g.stroke(); for (let i = -2; i <= 2; i++) { g.beginPath(); g.moveTo(i * 22, -14); g.lineTo(i * 22, 14); g.stroke(); } g.restore();
  g.textAlign = 'left'; g.textBaseline = 'alphabetic';
  const a = eOut5(prog(t, 7.85, 8.25)); if (a > 0) { g.globalAlpha = a; g.font = F(900, 250); const gr = g.createLinearGradient(0, 120, 0, 360); gr.addColorStop(0, '#173A9E'); gr.addColorStop(1, '#0A1A44'); g.fillStyle = gr; g.fillText('HTK', padX - 8, 340 + (1 - a) * 40); }
  const r = eOut(prog(t, 8.1, 8.45)); if (r > 0) { g.globalAlpha = 1; g.fillStyle = C.gold; g.fillRect(padX, 392, 150 * r, 12); }
  const b = eOut(prog(t, 8.2, 8.55)); if (b > 0) { g.globalAlpha = b; g.fillStyle = C.ink; g.font = F(800, 80); g.fillText('PIALA', padX, 520 + (1 - b) * 24); g.fillText('PENGARAH', padX, 612 + (1 - b) * 24); g.fillStyle = '#1846C8'; g.fillText('RAGBI', padX, 704 + (1 - b) * 24); }
  const l = eOut(prog(t, 8.4, 8.6)); if (l > 0) { g.globalAlpha = l; g.fillStyle = 'rgba(11,29,82,.14)'; g.fillRect(padX, 775, (W0 - padX * 2) * l, 3); }
  const d = eOut(prog(t, 8.45, 8.8)); if (d > 0) { g.globalAlpha = d; icoCal(g, padX, 832 + (1 - d) * 16, 58); g.fillStyle = C.ink; const s = fitText(g, '21 NOVEMBER 2026', 700, 54, W0 - padX * 2 - 90); g.font = F(700, s); g.fillText('21 NOVEMBER 2026', padX + 90, 882 + (1 - d) * 16); }
  const p = eOut(prog(t, 8.65, 9.0)); if (p > 0) { g.globalAlpha = p; icoPin(g, padX + 2, 950 + (1 - p) * 16, 58); g.fillStyle = C.ink; const s = fitText(g, 'IPG KAMPUS PERLIS', 700, 54, W0 - padX * 2 - 90); g.font = F(700, s); g.fillText('IPG KAMPUS PERLIS', padX + 90, 1000 + (1 - p) * 16); }
  g.globalAlpha = 1; shine(cd, prog(t, 9.45, 9.95));
}
// stylised map (layout loosely follows the campus road loop; not a survey map)
const ROADS = [
  { w: 16, pts: [[1180, -20], [1240, 120], [1300, 300], [1330, 520], [1320, 700], [1300, 900]] },
  { w: 14, pts: [[-20, 640], [300, 600], [700, 610], [1100, 640], [1330, 650], [2020, 660]] },
  { w: 12, pts: [[520, 520], [470, 360], [520, 190], [700, 120], [900, 130], [1080, 170], [1240, 120]] },
  { w: 12, pts: [[520, 520], [700, 560], [900, 540], [1100, 520], [1280, 470]] },
  { w: 8, pts: [[700, 120], [720, 320], [700, 560]] }, { w: 8, pts: [[470, 360], [720, 330], [960, 340], [1300, 330]] },
  { w: 8, pts: [[1330, 520], [1600, 480], [1850, 520], [2020, 500]] }, { w: 8, pts: [[1600, 480], [1620, 250], [1650, -20]] },
  { w: 8, pts: [[300, 600], [260, 800], [240, 900]] }, { w: 8, pts: [[1100, 640], [1080, 900]] }, { w: 6, pts: [[960, 340], [980, 520]] },
];
const ROUTE = [[2020, 660], [1330, 650], [1300, 470], [1280, 470], [1100, 520], [960, 525], [960, 340], [900, 300]];
const PIN = [900, 300];
function polyLen(p) { let L = 0; for (let i = 1; i < p.length; i++) L += Math.hypot(p[i][0] - p[i - 1][0], p[i][1] - p[i - 1][1]); return L; }
function drawPoly(g, p, frac) { const L = polyLen(p) * frac; let acc = 0; g.beginPath(); g.moveTo(p[0][0], p[0][1]); for (let i = 1; i < p.length; i++) { const s = Math.hypot(p[i][0] - p[i - 1][0], p[i][1] - p[i - 1][1]); if (acc + s >= L) { const k = (L - acc) / s; g.lineTo(lerp(p[i - 1][0], p[i][0], k), lerp(p[i - 1][1], p[i][1], k)); g.stroke(); return [lerp(p[i - 1][0], p[i][0], k), lerp(p[i - 1][1], p[i][1], k)]; } acc += s; g.lineTo(p[i][0], p[i][1]); } g.stroke(); return p[p.length - 1]; }
function drawMap(cd, t) {
  const { g, cv } = cd; faceBG(cd, '#0F2468', '#071338');
  g.save(); rrect(g, 0, 0, cv.width, cv.height, 60); g.clip();
  const gk = prog(t, 14.25, 14.7);
  g.globalAlpha = .5 * gk; g.strokeStyle = 'rgba(120,150,230,.12)'; g.lineWidth = 1; for (let x = 0; x < cv.width; x += 80) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, cv.height); g.stroke(); } for (let y = 0; y < cv.height; y += 80) { g.beginPath(); g.moveTo(0, y); g.lineTo(cv.width, y); g.stroke(); }
  // river
  g.globalAlpha = gk; g.strokeStyle = 'rgba(60,120,255,.55)'; g.lineWidth = 10; g.lineCap = 'round'; g.lineJoin = 'round'; drawPoly(g, [[-20, 760], [200, 720], [420, 790], [640, 860], [900, 830], [1200, 900]], 1);
  // campus block
  g.fillStyle = 'rgba(80,120,230,.10)'; g.beginPath(); g.moveTo(540, 500); g.lineTo(495, 360); g.lineTo(540, 210); g.lineTo(705, 145); g.lineTo(1060, 190); g.lineTo(1260, 140); g.lineTo(1300, 300); g.lineTo(1270, 455); g.lineTo(1100, 500); g.lineTo(700, 540); g.closePath(); g.fill();
  ROADS.forEach((r, i) => { const k = eOut(prog(t, 14.3 + i * .03, 14.75 + i * .03)); if (k <= 0) return; g.strokeStyle = 'rgba(170,195,255,.55)'; g.lineWidth = r.w * .8; drawPoly(g, r.pts, k); });
  // route
  const rk = eInOut(prog(t, 14.8, 15.75));
  if (rk > 0) { g.globalAlpha = 1; g.save(); g.shadowColor = 'rgba(255,200,70,.9)'; g.shadowBlur = 26; g.strokeStyle = C.gold; g.lineWidth = 14; const end = drawPoly(g, ROUTE, rk); g.restore(); g.fillStyle = '#fff'; g.beginPath(); g.arc(ROUTE[0][0] - 6, ROUTE[0][1], 0, 0, 7); g.fill(); g.fillStyle = C.goldL; g.beginPath(); g.arc(end[0], end[1], 12, 0, 7); g.fill(); }
  // pin
  const pd = prog(t, 15.7, 16.05);
  if (pd > 0) { const y = PIN[1] - 150 * (1 - eBack(pd, 1.6)) - 8; const rp = prog(t, 15.95, 16.7); if (rp > 0 && rp < 1) { g.globalAlpha = 1 - rp; g.strokeStyle = C.goldL; g.lineWidth = 5; g.beginPath(); g.ellipse(PIN[0], PIN[1], 30 + rp * 120, 12 + rp * 46, 0, 0, 7); g.stroke(); }
    g.globalAlpha = clamp(pd * 2); g.fillStyle = 'rgba(0,0,0,.35)'; g.beginPath(); g.ellipse(PIN[0], PIN[1], 24, 9, 0, 0, 7); g.fill();
    g.save(); g.shadowColor = 'rgba(255,190,60,.8)'; g.shadowBlur = 30; const s = 120; g.fillStyle = C.gold; g.beginPath(); g.arc(PIN[0], y - s * .62, s * .36, Math.PI * .82, Math.PI * 2.18); g.lineTo(PIN[0], y); g.closePath(); g.fill(); g.restore(); g.fillStyle = '#fff'; g.beginPath(); g.arc(PIN[0], y - s * .62, s * .15, 0, 7); g.fill(); }
  // label
  const lb = eOut(prog(t, 15.95, 16.3));
  if (lb > 0) { g.globalAlpha = lb; const lx = 1010, ly = 230; g.fillStyle = 'rgba(5,13,38,.78)'; rrect(g, lx, ly - 70 + (1 - lb) * 16, 640, 190, 28); g.fill(); g.strokeStyle = 'rgba(242,182,48,.7)'; g.lineWidth = 3; g.stroke();
    g.textAlign = 'left'; g.fillStyle = 'rgba(200,214,255,.8)'; g.font = F(600, 30); g.fillText('L O K A S I', lx + 40, ly - 12 + (1 - lb) * 16); g.fillStyle = '#fff'; g.font = F(800, 62); g.fillText('IPG KAMPUS PERLIS', lx + 40, ly + 70 + (1 - lb) * 16); }
  g.restore(); g.globalAlpha = 1;
}

// world-space helpers for cameras
function cardCenter(name, off = [0, 0]) { boardG.updateMatrixWorld(true); const c = cards[name]; return c.grp.localToWorld(v3(off[0], off[1], .13)); }
const boardNormal = () => v3(0, 0, 1).applyQuaternion(boardG.quaternion).normalize();
function framing(name, dist, mixFront = .55, off = [0, 0], lift = 0) { const c = cardCenter(name, off); const n = boardNormal().lerp(v3(0, 0, 1), 1 - mixFront).normalize(); return { p: c.clone().add(n.multiplyScalar(dist)).add(v3(0, lift, 0)), l: c }; }

// ======================================================================
//  CAMERA TRACKS
// ======================================================================
function arcMove(t, a, b, t0, t1, pull = 0, ease = eInOut) { const k = ease(prog(t, t0, t1)); const mid = a.p.clone().lerp(b.p, .5); const back = mid.clone().sub(a.l.clone().lerp(b.l, .5)).normalize().multiplyScalar(pull); mid.add(back); const p = a.p.clone().multiplyScalar((1 - k) ** 2).add(mid.multiplyScalar(2 * k * (1 - k))).add(b.p.clone().multiplyScalar(k * k)); return { p, l: a.l.clone().lerp(b.l, k) }; }
function drift(s, amt, k) { const d = s.l.clone().sub(s.p).multiplyScalar(amt * k); return { p: s.p.clone().add(d), l: s.l }; }

let FR = null;
function boardShots() { // computed lazily once board matrices are ready
  if (FR) return FR;
  FR = {
    over: { p: v3(0, -1.2, 36), l: v3(0, .2, 0) },
    overFar: { p: v3(0, -2.2, 44), l: v3(0, .4, 0) },
    cal: framing('cal', 15.5, .55, [0, -.1]),
    cal21: framing('cal', 14.0, .6, [.25, -.35]),
    info: framing('info', 15.2, .55, [0, 0]),
    map: framing('map', 13.5, .6, [3.0, -.2]),
    mapPin: framing('map', 13, .62, [.6, .2]),
  };
  return FR;
}
function camBoard(t) {
  const S = boardShots();
  if (t < 3.9) return drift(S.overFar, .04, prog(t, 3.2, 3.9));
  if (t < 4.85) return arcMove(t, drift(S.overFar, .04, 1), S.cal, 3.9, 4.85, 0, eInOut);
  if (t < 5.3) return drift(S.cal, .03, prog(t, 4.85, 5.3));
  if (t < 6.0) return arcMove(t, drift(S.cal, .03, 1), S.cal21, 5.3, 6.0, 0, eInOut);
  if (t < 7.35) return drift(S.cal21, .05, prog(t, 6.0, 7.35));
  if (t < 8.1) return arcMove(t, drift(S.cal21, .05, 1), S.info, 7.35, 8.1, 9, eInOut);
  if (t < 10.9) return drift(S.info, .07, prog(t, 8.1, 10.9));
  // map segment 14.2 → 17.1
  if (t < 14.25) return S.map;
  if (t < 16.2) return arcMove(t, S.map, S.mapPin, 14.5, 15.9, 0, eInOut);
  return arcMove(t, S.mapPin, S.over, 16.2, 17.15, 0, eOut5);
}
function camStadium(t) {
  if (t < 3.4) { // hook
    const k = eOut(prog(t, 0, 3.0));
    const p = v3(0, lerp(1.25, 1.5, k), lerp(33.5, 30.6, k));
    const lookField = v3(0, lerp(16, 3.2, eInOut(prog(t, .2, 1.9))), -30);
    const bp = ballPos(t); const follow = eInOut(prog(t, 1.3, 2.35));
    return { p, l: lookField.lerp(bp, follow), fov: 35 };
  }
  if (t < 14.4) { // trophy orbit
    const k = prog(t, 10.6, 14.3); const a = lerp(-.95, .25, eInOut(k)), r = lerp(9.5, 7.6, eOut(k));
    return { p: v3(Math.sin(a) * r, lerp(.8, 2.1, eInOut(k)), Math.cos(a) * r), l: v3(.2, lerp(1.55, 1.35, k), 0), fov: 30 };
  }
  // finale
  const k = prog(t, 17.0, 20.0);
  return { p: v3(lerp(-6, 4, k), lerp(26, 22, eOut(k)), lerp(62, 54, eOut(k))), l: v3(0, lerp(2, 4, k), -10), fov: 38 };
}
// ball flight (hook)
function ballPos(t) {
  const A = v3(-9, 14, -32), M = v3(-2, 5.5, 4), B = v3(.05, 1.47, 28.95), E = v3(.05, 1.5, 30.45);
  if (t < 1.25) return A.clone();
  if (t < 2.45) { const k = eExpo(prog(t, 1.25, 2.45)); return A.clone().multiplyScalar((1 - k) ** 2).add(M.clone().multiplyScalar(2 * k * (1 - k))).add(B.clone().multiplyScalar(k * k)); }
  if (t < 2.8) return B.clone().add(v3(0, .015 * Math.sin((t - 2.45) * 6), 0));
  return B.clone().lerp(E, eIn(prog(t, 2.8, 3.2)));
}

// ======================================================================
//  POST
// ======================================================================
const composer = new EffectComposer(renderer);
const rp = new RenderPass(stadium, camera); composer.addPass(rp);
const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), .85, .55, .82); composer.addPass(bloom);
composer.addPass(new OutputPass());

// ======================================================================
//  DOM overlays
// ======================================================================
const $ = id => document.getElementById(id);
function setTxt(el, a, ty = 0, sc = 1, blur = 0) { el.style.opacity = a; el.style.transform = `translateY(${ty}px) scale(${sc})`; el.style.filter = blur > .1 ? `blur(${blur}px)` : 'none'; }
function overlays(t) {
  const u = W / 1080;
  // hook caption
  const hc = prog(t, 1.75, 2.15) * (1 - prog(t, 2.85, 3.05)); setTxt($('hookCap'), eOut(hc), (1 - eOut(prog(t, 1.75, 2.15))) * 30 * u, 1, (1 - hc) * 6 * u);
  // trophy caption
  const tc = eOut(prog(t, 11.6, 12.05)) * (1 - prog(t, 13.95, 14.2)); setTxt($('trophyCap'), tc, (1 - eOut(prog(t, 11.6, 12.05))) * 30 * u, 1, (1 - tc) * 6 * u);
  // finale slams
  [['f1', 17.45], ['f2', 17.85], ['f3', 18.3]].forEach(([id, t0]) => { const k = prog(t, t0, t0 + .32); const e = eOut5(k); setTxt($(id), clamp(k * 2.2), 0, lerp(1.35, 1, e), (1 - e) * 14 * u); });
  $('finShade').style.opacity = eInOut(prog(t, 17.0, 17.6));
  $('finRule').style.transform = `scaleX(${eOut(prog(t, 18.75, 19.15))})`;
  const ff = eOut(prog(t, 18.9, 19.3)); setTxt($('finFoot'), ff, (1 - ff) * 24 * u);
  // dips & flashes (scene changes)
  const tri = (a, m, b) => t < a || t > b ? 0 : t < m ? eInOut(prog(t, a, m)) : 1 - eInOut(prog(t, m, b));
  $('dip').style.opacity = Math.max(tri(2.95, 3.22, 3.5), tri(10.45, 10.62, 10.85), tri(14.0, 14.2, 14.45), tri(16.85, 17.05, 17.3), t < .05 ? 1 : 0, prog(t, 19.75, 20) * .0);
  $('flash').style.opacity = Math.max(tri(.2, .22, .45) * .16, tri(.45, .47, .7) * .13, tri(.72, .74, .95) * .12, tri(.9, .92, 1.15) * .1, tri(5.45, 5.5, 5.85) * .18, tri(17.45, 17.5, 17.8) * .25, tri(17.85, 17.9, 18.2) * .25, tri(18.3, 18.35, 18.7) * .3);
  // whip blur on scene changes
  const wb = Math.max(tri(2.85, 3.2, 3.55), tri(10.3, 10.62, 10.95), tri(13.9, 14.2, 14.55), tri(16.75, 17.05, 17.35));
  renderer.domElement.style.filter = wb > .02 ? `blur(${wb * 10 * u}px)` : 'none';
}

// ======================================================================
//  MAIN RENDER
// ======================================================================
const inBoard = t => (t >= 3.2 && t < 10.62) || (t >= 14.2 && t < 17.05);
function renderAt(t) {
  t = clamp(t, 0, DURATION);
  overlays(t);
  if (inBoard(t)) {
    // card build-in (stagger) at scene start
    const order = ['header', 'cal', 'info', 'map'];
    order.forEach((n, i) => { const c = cards[n]; const k = t < 10.7 ? eOut(prog(t, 3.28 + i * .13, 3.62 + i * .13)) : 1; const s = lerp(.86, 1, k); c.grp.scale.setScalar(s); c.grp.position.z = (1 - k) * 1.2; c.slabMat.opacity = k; c.faceMat.opacity = k; c.draw(c, t); c.tex.needsUpdate = true; });
    bokeh.rotation.z = t * .01; bokeh.position.y = Math.sin(t * .3) * .3;
    const s = camBoard(t); camera.fov = 35; camera.position.copy(s.p); camera.up.set(0, 1, 0); camera.lookAt(s.l); camera.updateProjectionMatrix();
    rp.scene = board; bloom.strength = .32; bloom.threshold = .98; renderer.toneMappingExposure = 1.05;
  } else {
    // floodlights
    const finaleDim = t > 17 ? .75 : 1;
    towers.forEach(tw => { const on = t < 3.4 ? eOut(prog(t, tw.ign, tw.ign + .18)) : 1; const flick = t < 3.4 && t < tw.ign + .25 && t > tw.ign ? (.75 + .25 * Math.sin(t * 90)) : 1; const v = on * flick * finaleDim;
      tw.lampMat.color.setRGB(4 * v, 3.8 * v, 3.3 * v); tw.flare.scale.setScalar(12 + 5 * v); tw.flare.material.opacity = .85 * v; tw.spot.intensity = (tw.ign > .6 ? 520 : 900) * v; tw.cone.material.uniforms.opacity.value = .5 * v; });
    dust.material.opacity = .55 * prog(t, .5, 1.5); dust.rotation.y = t * .01;
    // ball
    const hook = t < 3.4; ball.visible = hook && t > 1.2;
    if (ball.visible) { const p = ballPos(t), p2 = ballPos(t + .01); ball.position.copy(p); const dir = p2.clone().sub(p); const axis = dir.lengthSq() > 1e-8 && t < 2.4 ? dir.normalize() : v3(.94, .2, -.28).normalize();
      const spinRate = t < 2.45 ? 28 : 2.2; const spin = t < 2.45 ? (t - 1.2) * spinRate : 1.25 * 28 + (t - 2.45) * spinRate;
      ball.quaternion.setFromUnitVectors(v3(0, 1, 0), axis); ball.rotateY(spin);
      const hk = prog(t, 2.0, 2.4); heroKey.intensity = 3.2 * hk; heroKey.position.set(-1.2, 2.6, 30.4); heroKey.target.position.copy(p); heroRim.intensity = 7 * hk; heroRim.position.set(1.4, 2.2, 27.4); heroRim.target.position.copy(p); }
    else { heroKey.intensity = 0; heroRim.intensity = 0; }
    // trophy
    const tr = t > 10.5 && t < 14.4; trophy.visible = teeBall.visible = tee.visible = tr; trophySpot.intensity = tr ? 32 * eOut(prog(t, 10.6, 11.0)) : 0; trophyRim.intensity = tr ? 18 : 0;
    sparkles.visible = tr; if (tr) { trophy.rotation.y = (t - 10.6) * .25; const pos = sparkles.geometry.attributes.position, b = sparkles.userData.base; for (let i = 0; i < pos.count; i++) pos.setY(i, b[i * 3 + 1] + ((t * .25 + i * .013) % 1) * .6); pos.needsUpdate = true; sparkles.material.opacity = .9 * prog(t, 10.9, 11.5); }
    const s = camStadium(t); camera.fov = s.fov; camera.position.copy(s.p); camera.up.set(0, 1, 0); camera.lookAt(s.l); camera.updateProjectionMatrix();
    rp.scene = stadium; const trs = t > 10.5 && t < 14.4; bloom.strength = t < 3.4 ? .6 : trs ? .35 : .5; bloom.radius = .35; bloom.threshold = trs ? .96 : .88; renderer.toneMappingExposure = t > 17 ? .6 : .9;
  }
  composer.render();
}
window.renderAt = renderAt;
window.DURATION = DURATION;
window.ready = (async () => { await Promise.all([700, 800, 900, 600, 400].map(w => document.fonts.load(F(w, 40)))); await document.fonts.ready; renderAt(0); return true; })();
