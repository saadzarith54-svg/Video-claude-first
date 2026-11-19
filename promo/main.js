// PERAH LAB — Orange Blast promo @ Hari Terbuka Asrama & Piala Pengarah Ragbi (deterministic renderAt(t))
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

// ---------- helpers ----------
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

// brand palette (from PERAH LAB poster/logo)
const C = { red: '#F23A3C', redD: '#C8202B', orange: '#FF8A00', orangeL: '#FFB23D', lime: '#E4F542', sky: '#1E9AD6', skyL: '#5CC6F2', skyD: '#0A6AAE', ink: '#0B3A6E', white: '#FFFFFF' };

const stage = document.getElementById('stage');
stage.style.width = W + 'px'; stage.style.height = H + 'px'; stage.style.setProperty('--u', (W / 1080) + 'px');
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H);
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
stage.prepend(renderer.domElement);
const camera = new THREE.PerspectiveCamera(35, W / H, 0.05, 600);
const pmrem = new THREE.PMREMGenerator(renderer);
const roomEnv = pmrem.fromScene(new RoomEnvironment(renderer), 0.04).texture;

const F = (w, s) => `${w} ${s}px IDX`, FL = s => `${s}px LIL`, FB = s => `${s}px BOW`;
function rrect(g, x, y, w, h, r) { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); }
function fit(g, text, fontFn, size, maxW) { let s = size; g.font = fontFn(s); while (g.measureText(text).width > maxW && s > 8) { s -= 2; g.font = fontFn(s); } return s; }
function makeCanvas(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
function texFrom(c) { const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; }
const IMG = {}; const imgLoad = n => new Promise(r => { const i = new Image(); i.onload = () => { IMG[n] = i; r(); }; i.src = `assets/${n}.png`; });
const imgLoadJ = (n, f) => new Promise(r => { const i = new Image(); i.onload = () => { IMG[n] = i; r(); }; i.src = f; });
const texLoader = new THREE.TextureLoader();
const loadTex = f => new Promise(r => texLoader.load(f, t => { t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; r(t); }));

// ---------- shared textures ----------
const flareTex = (() => { const c = makeCanvas(256, 256), g = c.getContext('2d'); const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(.12, 'rgba(255,245,220,.8)'); gr.addColorStop(.4, 'rgba(255,220,160,.18)'); gr.addColorStop(1, 'rgba(255,200,120,0)'); g.fillStyle = gr; g.fillRect(0, 0, 256, 256); return new THREE.CanvasTexture(c); })();
function peelTextures() {
  const c = makeCanvas(1024, 512), g = c.getContext('2d'); const gr = g.createLinearGradient(0, 0, 0, 512); gr.addColorStop(0, '#FF9A1A'); gr.addColorStop(.5, '#FF8400'); gr.addColorStop(1, '#F06A00'); g.fillStyle = gr; g.fillRect(0, 0, 1024, 512);
  seed = 9; for (let i = 0; i < 9000; i++) { g.fillStyle = `rgba(${rnd() < .5 ? '255,190,90' : '200,80,0'},${.15 + rnd() * .2})`; g.beginPath(); g.arc(rnd() * 1024, rnd() * 512, 1 + rnd() * 2, 0, 7); g.fill(); }
  const b = makeCanvas(1024, 512), h = b.getContext('2d'); h.fillStyle = '#909090'; h.fillRect(0, 0, 1024, 512); seed = 13; for (let i = 0; i < 14000; i++) { h.fillStyle = 'rgba(40,40,40,.5)'; h.beginPath(); h.arc(rnd() * 1024, rnd() * 512, 1.2 + rnd() * 1.6, 0, 7); h.fill(); }
  return [texFrom(c), new THREE.CanvasTexture(b)];
}
const [peelMap, peelBump] = peelTextures();
function sliceTexture() {
  const c = makeCanvas(512, 512), g = c.getContext('2d'), R = 256;
  g.fillStyle = '#FF8A00'; g.beginPath(); g.arc(R, R, 254, 0, 7); g.fill(); g.fillStyle = '#FFF4DC'; g.beginPath(); g.arc(R, R, 236, 0, 7); g.fill();
  for (let i = 0; i < 10; i++) { const a0 = i / 10 * Math.PI * 2 + .03, a1 = (i + 1) / 10 * Math.PI * 2 - .03; const gr = g.createRadialGradient(R, R, 20, R, R, 220); gr.addColorStop(0, '#FFC24A'); gr.addColorStop(1, '#FF8E0A'); g.fillStyle = gr; g.beginPath(); g.moveTo(R + Math.cos((a0 + a1) / 2) * 22, R + Math.sin((a0 + a1) / 2) * 22); g.arc(R, R, 214, a0, a1); g.closePath(); g.fill();
    seed = 40 + i; for (let k = 0; k < 40; k++) { const a = lerp(a0, a1, rnd()), r = 40 + rnd() * 160; g.fillStyle = 'rgba(255,240,190,.35)'; g.beginPath(); g.ellipse(R + Math.cos(a) * r, R + Math.sin(a) * r, 3, 9, a, 0, 7); g.fill(); } }
  g.fillStyle = '#FFF4DC'; g.beginPath(); g.arc(R, R, 18, 0, 7); g.fill();
  return texFrom(c);
}
const sliceMap = sliceTexture();
const peelMat = new THREE.MeshPhysicalMaterial({ map: peelMap, bumpMap: peelBump, bumpScale: 1.2, roughness: .48, clearcoat: .5, clearcoatRoughness: .35 });
const sliceMat = new THREE.MeshPhysicalMaterial({ map: sliceMap, roughness: .25, clearcoat: 1, clearcoatRoughness: .1, side: THREE.DoubleSide });
const leafMat = new THREE.MeshStandardMaterial({ color: '#3E9B2E', roughness: .5, side: THREE.DoubleSide });
function wholeOrange(r = 1) {
  const g = new THREE.Group(); const s = new THREE.Mesh(new THREE.SphereGeometry(r, 64, 48), peelMat); s.scale.y = .94; s.castShadow = true; g.add(s);
  const stem = new THREE.Mesh(new THREE.CylinderGeometry(r * .05, r * .07, r * .12, 12), new THREE.MeshStandardMaterial({ color: '#4d6b1f' })); stem.position.y = r * .95; g.add(stem);
  const leafShape = new THREE.Shape(); leafShape.moveTo(0, 0); leafShape.quadraticCurveTo(r * .35, r * .25, r * .8, 0); leafShape.quadraticCurveTo(r * .35, -r * .25, 0, 0);
  const leaf = new THREE.Mesh(new THREE.ShapeGeometry(leafShape, 16), leafMat); leaf.position.set(r * .04, r * .98, 0); leaf.rotation.set(-.4, 0, .5); g.add(leaf);
  return g;
}
function halfOrange(r = 1) {
  const g = new THREE.Group(); const dome = new THREE.Mesh(new THREE.SphereGeometry(r, 64, 32, 0, Math.PI * 2, 0, Math.PI / 2), peelMat); dome.castShadow = true; g.add(dome);
  const face = new THREE.Mesh(new THREE.CircleGeometry(r * .995, 64), sliceMat); face.rotation.x = Math.PI / 2; g.add(face); return g;
}
function wedge(r = 1) { // thick slice
  const g = new THREE.Group(); const rim = new THREE.Mesh(new THREE.CylinderGeometry(r, r, r * .22, 64, 1, true), peelMat); g.add(rim);
  for (const s of [1, -1]) { const f = new THREE.Mesh(new THREE.CircleGeometry(r * .998, 64), sliceMat); f.rotation.x = s * Math.PI / 2; f.position.y = s * r * .11; g.add(f); } return g;
}
const dropMat = new THREE.MeshPhysicalMaterial({ color: '#FFA51F', roughness: .05, clearcoat: 1, transmission: .25, thickness: .2, ior: 1.33 });
function droplets(n, sd) { seed = sd; const grp = new THREE.Group(); const geo = new THREE.SphereGeometry(1, 16, 12); for (let i = 0; i < n; i++) { const m = new THREE.Mesh(geo, dropMat); const d = v3(rnd() - .5, rnd() * .8 + .1, rnd() - .5).normalize(); m.userData = { dir: d, sp: .6 + rnd() * 1.4, s: .02 + rnd() * .05 }; grp.add(m); } return grp; }

// ======================================================================
//  1) STADIUM (hook)
// ======================================================================
const stadium = new THREE.Scene();
stadium.background = new THREE.Color('#02050f'); stadium.fog = new THREE.FogExp2('#030a22', 0.0075);
(function () { const es = new THREE.Scene(); es.background = new THREE.Color('#03060f'); const em = new THREE.MeshBasicMaterial({ color: new THREE.Color(6, 5.6, 4.8) });
  for (const [x, y, z] of [[-30, 25, -30], [30, 25, -30], [-30, 25, 30], [30, 25, 30]]) { const b = new THREE.Mesh(new THREE.BoxGeometry(14, 5, 1), em); b.position.set(x, y, z); b.lookAt(0, 0, 0); es.add(b); }
  stadium.environment = pmrem.fromScene(es, 0.02).texture; })();
function fieldTexture() { const c = makeCanvas(1400, 2000), g = c.getContext('2d'); const k = 20;
  for (let i = 0; i < 20; i++) { g.fillStyle = i % 2 ? '#164a1f' : '#1c5826'; g.fillRect(0, i * 100, 1400, 100); }
  seed = 3; for (let i = 0; i < 60000; i++) { g.fillStyle = `rgba(${rnd() < .5 ? '0,0,0' : '120,170,90'},${.05 + rnd() * .06})`; g.fillRect(rnd() * 1400, rnd() * 2000, 2, 3); }
  g.strokeStyle = 'rgba(250,250,245,.95)'; g.lineWidth = 5; const X = m => 700 + m * k, Z = m => 1000 + m * k; g.strokeRect(X(-34), Z(-48), 68 * k, 96 * k);
  const line = (z, dash) => { g.setLineDash(dash || []); g.beginPath(); g.moveTo(X(-34), Z(z)); g.lineTo(X(34), Z(z)); g.stroke(); };
  line(0); line(-38); line(38); line(-10, [24, 18]); line(10, [24, 18]); g.setLineDash([]); return texFrom(c); }
const field = new THREE.Mesh(new THREE.PlaneGeometry(70, 100), new THREE.MeshStandardMaterial({ map: fieldTexture(), roughness: .95 })); field.rotation.x = -Math.PI / 2; field.receiveShadow = true; stadium.add(field);
const apron = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshStandardMaterial({ color: '#0b1a12', roughness: 1 })); apron.rotation.x = -Math.PI / 2; apron.position.y = -.02; stadium.add(apron);
const postMat = new THREE.MeshStandardMaterial({ color: '#f4f4f0', roughness: .45 });
for (const z of [-48, 48]) { const grp = new THREE.Group(); for (const x of [-2.8, 2.8]) { const p = new THREE.Mesh(new THREE.CylinderGeometry(.09, .09, 14, 12), postMat); p.position.set(x, 7, 0); grp.add(p); } const bar = new THREE.Mesh(new THREE.CylinderGeometry(.08, .08, 5.6, 12), postMat); bar.rotation.z = Math.PI / 2; bar.position.y = 3; grp.add(bar); grp.position.z = z; stadium.add(grp); }
const standMat = new THREE.MeshStandardMaterial({ color: '#060a16', roughness: 1 });
function stand(w, d, x, z, ry) { const g = new THREE.Group(); for (let i = 0; i < 9; i++) { const b = new THREE.Mesh(new THREE.BoxGeometry(w, 1.1 * (i + 1), d / 9), standMat); b.position.set(0, .55 * (i + 1), i * d / 9); g.add(b); } g.position.set(x, 0, z); g.rotation.y = ry; stadium.add(g); }
stand(90, 16, 0, -60, 0); stand(120, 16, -46, 0, Math.PI / 2); stand(120, 16, 46, 0, -Math.PI / 2);
const BEAM_VS = `varying vec3 vN; varying vec3 vV; varying vec2 vUv; void main(){ vUv = uv; vec4 mv = modelViewMatrix * vec4(position,1.); vV = -mv.xyz; vN = normalMatrix * normal; gl_Position = projectionMatrix * mv; }`;
const BEAM_FS = `uniform float opacity; uniform vec3 color; varying vec3 vN; varying vec3 vV; varying vec2 vUv; void main(){ float e = pow(abs(dot(normalize(vN), normalize(vV))), 2.5); gl_FragColor = vec4(color * e * pow(vUv.y, 1.8) * opacity, 1.); }`;
const towers = [];
function tower(x, z, ign) {
  const top = v3(x, 34, z), target = v3(x * .25, 0, z > -50 ? z * .35 : -20);
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(.35, .6, 34, 8), new THREE.MeshStandardMaterial({ color: '#141c2e', roughness: .7 })); pole.position.set(x, 17, z); stadium.add(pole);
  const head = new THREE.Group(); head.position.copy(top); head.lookAt(target); stadium.add(head);
  const lampMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(0, 0, 0) });
  const frame = new THREE.Mesh(new THREE.BoxGeometry(8.6, 4.2, .5), new THREE.MeshStandardMaterial({ color: '#1a2233' })); frame.position.z = -.3; head.add(frame);
  for (let i = 0; i < 4; i++) for (let j = 0; j < 3; j++) { const l = new THREE.Mesh(new THREE.PlaneGeometry(1.7, 1.05), lampMat); l.position.set(-3.15 + i * 2.1, -1.3 + j * 1.3, .01); head.add(l); }
  const flare = new THREE.Sprite(new THREE.SpriteMaterial({ map: flareTex, color: '#fff2d8', blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, opacity: 0, fog: false })); flare.position.copy(top); stadium.add(flare);
  const spot = new THREE.SpotLight('#fff1dc', 0, 160, .42, .55, 1.2); spot.position.copy(top); spot.target.position.copy(target); stadium.add(spot, spot.target);
  const len = top.distanceTo(target);
  const cone = new THREE.Mesh(new THREE.CylinderGeometry(.6, 7.5, len, 48, 1, true), new THREE.ShaderMaterial({ uniforms: { opacity: { value: 0 }, color: { value: new THREE.Color('#ffe6bd') } }, vertexShader: BEAM_VS, fragmentShader: BEAM_FS, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }));
  cone.position.copy(top).add(target).multiplyScalar(.5); cone.quaternion.setFromUnitVectors(v3(0, 1, 0), top.clone().sub(target).normalize()); stadium.add(cone);
  towers.push({ lampMat, flare, spot, cone, ign });
}
tower(-11, -62, 0.20); tower(11, -62, 0.45); tower(-40, 40, 0.72); tower(40, 40, 0.90);
stadium.add(new THREE.HemisphereLight('#2a3d78', '#04080f', 0.18));
const dust = (() => { seed = 11; const n = 900, p = new Float32Array(n * 3); for (let i = 0; i < n; i++) { p[i * 3] = (rnd() - .5) * 60; p[i * 3 + 1] = rnd() * 22; p[i * 3 + 2] = (rnd() - .5) * 90; }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(p, 3)); const pts = new THREE.Points(g, new THREE.PointsMaterial({ size: .12, map: flareTex, color: '#ffe4b0', transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false })); stadium.add(pts); return pts; })();
// rugby ball
function ballTexture() { const c = makeCanvas(1024, 512), g = c.getContext('2d'); g.fillStyle = '#f3f1ea'; g.fillRect(0, 0, 1024, 512);
  for (let p = 0; p < 4; p++) { const x0 = p * 256; g.fillStyle = p % 2 ? '#0E2E8E' : '#0A1A44'; g.beginPath(); g.moveTo(x0 + 40, 0); g.bezierCurveTo(x0 + 10, 180, x0 + 10, 330, x0 + 40, 512); g.lineTo(x0 + 120, 512); g.bezierCurveTo(x0 + 70, 330, x0 + 70, 180, x0 + 120, 0); g.closePath(); g.fill();
    g.fillStyle = '#E9A92A'; g.beginPath(); g.moveTo(x0 + 128, 0); g.bezierCurveTo(x0 + 100, 180, x0 + 100, 330, x0 + 128, 512); g.lineTo(x0 + 150, 512); g.bezierCurveTo(x0 + 122, 330, x0 + 122, 180, x0 + 150, 0); g.fill(); }
  g.strokeStyle = 'rgba(40,30,20,.75)'; g.lineWidth = 6; for (let p = 0; p < 4; p++) { g.beginPath(); g.moveTo(p * 256 + 2, 0); g.lineTo(p * 256 + 2, 512); g.stroke(); } return texFrom(c); }
