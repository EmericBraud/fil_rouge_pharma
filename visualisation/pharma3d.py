"""
pharma3d.py — Rendu 3D Three.js via st.components.v1.html
"""

import json
import networkx as nx
import streamlit.components.v1 as components
from collections import defaultdict

from data_file import POS, EDGES

OFFSET = 35


def compute_full_path(medications: list, order_ids: list):
    def euclidean(a, b, pos):
        return ((pos[a][0] - pos[b][0]) ** 2 + (pos[a][1] - pos[b][1]) ** 2) ** 0.5

    G = nx.Graph()
    pos = POS.copy()
    for u, v in EDGES:
        G.add_edge(u, v, weight=euclidean(u, v, pos))

    edge_to_meds = defaultdict(list)
    for m in medications:
        key = (min(m["u"], m["v"]), max(m["u"], m["v"]))
        edge_to_meds[key].append(m)

    med_pos = {}
    for (u, v), meds_on_edge in edge_to_meds.items():
        sorted_meds = sorted(meds_on_edge, key=lambda m: m["dist_u"])
        pu, pv = POS[u], POS[v]
        for m in sorted_meds:
            nid = m["id"] + OFFSET
            du, dv = m["dist_u"], m["dist_v"]
            pos[nid] = (
                (dv * pu[0] + du * pv[0]) / (du + dv),
                (dv * pu[1] + du * pv[1]) / (du + dv),
            )
            med_pos[nid] = pos[nid]
        if G.has_edge(u, v):
            G.remove_edge(u, v)
        chain = [u] + [m["id"] + OFFSET for m in sorted_meds] + [v]
        for a, b in zip(chain, chain[1:]):
            G.add_edge(a, b, weight=euclidean(a, b, pos))

    points = [35] + [oid + OFFSET for oid in order_ids] + [0]
    full_path = []
    for i in range(len(points) - 1):
        try:
            p = nx.shortest_path(G, points[i], points[i + 1], weight="weight")
            full_path.extend(p if i == 0 else p[1:])
        except Exception:
            pass
    return full_path, med_pos


def render_3d_pharmacy(medications: list, order_ids: list, height: int = 700):
    full_path, med_pos = compute_full_path(medications, order_ids)

    pos_json = json.dumps({str(k): list(v) for k, v in POS.items()})
    edges_json = json.dumps([[u, v] for u, v in EDGES])
    path_json = json.dumps(full_path)
    order_json = json.dumps(order_ids)
    meds_json = json.dumps(medications)
    med_pos_json = json.dumps({str(k): list(v) for k, v in med_pos.items()})

    html = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"/>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0a0e1a; overflow:hidden; font-family:'Courier New',monospace; }}
canvas {{ display:block; }}