function ballGeometry(L = .145, R = .097) { const pts = []; for (let i = 0; i <= 64; i++) { const y = -L + 2 * L * i / 64; pts.push(new THREE.Vector2(Math.max(R * Math.pow(Math.max(0, 1 - (y / L) ** 2), .72), .0005), y)); } return new THREE.LatheGeometry(pts, 96); }
const ball = new THREE.Mesh(ballGeometry(), new THREE.MeshPhysicalMaterial({ map: ballTexture(), roughness: .55, clearcoat: .35 })); stadium.add(ball);
const hookOrange = wholeOrange(.11); stadium.add(hookOrange);
const hookDrops = droplets(46, 77); stadium.add(hookDrops);
const heroKey = new THREE.SpotLight('#fff3e0', 0, 12, .5, .6, 1.5); stadium.add(heroKey, heroKey.target);
const heroRim = new THREE.SpotLight('#ffcf6a', 0, 12, .6, .6, 1.5); stadium.add(heroRim, heroRim.target);
const HERO = v3(.05, 1.47, 28.95);
function ballPos(t) { const A = v3(-9, 14, -32), M = v3(-2, 5.5, 4), E = v3(.05, 1.5, 30.45);
  if (t < 1.1) return A.clone(); if (t < 2.15) { const k = eExpo(prog(t, 1.1, 2.15)); return A.clone().multiplyScalar((1 - k) ** 2).add(M.clone().multiplyScalar(2 * k * (1 - k))).add(HERO.clone().multiplyScalar(k * k)); }
  if (t < 2.7) return HERO.clone().add(v3(0, .012 * Math.sin((t - 2.15) * 6), 0)); return HERO.clone().lerp(E, eIn(prog(t, 2.7, 3.0))); }

// ======================================================================
//  2) BRAND scene (reveal + end card): sky-blue, product cut-out, 3D oranges
// ======================================================================
const brand = new THREE.Scene(); brand.environment = roomEnv;
brand.background = (() => { const c = makeCanvas(540, 960), g = c.getContext('2d'); const gr = g.createRadialGradient(270, 330, 30, 270, 480, 760); gr.addColorStop(0, '#7FD6FA'); gr.addColorStop(.35, '#2EAAE6'); gr.addColorStop(1, '#0B6FB4'); g.fillStyle = gr; g.fillRect(0, 0, 540, 960);
  g.globalAlpha = .12; g.fillStyle = '#fff'; for (let i = 0; i < 14; i++) { g.save(); g.translate(270, 330); g.rotate(i / 14 * Math.PI * 2); g.beginPath(); g.moveTo(0, 0); g.lineTo(-40, -900); g.lineTo(40, -900); g.closePath(); g.fill(); g.restore(); } return texFrom(c); })();
brand.add(new THREE.HemisphereLight('#ffffff', '#4aa0d8', 1.1));
const sun = new THREE.DirectionalLight('#fff4e0', 2.6); sun.position.set(4, 6, 8); brand.add(sun);
let logoPlane, cupPlane;
const brandOranges = new THREE.Group(); brand.add(brandOranges);
const ORS = []; // floating fruit with parallax
function addFruit(obj, base, rotSp, sc) { obj.position.copy(base); obj.scale.setScalar(sc); obj.userData = { base: base.clone(), rotSp, sc, ph: rnd() * 6 }; brandOranges.add(obj); ORS.push(obj); }
seed = 101;
addFruit(halfOrange(1), v3(-1.75, 2.75, -1.5), v3(.4, .3, .2), .42);
addFruit(wedge(1), v3(1.72, 2.55, -.8), v3(.2, .5, .3), .38);
addFruit(wholeOrange(1), v3(1.95, -.35, -2.5), v3(.1, .35, 0), .45);
addFruit(wedge(1), v3(-1.95, -.9, -1.2), v3(.5, .2, .4), .34);
addFruit(halfOrange(1), v3(-1.6, -2.85, 1.2), v3(.3, .4, .1), .4);
addFruit(wedge(1), v3(1.6, -2.7, 1.6), v3(.2, .3, .5), .3);
const brandDrops = droplets(40, 55); brand.add(brandDrops);
const ice = (() => { const g = new THREE.Group(); const m = new THREE.MeshPhysicalMaterial({ color: '#ffffff', roughness: .05, transmission: .9, thickness: .5, ior: 1.31, clearcoat: 1 }); seed = 61; for (let i = 0; i < 6; i++) { const c = new THREE.Mesh(new RoundedBoxGeometry(.32, .32, .32, 4, .06), m); c.userData.base = v3((rnd() - .5) * 3.4, (rnd() - .5) * 5.6, -1 - rnd() * 2); c.userData.ph = rnd() * 6; g.add(c); } brand.add(g); return g; })();