#ui {{
  position:absolute; top:14px; left:14px; color:#a0f0c0; font-size:11px;
  pointer-events:none; text-shadow:0 0 6px #00ff88; max-width:175px;
}}
#ui h3 {{ font-size:12px; color:#00ff88; margin-bottom:5px; letter-spacing:2px; }}
.step {{ padding:1px 0; opacity:0.4; transition:all .3s; }}
.step.active {{ opacity:1; color:#ffdd44; text-shadow:0 0 8px #ffaa00; font-weight:bold; }}
.step.done   {{ opacity:0.3; color:#44ff88; text-decoration:line-through; }}

#legend {{
  position:absolute; top:14px; right:14px; color:#a0f0c0; font-size:10px;
  background:rgba(0,0,0,.4); padding:8px 10px; border-radius:6px;
  border:1px solid #1a3040;
}}
.leg {{ display:flex; align-items:center; gap:5px; margin-bottom:3px; }}
.dot {{ width:9px; height:9px; border-radius:50%; flex-shrink:0; }}

#bottom {{
  position:absolute; bottom:10px; left:50%; transform:translateX(-50%);
  display:flex; flex-direction:column; align-items:center; gap:5px;
}}
.row {{ display:flex; align-items:center; gap:10px; color:#a0f0c0; font-size:10px; }}
input[type=range] {{ accent-color:#00ff88; width:90px; }}
button {{
  background:rgba(0,255,136,.1); border:1px solid #00ff88; color:#00ff88;
  padding:5px 12px; border-radius:3px; cursor:pointer;
  font-family:'Courier New',monospace; font-size:10px; letter-spacing:1px;
  transition:background .15s;
}}
button:hover {{ background:rgba(0,255,136,.25); }}
button.active {{ background:rgba(0,255,136,.3); color:#fff; }}

#hint {{
  position:absolute; bottom:80px; right:14px;
  color:#4a6a7a; font-size:9px; text-align:right; pointer-events:none;
}}
:fullscreen canvas, :-webkit-full-screen canvas {{ width:100vw !important; height:100vh !important; }}
</style>
</head>
<body>
<canvas id="c"></canvas>

<div id="ui">
  <h3>▶ TRAJET OPTIMAL</h3>
  <div id="steps"></div>
</div>

<div id="legend">
  <div class="leg"><div class="dot" style="background:#00ff88"></div>Départ (35)</div>
  <div class="leg"><div class="dot" style="background:#4488ff"></div>Arrivée (0)</div>
  <div class="leg"><div class="dot" style="background:#aaaaaa"></div>Nœud</div>
  <div class="leg"><div class="dot" style="background:#ff3333"></div>Médicament</div>
  <div class="leg"><div class="dot" style="background:#ffdd44"></div>Pharmacien</div>
  <div class="leg"><div class="dot" style="background:#ff8800"></div>Nœud courant</div>
  <div class="leg"><div class="dot" style="background:#00cc66; border-radius:2px;"></div>Chemin parcouru</div>
</div>

<div id="hint">🖱 Drag: orbite · Molette: zoom</div>

<div id="bottom">
  <div class="row">
    <span>Vitesse</span>
    <input type="range" id="spd" min="0.3" max="8" step="0.3" value="2"/>
    <button id="bp">⏸ PAUSE</button>
    <button id="br">↺ REJOUER</button>
    <button id="bo" class="active">🔄 AUTO-CAM</button>
    <button id="bfs">⛶ PLEIN ÉCRAN</button>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// ── Data ─────────────────────────────────────────────────────────────────────
const POS       = {pos_json};
const EDGES     = {edges_json};
const FULL_PATH = {path_json};
const ORDER_IDS = {order_json};
const MEDS      = {meds_json};
const MED_POS   = {med_pos_json};
const OFFSET    = 35;
const SCALE     = 1.3;

// ── Renderer ─────────────────────────────────────────────────────────────────
const canvas = document.getElementById('c');
canvas.width  = window.innerWidth;
canvas.height = window.innerHeight;
const renderer = new THREE.WebGLRenderer({{canvas, antialias:true}});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x080c14);
scene.fog = new THREE.FogExp2(0x080c14, 0.032);

// ── Camera ───────────────────────────────────────────────────────────────────
const camera = new THREE.PerspectiveCamera(40, window.innerWidth/window.innerHeight, 0.1, 300);
// Target = centre of graph
const CX = 5.5 * SCALE, CZ = -3 * SCALE;
camera.position.set(CX, 22, CZ + 20);
camera.lookAt(CX, 0, CZ);

// Orbit state
let orbitAuto  = true;
let isDragging = false;
let dragStart  = {{x:0, y:0}};
let theta = 0, phi = 1.1;   // spherical coords
let radius = 26;
const MIN_R = 6, MAX_R = 55;

function updateCamera() {{
  camera.position.x = CX + radius * Math.sin(phi) * Math.sin(theta);
  camera.position.y =      radius * Math.cos(phi);
  camera.position.z = CZ + radius * Math.sin(phi) * Math.cos(theta);
  camera.lookAt(CX, 1, CZ);
}}

// Drag
canvas.addEventListener('mousedown', e => {{
  isDragging = true; dragStart = {{x:e.clientX, y:e.clientY}};
  orbitAuto  = false;
  document.getElementById('bo').classList.remove('active');
}});
canvas.addEventListener('mousemove', e => {{
  if (!isDragging) return;
  const dx = e.clientX - dragStart.x;
  const dy = e.clientY - dragStart.y;
  theta -= dx * 0.005;
  phi    = Math.max(0.15, Math.min(Math.PI/2 - 0.05, phi + dy * 0.005));
  dragStart = {{x:e.clientX, y:e.clientY}};
  updateCamera();
}});
canvas.addEventListener('mouseup',    () => {{ isDragging = false; }});
canvas.addEventListener('mouseleave', () => {{ isDragging = false; }});

// Zoom
canvas.addEventListener('wheel', e => {{
  e.preventDefault();
  e.stopPropagation();
  radius = Math.max(MIN_R, Math.min(MAX_R, radius + e.deltaY * 0.05));
  updateCamera();
}}, {{ passive: false }});

// Auto-cam toggle
document.getElementById('bo').onclick = () => {{
  orbitAuto = !orbitAuto;
  document.getElementById('bo').classList.toggle('active', orbitAuto);
}};

// ── Lights ───────────────────────────────────────────────────────────────────
scene.add(new THREE.AmbientLight(0x1a2a3a, 3));
const sun = new THREE.DirectionalLight(0x8ab8d0, 0.8);
sun.position.set(10, 25, 10); sun.castShadow = true;
scene.add(sun);
const walkerLight = new THREE.PointLight(0xffdd44, 3.5, 8);
scene.add(walkerLight);
[[3,8],[6,4],[6,0],[6,-2],[8.5,4],[8.5,0]].forEach(([gx,gy]) => {{
  const l = new THREE.PointLight(0x6a9abf, 0.45, 6);
  l.position.set(gx*SCALE, 4, -gy*SCALE);
  scene.add(l);
}});

// ── Helpers ───────────────────────────────────────────────────────────────────
function toW(gx, gy) {{ return new THREE.Vector3(gx*SCALE, 0, -gy*SCALE); }}
function nodeWorld(nid) {{
  const s = String(nid);
  if (MED_POS[s]) return toW(MED_POS[s][0], MED_POS[s][1]);
  if (POS[s])     return toW(POS[s][0], POS[s][1]);
  return null;
}}

// ── Floor ─────────────────────────────────────────────────────────────────────
const floor = new THREE.Mesh(
  new THREE.PlaneGeometry(34,30),
  new THREE.MeshLambertMaterial({{color:0x0e1520}})
);
floor.rotation.x = -Math.PI/2;
floor.position.set(CX, -0.01, CZ);
floor.receiveShadow = true;
scene.add(floor);
const grid = new THREE.GridHelper(34, 34, 0x182535, 0x182535);
grid.position.set(CX, 0.001, CZ);
grid.material.transparent = true; grid.material.opacity = 0.5;
scene.add(grid);


// ── Canvas 2D for labels ──────────────────────────────────────────────────────
function makeLabel(text, color='#ffffff', bgColor='rgba(0,0,0,0.55)') {{
  const c = document.createElement('canvas');
  c.width = 128; c.height = 48;
  const ctx = c.getContext('2d');
  ctx.fillStyle = bgColor;
  ctx.roundRect(2, 8, 124, 32, 6);
  ctx.fill();
  ctx.fillStyle = color;
  ctx.font = 'bold 20px Courier New';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, 64, 24);
  const tex = new THREE.CanvasTexture(c);
  const mat = new THREE.SpriteMaterial({{map:tex, transparent:true, depthTest:false}});
  const sprite = new THREE.Sprite(mat);
  sprite.scale.set(0.9, 0.34, 1);
  return sprite;
}}

// ── Nodes ─────────────────────────────────────────────────────────────────────
const nodeSprites = {{}};   // nid → sprite (for highlight update)
const nodeMeshes  = {{}};   // nid → mesh

Object.entries(POS).forEach(([nid,[gx,gy]]) => {{
  const id = parseInt(nid);
  const isStart = id===35, isEnd = id===0;
  const col = isStart ? 0x00ff88 : isEnd ? 0x4488ff : 0x778899;
  const r   = isStart||isEnd ? 0.24 : 0.13;

  const geo = new THREE.SphereGeometry(r, 14, 10);
  const mat = new THREE.MeshLambertMaterial({{
    color:col, emissive:col,
    emissiveIntensity: isStart||isEnd ? 0.7 : 0.15
  }});
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.copy(toW(gx,gy));
  mesh.position.y = r;
  scene.add(mesh);
  nodeMeshes[id] = mesh;

  // Label
  const labelColor = isStart ? '#00ff88' : isEnd ? '#88aaff' : '#aabbcc';
  const spr = makeLabel(String(id), labelColor);
  spr.position.copy(mesh.position);
  spr.position.y += r + 0.45;
  scene.add(spr);
  nodeSprites[id] = spr;
}});

// Med nodes
MEDS.forEach(m => {{
  const key = String(m.id+OFFSET);
  const p = MED_POS[key]; if (!p) return;
  const geo = new THREE.SphereGeometry(0.19,12,8);
  const mat = new THREE.MeshLambertMaterial({{color:0xff3333,emissive:0xff1111,emissiveIntensity:0.5}});
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(p[0]*SCALE, 0.19, -p[1]*SCALE);
  scene.add(mesh);
  nodeMeshes[m.id+OFFSET] = mesh;

  const spr = makeLabel('M'+m.id, '#ff8888');
  spr.position.copy(mesh.position);
  spr.position.y += 0.55;
  scene.add(spr);
  nodeSprites[m.id+OFFSET] = spr;

  // Glow ring
  const rg = new THREE.RingGeometry(0.25,0.36,20);
  const rm = new THREE.MeshBasicMaterial({{color:0xff3333,transparent:true,opacity:0.3,side:THREE.DoubleSide}});
  const ring = new THREE.Mesh(rg, rm);
  ring.rotation.x = -Math.PI/2;
  ring.position.set(p[0]*SCALE, 0.02, -p[1]*SCALE);
  scene.add(ring);
}});

// ── Highlight current node ────────────────────────────────────────────────────
let lastHighlightId = -1;
const highlightGeo = new THREE.SphereGeometry(0.32, 14, 10);
const highlightMat = new THREE.MeshBasicMaterial({{
  color:0xff8800, transparent:true, opacity:0.45, wireframe:true
}});
const highlightMesh = new THREE.Mesh(highlightGeo, highlightMat);
highlightMesh.visible = false;
scene.add(highlightMesh);

function setHighlight(nid) {{
  if (nid === lastHighlightId) return;
  lastHighlightId = nid;
  const w = nodeWorld(nid);
  if (!w) {{ highlightMesh.visible=false; return; }}
  highlightMesh.position.set(w.x, 0.32, w.z);
  highlightMesh.visible = true;
}};

// ── Path lines ────────────────────────────────────────────────────────────────
const pathPts = FULL_PATH.map(nid => {{
  const w = nodeWorld(nid); if (!w) return null;
  return new THREE.Vector3(w.x, 0.07, w.z);
}}).filter(Boolean);

if (pathPts.length >= 2) {{
  const ag = new THREE.BufferGeometry().setFromPoints(pathPts);
  scene.add(new THREE.Line(ag,
    new THREE.LineBasicMaterial({{color:0x1a3a55, transparent:true, opacity:0.6}})));
}}
const doneGeo = new THREE.BufferGeometry();
const doneLine = new THREE.Line(doneGeo,
  new THREE.LineBasicMaterial({{color:0x00cc66, transparent:true, opacity:0.9}}));
scene.add(doneLine);

// ── Walker ────────────────────────────────────────────────────────────────────
const walkerG = new THREE.Group();
const bodyMat = new THREE.MeshLambertMaterial({{color:0xffdd44,emissive:0xcc9900,emissiveIntensity:0.35}});
const body = new THREE.Mesh(new THREE.CylinderGeometry(0.11,0.11,0.46,10), bodyMat);
body.position.y=0.33; walkerG.add(body);
const head = new THREE.Mesh(new THREE.SphereGeometry(0.14,12,8), bodyMat);
head.position.y=0.67; walkerG.add(head);
const legMat = new THREE.MeshLambertMaterial({{color:0xcc8800}});
const legL = new THREE.Mesh(new THREE.CylinderGeometry(0.044,0.044,0.26,8), legMat);
legL.position.set(-0.07,0.09,0); walkerG.add(legL);
const legR = new THREE.Mesh(new THREE.CylinderGeometry(0.044,0.044,0.26,8), legMat.clone());
legR.position.set( 0.07,0.09,0); walkerG.add(legR);
const pack = new THREE.Mesh(new THREE.BoxGeometry(0.15,0.19,0.1),
  new THREE.MeshLambertMaterial({{color:0x335577}}));
pack.position.set(0,0.34,-0.13); walkerG.add(pack);

if (pathPts.length > 0) walkerG.position.copy(pathPts[0]);
scene.add(walkerG);

// ── Steps UI ──────────────────────────────────────────────────────────────────
const medMap = {{}};
MEDS.forEach(m => {{ medMap[m.id]=m; }});
const stepsEl = document.getElementById('steps');
const stepNodeIds = [35, ...ORDER_IDS.map(id=>id+OFFSET), 0];
const stepLabels  = [
  '🟢 DÉPART',
  ...ORDER_IDS.map(id => {{
    const m=medMap[id];
    return `💊 Med ${{id}}` + (m?` (${{m.u}}-${{m.v}})`:'');
  }}),
  '🔵 ARRIVÉE'
];
stepLabels.forEach((s,i) => {{
  const d = document.createElement('div');
  d.className='step'; d.id=`st${{i}}`; d.textContent=s;
  stepsEl.appendChild(d);
}});

// ── Animation ─────────────────────────────────────────────────────────────────
let currentT=0, playing=true;
let lastTime=performance.now();
let autoTheta=0;

function animate() {{
  requestAnimationFrame(animate);
  const now=performance.now();
  const dt=Math.min((now-lastTime)/1000, 0.05);
  lastTime=now;

  const speed=parseFloat(document.getElementById('spd').value);

  if (playing && pathPts.length>1) {{
    currentT=Math.min(currentT+dt*speed, pathPts.length-1);
    const idx=Math.floor(currentT), frac=currentT-idx;
    const pA=pathPts[Math.min(idx,   pathPts.length-1)];
    const pB=pathPts[Math.min(idx+1, pathPts.length-1)];
    const wPos=pA.clone().lerp(pB,frac);

    walkerG.position.copy(wPos); walkerG.position.y=0;
    if (!pA.equals(pB)) {{
      walkerG.rotation.y=Math.atan2(pB.x-pA.x, pB.z-pA.z);
    }}
    const ls=now*0.007*speed;
    legL.rotation.x= Math.sin(ls)*0.55;
    legR.rotation.x=-Math.sin(ls)*0.55;

    walkerLight.position.set(wPos.x,1.8,wPos.z);

    const dPts=pathPts.slice(0,idx+2).map((p,i)=>
      i===idx+1?pA.clone().lerp(pB,frac):p);
    if (dPts.length>=2) doneGeo.setFromPoints(dPts);

    // Highlight current node
    const curNodeId=FULL_PATH[Math.min(idx,FULL_PATH.length-1)];
    setHighlight(curNodeId);

    // Step UI
    const visited=new Set(FULL_PATH.slice(0,idx+1));
    document.querySelectorAll('.step').forEach(el=>el.classList.remove('active','done'));
    const s0=document.getElementById('st0');
    if (s0) s0.classList.add(idx>0?'done':'active');
    ORDER_IDS.forEach((oid,i)=>{{
      const el=document.getElementById(`st${{i+1}}`); if(!el) return;
      if (visited.has(oid+OFFSET)) el.classList.add('done');
    }});
    const last=document.getElementById(`st${{stepLabels.length-1}}`);
    if (last && visited.has(0)) last.classList.add('done');

    if (currentT>=pathPts.length-1) playing=false;
  }}

  // Auto-orbit (gentle, only when enabled)
  if (orbitAuto) {{
    autoTheta += dt*0.06;
    theta = autoTheta;
    updateCamera();
  }}

  renderer.render(scene, camera);
}}
animate();

// ── Playback controls ────────────────────────────────────────────────────────
document.getElementById('bp').onclick=()=>{{
  playing=!playing;
  document.getElementById('bp').textContent=playing?'⏸ PAUSE':'▶ PLAY';
}};
document.getElementById('br').onclick=()=>{{
  currentT=0; playing=true;
  document.getElementById('bp').textContent='⏸ PAUSE';
  if (pathPts.length>0) doneGeo.setFromPoints([pathPts[0]]);
}};

// Fullscreen
document.getElementById('bfs').onclick = () => {{
  const el = document.documentElement;
  if (!document.fullscreenElement) {{
    el.requestFullscreen && el.requestFullscreen();
    document.getElementById('bfs').textContent = '✕ QUITTER';
  }} else {{
    document.exitFullscreen && document.exitFullscreen();
    document.getElementById('bfs').textContent = '⛶ PLEIN ÉCRAN';
  }}
}};
document.addEventListener('fullscreenchange', () => {{
  const isFs = !!document.fullscreenElement;
  renderer.setSize(window.innerWidth, window.innerHeight);
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  document.getElementById('bfs').textContent = isFs ? '✕ QUITTER' : '⛶ PLEIN ÉCRAN';
}});

window.addEventListener('resize',()=>{{
  camera.aspect=window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth,window.innerHeight);
}});

updateCamera();
</script></body></html>"""

    components.html(html, height=height, scrolling=False)