// ======================================================================
//  3) BOARD scene (bento cards on brand blue)
// ======================================================================
const board = new THREE.Scene(); board.environment = roomEnv;
board.background = (() => { const c = makeCanvas(540, 960), g = c.getContext('2d'); const gr = g.createRadialGradient(270, 400, 20, 270, 470, 760); gr.addColorStop(0, '#6CCDF7'); gr.addColorStop(.45, '#1E9AD6'); gr.addColorStop(1, '#08558F'); g.fillStyle = gr; g.fillRect(0, 0, 540, 960); return texFrom(c); })();
board.add(new THREE.HemisphereLight('#ffffff', '#3a8fc8', .7));
const key = new THREE.DirectionalLight('#ffffff', 2.0); key.position.set(-8, 14, 16); key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
Object.assign(key.shadow.camera, { left: -14, right: 14, top: 14, bottom: -14, near: 1, far: 60 }); key.shadow.radius = 6; key.shadow.bias = -.0004; board.add(key);
const boardG = new THREE.Group(); boardG.rotation.set(-0.40, 0, 0.035); board.add(boardG);
const catcher = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.ShadowMaterial({ opacity: .28 })); catcher.position.z = -.35; catcher.receiveShadow = true; boardG.add(catcher);
const PX = 200; const cards = {};
function card(name, w, h, x, y, slabColor, draw) {
  const grp = new THREE.Group(); grp.position.set(x, y, 0);
  const slabMat = new THREE.MeshPhysicalMaterial({ color: slabColor, roughness: .38, clearcoat: 1, clearcoatRoughness: .18, transparent: true });
  const slab = new THREE.Mesh(new RoundedBoxGeometry(w, h, .26, 6, .3), slabMat); slab.castShadow = true; grp.add(slab);
  const cv = makeCanvas(Math.round(w * PX), Math.round(h * PX)); const tex = texFrom(cv);
  const faceMat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, toneMapped: false });
  const face = new THREE.Mesh(new THREE.PlaneGeometry(w - .02, h - .02), faceMat); face.position.z = .131; grp.add(face); boardG.add(grp);
  cards[name] = { grp, slabMat, faceMat, cv, g: cv.getContext('2d'), tex, w, h, draw };
}
card('header', 10, 1.7, 0, 5.2, '#D92A33', drawHeader);
card('cal', 4.85, 5.8, -2.575, 1.2, '#FF7A00', drawCal);
card('ev', 4.85, 5.8, 2.575, 1.2, '#F4F6FB', drawEvents);
card('map', 10, 4.4, 0, -4.15, '#0A5A98', drawMap);
function faceBG(cd, top, bot) { const { g, cv } = cd; g.clearRect(0, 0, cv.width, cv.height); const gr = g.createLinearGradient(0, 0, cv.width * .4, cv.height); gr.addColorStop(0, top); gr.addColorStop(1, bot); g.fillStyle = gr; rrect(g, 0, 0, cv.width, cv.height, 60); g.fill();
  const sh = g.createLinearGradient(0, 0, 0, cv.height * .5); sh.addColorStop(0, 'rgba(255,255,255,.14)'); sh.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = sh; rrect(g, 0, 0, cv.width, cv.height, 60); g.fill(); }
function shine(cd, k) { if (k <= 0 || k >= 1) return; const { g, cv } = cd; const x = lerp(-cv.width * .5, cv.width * 1.5, k); g.save(); rrect(g, 0, 0, cv.width, cv.height, 60); g.clip(); const gr = g.createLinearGradient(x - 160, 0, x + 160, cv.height * .3); gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(.5, 'rgba(255,255,255,.28)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, cv.width, cv.height); g.restore(); }

// timeline anchors (board)
const TB0 = 6.6, TB1 = 15.2;
function drawHeader(cd, t) { faceBG(cd, '#FF4A4C', '#C61E2A'); const { g, cv } = cd;
  const a = eOut(prog(t, 14.35, 14.75)), b = eOut(prog(t, 14.55, 14.9));
  if (a > 0 && IMG.perahlab_logo) { const im = IMG.perahlab_logo, h = 300 * lerp(.85, 1, eBack(a)), w = h * im.width / im.height; g.globalAlpha = a; g.drawImage(im, 70, (cv.height - h) / 2, w, h); }
  if (b > 0) { g.globalAlpha = b; g.textAlign = 'left'; g.textBaseline = 'middle'; g.fillStyle = '#fff'; const s = fit(g, 'JUMPA KAMI DI SINI!', FL, 112, cv.width - 700); g.font = FL(s); g.fillText('JUMPA KAMI DI SINI!', 640 + (1 - b) * 30, cv.height / 2 + 6); }
  g.globalAlpha = 1; }
const DAYS = ['I', 'S', 'R', 'K', 'J', 'S', 'A'];
const CELLS = (() => { const out = []; let col = 6, row = 0; for (let d = 1; d <= 30; d++) { out.push({ d, col, row }); col++; if (col > 6) { col = 0; row++; } } return out; })(); // 1 Nov 2026 = Ahad
function drawCal(cd, t) { faceBG(cd, '#FFA126', '#F05A00'); const { g, cv } = cd; const W0 = cv.width, padX = 70;
  const head = eOut(prog(t, 7.55, 7.85)), wk = eOut(prog(t, 7.7, 8.0)); g.textBaseline = 'alphabetic';
  if (head > 0) { g.globalAlpha = head; g.fillStyle = '#fff'; g.textAlign = 'left'; g.font = FL(78); g.fillText('NOVEMBER 2026', padX, 128 + (1 - head) * 16); g.fillStyle = C.lime; g.beginPath(); g.arc(W0 - padX - 8, 102, 13, 0, 7); g.fill(); }
  const colW = (W0 - padX * 2) / 7, cx = i => padX + colW * (i + .5), rowY = r => 320 + r * 132;
  if (wk > 0) { g.globalAlpha = wk; g.strokeStyle = 'rgba(255,255,255,.4)'; g.lineWidth = 2; g.beginPath(); g.moveTo(padX, 228); g.lineTo(W0 - padX, 228); g.stroke(); g.textAlign = 'center';
    for (let i = 0; i < 7; i++) { const sab = i === 5, hl = sab ? eOut(prog(t, 8.3, 8.55)) : 0; g.font = F(sab && hl > 0 ? 900 : 700, 36); g.fillStyle = hl > 0 ? `rgba(228,245,66,${.6 + .4 * hl})` : 'rgba(255,240,220,.85)'; g.fillText(DAYS[i], cx(i), 205); if (sab && hl > 0) { g.fillStyle = C.lime; g.fillRect(cx(i) - 22 * hl, 216, 44 * hl, 6); } } }
  const colHL = prog(t, 8.3, 8.6); if (colHL > 0) { g.globalAlpha = colHL * .9; g.fillStyle = 'rgba(255,255,255,.16)'; rrect(g, cx(5) - colW * .46, 240, colW * .92, rowY(4) - 190, 34); g.fill(); }
  for (const c of CELLS) { const k = eOut(prog(t, 7.85 + c.row * .06 + c.col * .012, 8.15 + c.row * .06 + c.col * .012)); if (k <= 0) continue; const x = cx(c.col), y = rowY(c.row);
    if (c.d === 21) { const pop = prog(t, 8.55, 8.85), s = pop > 0 ? eBack(pop, 2.4) : 0;
      if (s > 0) { const pulse = prog(t, 8.7, 9.5); if (pulse > 0 && pulse < 1) { g.globalAlpha = (1 - pulse) * .9; g.strokeStyle = C.lime; g.lineWidth = 7; g.beginPath(); g.arc(x, y - 16, 58 + pulse * 75, 0, 7); g.stroke(); }
        g.globalAlpha = 1; g.save(); g.shadowColor = 'rgba(228,245,66,.95)'; g.shadowBlur = 50 + 14 * Math.sin(t * 5); g.fillStyle = C.lime; g.beginPath(); g.arc(x, y - 16, 58 * s, 0, 7); g.fill(); g.restore();
        g.globalAlpha = clamp(s); g.fillStyle = C.redD; g.textAlign = 'center'; g.font = F(900, 56); g.fillText('21', x, y + 3); continue; } }
    g.globalAlpha = k * (c.d === 21 ? 1 : 1 - .4 * prog(t, 8.6, 9.0)); g.fillStyle = '#fff'; g.textAlign = 'center'; g.font = F(600, 52); g.fillText(String(c.d), x, y + (1 - k) * 18); }
  const pl = eOut(prog(t, 9.0, 9.35)); if (pl > 0) { g.globalAlpha = pl; const px = cx(1) - colW * .35, pw = (W0 - padX) - px, py = rowY(5) - 62; g.fillStyle = '#fff'; rrect(g, px, py + (1 - pl) * 14, pw, 84, 42); g.fill();
    g.fillStyle = C.red; g.textAlign = 'center'; const s = fit(g, 'SABTU · 21 NOVEMBER 2026', FL, 44, pw - 40); g.font = FL(s); g.fillText('SABTU · 21 NOVEMBER 2026', px + pw / 2, py + 58 + (1 - pl) * 14); }
  g.globalAlpha = 1; shine(cd, prog(t, 9.45, 9.9)); }
function drawEvents(cd, t) { faceBG(cd, '#FFFFFF', '#E8EEF6'); const { g, cv } = cd; const W0 = cv.width, pad = 70;
  const h = eOut(prog(t, 10.2, 10.5)); g.textBaseline = 'alphabetic'; g.textAlign = 'left';
  if (h > 0) { g.globalAlpha = h; g.fillStyle = C.red; g.font = FL(74); g.fillText('JUMPA KAMI DI', pad, 130 + (1 - h) * 16); g.fillStyle = C.orange; g.fillRect(pad, 160, 170 * h, 10); }
  const row = (img, y0, name, t0, tile) => { const k = prog(t, t0, t0 + .35); if (k <= 0) return; const s = eBack(k, 1.8); const box = 330;
    g.globalAlpha = clamp(k * 2); g.save(); g.translate(pad + box / 2, y0 + box / 2); g.scale(s, s);
    g.fillStyle = '#fff'; g.shadowColor = 'rgba(10,60,110,.25)'; g.shadowBlur = 30; g.shadowOffsetY = 10; rrect(g, -box / 2, -box / 2, box, box, 40); g.fill(); g.shadowColor = 'transparent';
    const im = IMG[img]; if (im) { if (tile) { g.save(); rrect(g, -box / 2 + 14, -box / 2 + 14, box - 28, box - 28, 30); g.clip(); const sc = Math.max((box - 28) / im.width, (box - 28) / im.height); g.drawImage(im, -im.width * sc / 2, -im.height * sc / 2, im.width * sc, im.height * sc); g.restore(); }
      else { const sc = Math.min((box - 40) / im.width, (box - 40) / im.height); g.drawImage(im, -im.width * sc / 2, -im.height * sc / 2, im.width * sc, im.height * sc); } }
    g.restore(); const n = eOut(prog(t, t0 + .2, t0 + .5)); if (n > 0) { g.globalAlpha = n; g.fillStyle = C.ink; const lines = name.split('\n'); const fs = 66; g.font = FL(fs); lines.forEach((l, i) => { const s = fit(g, l, FL, fs, W0 - pad * 2 - box - 30); g.font = FL(s); g.fillText(l, pad + box + 30 + (1 - n) * 24, y0 + box / 2 - (lines.length - 1) * fs * .55 + i * fs * 1.08 + 20); }); } };
  row('htk', 225, 'HARI\nTERBUKA\nASRAMA', 10.45, true);
  const l = eOut(prog(t, 10.7, 11.0)); if (l > 0) { g.globalAlpha = l; g.fillStyle = 'rgba(11,58,110,.14)'; g.fillRect(pad, 590, (W0 - pad * 2) * l, 3); }
  row('logo_ipg10s', 620, 'PIALA\nPENGARAH\nRAGBI', 10.9, false);
  const f = eOut(prog(t, 11.3, 11.6)); if (f > 0) { g.globalAlpha = f; g.fillStyle = C.orange; g.font = FL(46); g.textAlign = 'center'; g.fillText('21 NOVEMBER 2026', W0 / 2, 1060 + (1 - f) * 14); }
  g.globalAlpha = 1; shine(cd, prog(t, 11.55, 12.0)); }
// stylised map (layout loosely follows the campus road loop)
const ROADS = [
  { w: 16, pts: [[1180, -20], [1240, 120], [1300, 300], [1330, 520], [1320, 700], [1300, 900]] },
  { w: 14, pts: [[-20, 640], [300, 600], [700, 610], [1100, 640], [1330, 650], [2020, 660]] },
  { w: 12, pts: [[520, 520], [470, 360], [520, 190], [700, 120], [900, 130], [1080, 170], [1240, 120]] },
  { w: 12, pts: [[520, 520], [700, 560], [900, 540], [1100, 520], [1280, 470]] },
  { w: 8, pts: [[700, 120], [720, 320], [700, 560]] }, { w: 8, pts: [[470, 360], [720, 330], [960, 340], [1300, 330]] },
  { w: 8, pts: [[1330, 520], [1600, 480], [1850, 520], [2020, 500]] }, { w: 8, pts: [[1600, 480], [1620, 250], [1650, -20]] },
  { w: 8, pts: [[300, 600], [260, 800], [240, 900]] }, { w: 8, pts: [[1100, 640], [1080, 900]] }, { w: 6, pts: [[960, 340], [980, 520]] }];
const ROUTE = [[2020, 660], [1330, 650], [1300, 470], [1280, 470], [1100, 520], [960, 525], [960, 340], [900, 300]]; const PIN = [900, 300];
function polyLen(p) { let L = 0; for (let i = 1; i < p.length; i++) L += Math.hypot(p[i][0] - p[i - 1][0], p[i][1] - p[i - 1][1]); return L; }
function drawPoly(g, p, frac) { const L = polyLen(p) * frac; let acc = 0; g.beginPath(); g.moveTo(p[0][0], p[0][1]); for (let i = 1; i < p.length; i++) { const s = Math.hypot(p[i][0] - p[i - 1][0], p[i][1] - p[i - 1][1]); if (acc + s >= L) { const k = (L - acc) / s; const e = [lerp(p[i - 1][0], p[i][0], k), lerp(p[i - 1][1], p[i][1], k)]; g.lineTo(e[0], e[1]); g.stroke(); return e; } acc += s; g.lineTo(p[i][0], p[i][1]); } g.stroke(); return p[p.length - 1]; }
function drawMap(cd, t) { const { g, cv } = cd; faceBG(cd, '#0E6BB0', '#073F72'); g.save(); rrect(g, 0, 0, cv.width, cv.height, 60); g.clip();
  const gk = prog(t, 12.25, 12.7); g.globalAlpha = .5 * gk; g.strokeStyle = 'rgba(160,210,255,.14)'; g.lineWidth = 1; for (let x = 0; x < cv.width; x += 80) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, cv.height); g.stroke(); } for (let y = 0; y < cv.height; y += 80) { g.beginPath(); g.moveTo(0, y); g.lineTo(cv.width, y); g.stroke(); }
  g.globalAlpha = gk; g.strokeStyle = 'rgba(120,200,255,.6)'; g.lineWidth = 10; g.lineCap = 'round'; g.lineJoin = 'round'; drawPoly(g, [[-20, 760], [200, 720], [420, 790], [640, 860], [900, 830], [1200, 900]], 1);
  g.fillStyle = 'rgba(255,255,255,.08)'; g.beginPath(); g.moveTo(540, 500); g.lineTo(495, 360); g.lineTo(540, 210); g.lineTo(705, 145); g.lineTo(1060, 190); g.lineTo(1260, 140); g.lineTo(1300, 300); g.lineTo(1270, 455); g.lineTo(1100, 500); g.lineTo(700, 540); g.closePath(); g.fill();
  ROADS.forEach((r, i) => { const k = eOut(prog(t, 12.3 + i * .03, 12.75 + i * .03)); if (k <= 0) return; g.strokeStyle = 'rgba(210,235,255,.6)'; g.lineWidth = r.w * .8; drawPoly(g, r.pts, k); });
  const rk = eInOut(prog(t, 12.75, 13.6)); if (rk > 0) { g.globalAlpha = 1; g.save(); g.shadowColor = 'rgba(255,160,40,.95)'; g.shadowBlur = 26; g.strokeStyle = C.orangeL; g.lineWidth = 15; const end = drawPoly(g, ROUTE, rk); g.restore(); g.fillStyle = '#fff'; g.beginPath(); g.arc(end[0], end[1], 12, 0, 7); g.fill(); }
  const pd = prog(t, 13.55, 13.9); if (pd > 0) { const y = PIN[1] - 150 * (1 - eBack(pd, 1.6)) - 8; const rp = prog(t, 13.8, 14.5); if (rp > 0 && rp < 1) { g.globalAlpha = 1 - rp; g.strokeStyle = C.lime; g.lineWidth = 5; g.beginPath(); g.ellipse(PIN[0], PIN[1], 30 + rp * 120, 12 + rp * 46, 0, 0, 7); g.stroke(); }
    g.globalAlpha = clamp(pd * 2); g.fillStyle = 'rgba(0,0,0,.3)'; g.beginPath(); g.ellipse(PIN[0], PIN[1], 24, 9, 0, 0, 7); g.fill();
    g.save(); g.shadowColor = 'rgba(242,58,60,.7)'; g.shadowBlur = 30; const s = 120; g.fillStyle = C.red; g.beginPath(); g.arc(PIN[0], y - s * .62, s * .36, Math.PI * .82, Math.PI * 2.18); g.lineTo(PIN[0], y); g.closePath(); g.fill(); g.restore(); g.fillStyle = '#fff'; g.beginPath(); g.arc(PIN[0], y - s * .62, s * .15, 0, 7); g.fill(); }
  const lb = eOut(prog(t, 13.8, 14.15)); if (lb > 0) { g.globalAlpha = lb; const lx = 990, ly = 240, lw = 700; g.fillStyle = '#fff'; rrect(g, lx, ly - 80 + (1 - lb) * 16, lw, 200, 30); g.fill();
    g.textAlign = 'left'; g.fillStyle = C.orange; g.font = FL(38); g.fillText('LOKASI', lx + 40, ly - 20 + (1 - lb) * 16); g.fillStyle = C.ink; const s = fit(g, 'IPG KAMPUS PERLIS', FL, 70, lw - 70); g.font = FL(s); g.fillText('IPG KAMPUS PERLIS', lx + 40, ly + 70 + (1 - lb) * 16); }
  g.restore(); g.globalAlpha = 1; }
function cardCenter(name, off = [0, 0]) { boardG.updateMatrixWorld(true); return cards[name].grp.localToWorld(v3(off[0], off[1], .13)); }
const boardNormal = () => v3(0, 0, 1).applyQuaternion(boardG.quaternion).normalize();
function framing(name, dist, mixFront = .55, off = [0, 0]) { const c = cardCenter(name, off); const n = boardNormal().lerp(v3(0, 0, 1), 1 - mixFront).normalize(); return { p: c.clone().add(n.multiplyScalar(dist)), l: c }; }
function arcMove(t, a, b, t0, t1, pull = 0, ease = eInOut) { const k = ease(prog(t, t0, t1)); const mid = a.p.clone().lerp(b.p, .5); mid.add(mid.clone().sub(a.l.clone().lerp(b.l, .5)).normalize().multiplyScalar(pull)); return { p: a.p.clone().multiplyScalar((1 - k) ** 2).add(mid.multiplyScalar(2 * k * (1 - k))).add(b.p.clone().multiplyScalar(k * k)), l: a.l.clone().lerp(b.l, k) }; }
function drift(s, amt, k) { return { p: s.p.clone().add(s.l.clone().sub(s.p).multiplyScalar(amt * k)), l: s.l }; }
let FR = null;
function shots() { if (FR) return FR; const sv = Object.values(cards).map(c => [c.grp.scale.x, c.grp.position.z]); Object.values(cards).forEach(c => { c.grp.scale.setScalar(1); c.grp.position.z = 0; });
  FR = { over: { p: v3(0, -1.2, 36), l: v3(0, .2, 0) }, overFar: { p: v3(0, -2.2, 44), l: v3(0, .4, 0) }, cal: framing('cal', 15.5, .55, [0, -.1]), cal21: framing('cal', 14.0, .6, [.25, -.35]), ev: framing('ev', 15.2, .55), map: framing('map', 13.5, .6, [3.0, -.2]), mapPin: framing('map', 14.6, .62, [1.45, .2]) };
  Object.values(cards).forEach((c, i) => { c.grp.scale.setScalar(sv[i][0]); c.grp.position.z = sv[i][1]; }); return FR; }
function camBoard(t) { const S = shots();
  if (t < 7.2) return drift(S.overFar, .04, prog(t, TB0, 7.2));
  if (t < 8.05) return arcMove(t, drift(S.overFar, .04, 1), S.cal, 7.2, 8.05);
  if (t < 8.4) return drift(S.cal, .03, prog(t, 8.05, 8.4));
  if (t < 9.0) return arcMove(t, drift(S.cal, .03, 1), S.cal21, 8.4, 9.0);
  if (t < 9.85) return drift(S.cal21, .04, prog(t, 9.0, 9.85));
  if (t < 10.5) return arcMove(t, drift(S.cal21, .04, 1), S.ev, 9.85, 10.5, 9);
  if (t < 11.9) return drift(S.ev, .06, prog(t, 10.5, 11.9));
  if (t < 12.6) return arcMove(t, drift(S.ev, .06, 1), S.map, 11.9, 12.6, 8);
  if (t < 14.1) return arcMove(t, S.map, S.mapPin, 12.6, 13.9);
  return arcMove(t, S.mapPin, S.over, 14.1, 15.0, 0, eOut5); }

// ======================================================================
//  POST + OVERLAYS
// ======================================================================
const composer = new EffectComposer(renderer); const rp = new RenderPass(stadium, camera); composer.addPass(rp);
const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), .6, .35, .88); composer.addPass(bloom); composer.addPass(new OutputPass());
const $ = id => document.getElementById(id);
function setTxt(el, a, ty = 0, sc = 1, blur = 0, rot = 0) { el.style.opacity = a; el.style.transform = `translateY(${ty}px) scale(${sc}) rotate(${rot}deg)`; el.style.filter = blur > .1 ? `blur(${blur}px)` : 'none'; }
const tri = (t, a, m, b) => t < a || t > b ? 0 : t < m ? eInOut(prog(t, a, m)) : 1 - eInOut(prog(t, m, b));
function overlays(t) { const u = W / 1080;
  const hk = prog(t, 2.2, 2.45); setTxt($('haus'), clamp(hk * 2) * (1 - prog(t, 2.8, 2.95)), 0, lerp(1.6, 1, eOut5(hk)), (1 - eOut5(hk)) * 16 * u, -4);
  // brand reveal (3.0–6.6)
  const mb = eOut(prog(t, 4.3, 4.55)), out1 = 1 - prog(t, 6.35, 6.55);
  setTxt($('menuBaru'), mb * out1, (1 - mb) * 20 * u, lerp(.7, 1, eBack(prog(t, 4.3, 4.55))));
  const bl = prog(t, 4.45, 4.75); setTxt($('blast'), clamp(bl * 2) * out1, 0, lerp(1.5, 1, eOut5(bl)), (1 - eOut5(bl)) * 14 * u, -5 + Math.sin(t * 2) * .6);
  const tg = eOut(prog(t, 5.0, 5.35)); setTxt($('tagline'), tg * out1, (1 - tg) * 24 * u, 1, 0, -8); $('tagline').querySelector('.sw').style.transform = `scaleX(${eOut(prog(t, 5.25, 5.6))})`;
  // end card (15.4–20)
  const ig = eOut(prog(t, 16.0, 16.3)); setTxt($('endIG'), ig, (1 - ig) * 16 * u);
  const et = prog(t, 16.25, 16.6); setTxt($('endTag'), clamp(et * 2), 0, lerp(1.4, 1, eOut5(et)), (1 - eOut5(et)) * 12 * u, -3);
  const ei = eOut(prog(t, 16.8, 17.15)); setTxt($('endInfo'), ei, (1 - ei) * 30 * u, lerp(.9, 1, eBack(prog(t, 16.8, 17.15))));
  $('dip').style.opacity = Math.max(tri(t, 2.8, 3.0, 3.2), tri(t, 6.35, 6.6, 6.85), tri(t, 15.0, 15.3, 15.55));
  $('flash').style.opacity = Math.max(tri(t, .2, .22, .45) * .14, tri(t, .45, .47, .7) * .12, tri(t, .72, .74, .95) * .1, tri(t, .9, .92, 1.15) * .1, tri(t, 2.12, 2.16, 2.5) * .85, tri(t, 3.0, 3.05, 3.4) * .25);
  const wb = Math.max(tri(t, 2.75, 3.0, 3.25), tri(t, 6.3, 6.6, 6.9), tri(t, 14.95, 15.3, 15.6));
  renderer.domElement.style.filter = wb > .02 ? `blur(${wb * 10 * u}px)` : 'none'; }

// ======================================================================
//  RENDER
// ======================================================================
function placePlane(p, x, yBottom, width) { const h = width * p.userData.ar; p.scale.set(width, h, 1); p.position.set(x, yBottom + h / 2, p.position.z); }
function updateFruit(t, t0, mode) { ORS.forEach((o, i) => { const d = o.userData; const k = eBack(prog(t, t0 + i * .07, t0 + .5 + i * .07), 1.4); const from = d.base.clone().multiplyScalar(2.6);
    o.position.copy(from.lerp(d.base, clamp(k, 0, 1.2))); o.position.y += Math.sin(t * 1.3 + d.ph) * .08; if (mode === 'end') o.position.multiplyScalar(1.05);
    o.rotation.set(d.rotSp.x * t + d.ph, d.rotSp.y * t, d.rotSp.z * t); o.scale.setScalar(d.sc * clamp(k)); });
  ice.children.forEach(c => { c.position.copy(c.userData.base); c.position.y += Math.sin(t * 1.1 + c.userData.ph) * .1; c.rotation.set(t * .4 + c.userData.ph, t * .3, 0); c.scale.setScalar(clamp(prog(t, t0 + .3, t0 + .8))); });
  brandDrops.children.forEach((m, i) => { const d = m.userData; const tt = ((t - t0) * .35 * d.sp + i * .137) % 1; m.position.set(d.dir.x * 2.2 * (1 + tt), -3.4 + tt * 7.2, d.dir.z * 1.5 - .3); m.scale.setScalar(d.s * Math.sin(Math.PI * tt) * clamp(prog(t, t0, t0 + .5))); }); }
function renderAt(t) { t = clamp(t, 0, DURATION); overlays(t);
  if (t < 3.0) { // ---- HOOK
    towers.forEach(tw => { const on = eOut(prog(t, tw.ign, tw.ign + .18)); const flick = t > tw.ign && t < tw.ign + .25 ? (.75 + .25 * Math.sin(t * 90)) : 1; const v = on * flick;
      tw.lampMat.color.setRGB(4 * v, 3.8 * v, 3.3 * v); tw.flare.scale.setScalar(12 + 5 * v); tw.flare.material.opacity = .85 * v; tw.spot.intensity = (tw.ign > .6 ? 520 : 900) * v; tw.cone.material.uniforms.opacity.value = .5 * v; });
    dust.material.opacity = .55 * prog(t, .5, 1.5);
    const p = ballPos(t), swap = t >= 2.16; ball.visible = t > 1.05 && !swap; hookOrange.visible = swap;
    if (ball.visible) { const p2 = ballPos(t + .01), dir = p2.clone().sub(p); const axis = dir.lengthSq() > 1e-8 && t < 2.1 ? dir.normalize() : v3(.94, .2, -.28).normalize(); ball.position.copy(p); ball.quaternion.setFromUnitVectors(v3(0, 1, 0), axis); ball.rotateY((t - 1.05) * 26); }
    if (swap) { hookOrange.position.copy(p); hookOrange.rotation.set(.2, (t - 2.16) * 2.5, .15); const s = eBack(prog(t, 2.16, 2.36), 2.2); hookOrange.scale.setScalar(lerp(.6, 1, s)); }
    hookDrops.visible = swap; if (swap) { const k = prog(t, 2.16, 2.9); hookDrops.children.forEach(m => { const d = m.userData; const dd = d.dir.clone(); dd.z = -Math.abs(dd.z) - .2; m.position.copy(HERO).add(dd.multiplyScalar(eOut(k) * .32 * d.sp)).add(v3(0, -k * k * .2, 0)); m.scale.setScalar(d.s * .12 * (1 - k * .6)); }); }
    const hk = prog(t, 1.9, 2.2); heroKey.intensity = 3.2 * hk; heroKey.position.set(-1.2, 2.6, 30.4); heroKey.target.position.copy(p); heroRim.intensity = 7 * hk; heroRim.position.set(1.4, 2.2, 27.4); heroRim.target.position.copy(p);
    const k = eOut(prog(t, 0, 3.0)); camera.fov = 35; camera.position.set(0, lerp(1.25, 1.5, k), lerp(33.5, 30.6, k)); camera.lookAt(v3(0, lerp(16, 3.2, eInOut(prog(t, .2, 1.8))), -30).lerp(p, eInOut(prog(t, 1.2, 2.15))));
    camera.updateProjectionMatrix(); rp.scene = stadium; bloom.strength = .6; bloom.threshold = .88; renderer.toneMappingExposure = .9;
  } else if (t < TB0 || t >= TB1 + .1) { // ---- BRAND (reveal / end card)
    const end = t >= TB1; const t0 = end ? 15.3 : 3.0;
    updateFruit(t, t0, end ? 'end' : 'reveal');
    if (!end) { const a = eBack(prog(t, 3.05, 3.5), 1.6); const up = eInOut(prog(t, 3.85, 4.3)); logoPlane.position.z = 0; placePlane(logoPlane, 0, lerp(-.55, 1.48, up), lerp(3.1, 2.3, up) * clamp(a, 0, 1.2)); logoPlane.rotation.z = Math.sin(t * 2.4) * .03 * (1 - up) + (1 - clamp(a)) * .4;
      const c = eOut5(prog(t, 4.0, 4.55)); cupPlane.visible = t > 3.95; placePlane(cupPlane, .12, lerp(-7.2, -3.25, c), 3.75); cupPlane.rotation.z = Math.sin(t * 1.6) * .02; cupPlane.position.y += Math.sin(t * 1.8) * .04; }
    else { const a = eBack(prog(t, 15.4, 15.85), 1.6); placePlane(logoPlane, 0, 1.6, 2.15 * clamp(a, 0, 1.2)); logoPlane.rotation.z = 0;
      const c = eOut5(prog(t, 15.55, 16.15)); cupPlane.visible = true; placePlane(cupPlane, .25, lerp(-7.2, -3.3, c), 3.25); cupPlane.rotation.z = -.03 + Math.sin(t * 1.6) * .02; cupPlane.position.y += Math.sin(t * 1.8) * .04; }
    const dz = end ? prog(t, 15.3, 20) : prog(t, 3.0, 6.6); camera.fov = 35; camera.position.set(Math.sin(t * .35) * .25, lerp(.1, -.05, dz), lerp(10.6, 9.6, eOut(dz))); camera.lookAt(0, 0, 0); camera.updateProjectionMatrix();
    rp.scene = brand; bloom.strength = .18; bloom.threshold = .97; renderer.toneMappingExposure = 1.0;
  } else { // ---- BOARD
    ['header', 'cal', 'ev', 'map'].forEach((n, i) => { const c = cards[n]; const k = eOut(prog(t, TB0 + .05 + i * .12, TB0 + .4 + i * .12)); c.grp.scale.setScalar(lerp(.86, 1, k)); c.grp.position.z = (1 - k) * 1.2; c.slabMat.opacity = k; c.faceMat.opacity = k; c.draw(c, t); c.tex.needsUpdate = true; });
    const s = camBoard(t); camera.fov = 35; camera.position.copy(s.p); camera.lookAt(s.l); camera.updateProjectionMatrix();
    rp.scene = board; bloom.strength = .25; bloom.threshold = .98; renderer.toneMappingExposure = 1.0; }
  composer.render(); }
window.renderAt = renderAt; window.DURATION = DURATION;
window.ready = (async () => {
  await Promise.all([document.fonts.load(FL(40)), document.fonts.load(FB(40)), ...[900, 800, 700, 600].map(w => document.fonts.load(F(w, 40)))]); await document.fonts.ready;
  await Promise.all([imgLoad('perahlab_logo'), imgLoad('logo_ipg10s'), imgLoadJ('htk', 'assets/src/logo_htk26.jpg')]);
  const mk = async (f) => { const tx = await loadTex(f); const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: tx, transparent: true, toneMapped: false })); m.userData.ar = tx.image.height / tx.image.width; brand.add(m); return m; };
  logoPlane = await mk('assets/perahlab_logo.png'); logoPlane.position.z = .2; logoPlane.renderOrder = 2;
  cupPlane = await mk('assets/cup_hand.png'); cupPlane.position.z = .5; cupPlane.renderOrder = 3;
  renderAt(0); return true; })();
