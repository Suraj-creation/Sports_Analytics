"""
annotate_court.py — browser-based court annotation.

Run:
    python3 annotate_court.py --video video_fixed/Test9_Full.mp4 --out court.json

Then open  http://localhost:5050  in your browser.
Click the 8 court points in order, then hit Save.

Which frame gets shown to click on:
  --frame N        use exactly this frame (you already know a good timestamp)
  --auto_frame      search the WHOLE video for the frame with the clearest,
                    largest detected court region, and use that (see
                    find_best_frame() below) -- for a full broadcast, the
                    fixed default (frame 90, ~3s in) is usually still intro/
                    sponsor graphics, not rally footage.
  (neither)         defaults to frame 90 -- fine for a pre-trimmed rally clip.
"""

import argparse, base64, json, os, sys, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frame_picker import rank_candidate_frames, pick_frame_fast

LABELS = ['TL', 'TR', 'BR', 'BL', 'NL', 'NR', 'CL', 'CR']
DESCS  = [
    'Top-Left court corner',
    'Top-Right court corner',
    'Bottom-Right court corner',
    'Bottom-Left court corner',
    'Left net post base (ground)',
    'Right net post base (ground)',
    'Left net cable top',
    'Right net cable top',
]
COLORS = ['#00ff64','#00b4ff','#ff0000','#ff5000',
          '#b400ff','#ff00b4','#00ffff','#ffff00']


ap = argparse.ArgumentParser()
ap.add_argument('--video', required=True)
ap.add_argument('--out',   required=True)
ap.add_argument('--frame', type=int, default=None,
                help='Exact frame to annotate (default: 90, or the result '
                     'of --auto_frame if given)')
ap.add_argument('--auto_frame', action='store_true',
                help='Try the video midpoint, checking a few nearby frames '
                     'if needed, for a frame that clearly shows the court -- '
                     'instead of using a fixed default. Use this for full '
                     'broadcasts, not needed for pre-trimmed clips. Cheap '
                     '(at most 1 + --max_fallback_frames frame reads).')
ap.add_argument('--search_step_sec', type=float, default=5.0,
                help='--auto_frame fallback candidate spacing in seconds '
                     '(default 5.0), only used if the first try isn\'t good enough')
ap.add_argument('--search_start_frame', type=int, default=None,
                help='--auto_frame tries this frame first instead of the '
                     'video midpoint -- use if you already know roughly '
                     'where play starts (e.g. 900 = 30s in @ 30fps)')
ap.add_argument('--max_fallback_frames', type=int, default=20,
                help='--auto_frame: if the first frame tried isn\'t good '
                     'enough, check at most this many more before giving up '
                     '(default 20)')
ap.add_argument('--full_scan', action='store_true',
                help='--auto_frame: scan the WHOLE video (rank_candidate_frames) '
                     'instead of the fast midpoint-first search. Much slower '
                     'on a long broadcast -- only use if the fast search '
                     'genuinely can\'t find a good frame.')
ap.add_argument('--port',  type=int, default=5050)
ap.add_argument('--no_preprocess', action='store_true',
                help='Skip the automatic codec/resolution/fps check+fix '
                     '(video_utils.ensure_preprocessed). Use if you already '
                     'know the video is H.264 1280x720@30fps and want to '
                     'skip the ffprobe check, or are deliberately annotating '
                     'a video at a different resolution.')
ap.add_argument('--no_stability_check', action='store_true',
                help='--auto_frame: skip verifying the candidate frame is part '
                     'of a sustained (>=3s) consistent court view -- only the '
                     'single-frame area/center/margin score decides. Faster, '
                     'but risks landing on a transitional frame (e.g. mid '
                     'camera-pan) that is not representative of the frames '
                     'court_presence.py will later check against it.')
args = ap.parse_args()

if not args.no_preprocess:
    from video_utils import ensure_preprocessed
    args.video = str(ensure_preprocessed(args.video))

# candidate_frames: ranked alternative frame numbers to offer via the
# browser's "Try Different Frame" button. Populated by --auto_frame;
# without it, that button just steps forward --search_step_sec at a time
# with no scoring (still useful for manually browsing).
candidate_frames = []
candidate_idx = 0

if args.frame is not None:
    frame_no = args.frame
elif args.auto_frame:
    if args.full_scan:
        ranked = rank_candidate_frames(args.video, args.search_step_sec,
                                       start_frame=args.search_start_frame or 0,
                                       verify_stable=not args.no_stability_check)
    else:
        ranked = pick_frame_fast(args.video, args.search_step_sec,
                                 args.max_fallback_frames,
                                 start_frame=args.search_start_frame,
                                 verify_stable=not args.no_stability_check)
    candidate_frames = [fno for fno, _, _ in ranked]
    frame_no = candidate_frames[0]
else:
    frame_no = 90
args.frame = frame_no

VIDEO_CAP = cv2.VideoCapture(args.video)
VW  = int(VIDEO_CAP.get(cv2.CAP_PROP_FRAME_WIDTH))
VH  = int(VIDEO_CAP.get(cv2.CAP_PROP_FRAME_HEIGHT))
VFPS = VIDEO_CAP.get(cv2.CAP_PROP_FPS) or 30.0
VTOTAL = int(VIDEO_CAP.get(cv2.CAP_PROP_FRAME_COUNT))
NEXT_STEP_FRAMES = max(1, int(args.search_step_sec * VFPS))


def _read_frame_no(fno):
    fno = max(0, min(VTOTAL - 1, fno))
    VIDEO_CAP.set(cv2.CAP_PROP_POS_FRAMES, fno)
    ok, frame = VIDEO_CAP.read()
    if not ok:
        raise RuntimeError(f'Cannot read frame {fno} from {args.video}')
    return frame


# ── read the initial frame ──────────────────────────────────────────────────────
bgr = _read_frame_no(args.frame)

_, jpg  = cv2.imencode('.jpg', bgr, [cv2.IMWRITE_JPEG_QUALITY, 92])
IMG_B64 = base64.b64encode(jpg.tobytes()).decode()

points = []   # accumulated [x, y] pairs

# ── HTML ───────────────────────────────────────────────────────────────────────
HTML = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Court Annotation</title>
<style>
body{{margin:0;background:#111;color:#eee;font-family:monospace}}
h2{{margin:8px 14px;font-size:14px}}
#bar{{background:#1a1a1a;padding:7px 14px;font-size:13px;border-bottom:1px solid #333}}
#next{{color:#3f3;font-weight:bold}}
button{{padding:5px 13px;font-size:12px;cursor:pointer;border:none;border-radius:4px;margin-left:8px}}
#undo{{background:#444;color:#eee}}
#nextframe{{background:#a60;color:#fff}}
#save{{background:#1a8;color:#fff;display:none}}
#wrap{{position:relative;display:inline-block}}
img{{display:block;max-width:100vw;cursor:crosshair}}
.dot{{position:absolute;width:14px;height:14px;border-radius:50%;
      transform:translate(-50%,-50%);border:2px solid #fff;
      font-size:9px;font-weight:bold;color:#000;
      display:flex;align-items:center;justify-content:center;
      pointer-events:none}}
</style></head>
<body>
<h2 id="title">Court Annotation — {os.path.basename(args.video)} — frame {args.frame} — {VW}×{VH}</h2>
<div id="bar">
  <span id="next">Click TL — Top-Left court corner &nbsp;(1 / {len(LABELS)})</span>
  <button id="undo" onclick="undo()">↩ Undo</button>
  <button id="nextframe" onclick="nextFrame()">🔄 Try Different Frame</button>
  <button id="save" onclick="save()">💾 Save</button>
</div>
<div id="wrap">
  <img id="img" src="data:image/jpeg;base64,{IMG_B64}" onclick="clicked(event)">
</div>
<script>
const LABELS={json.dumps(LABELS)};
const DESCS={json.dumps(DESCS)};
const COLORS={json.dumps(COLORS)};
const VIDEO_NAME={json.dumps(os.path.basename(args.video))};
const VW={VW}, VH={VH};
let pts=[], scaleX=1, scaleY=1;
const img=document.getElementById('img');
const wrap=document.getElementById('wrap');
function getScale(){{
  const r=img.getBoundingClientRect();
  scaleX=VW/r.width; scaleY=VH/r.height;
}}
img.onload=getScale;
window.onresize=getScale;
function clicked(e){{
  if(pts.length>={len(LABELS)}) return;
  getScale();
  const r=img.getBoundingClientRect();
  const x=Math.round((e.clientX-r.left)*scaleX);
  const y=Math.round((e.clientY-r.top)*scaleY);
  const px=e.clientX-r.left, py=e.clientY-r.top;
  pts.push([x,y]);
  const d=document.createElement('div');
  d.className='dot'; d.id='dot'+(pts.length-1);
  d.style.left=px+'px'; d.style.top=py+'px';
  d.style.background=COLORS[pts.length-1];
  d.textContent=LABELS[pts.length-1];
  wrap.appendChild(d);
  fetch('/click',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{x,y}})}});
  update();
}}
function undo(){{
  if(!pts.length) return;
  const i=pts.length-1;
  pts.pop();
  const d=document.getElementById('dot'+i); if(d) d.remove();
  fetch('/undo',{{method:'POST'}});
  update();
}}
function nextFrame(){{
  document.getElementById('nextframe').disabled=true;
  fetch('/next_frame',{{method:'POST'}})
    .then(r=>r.json())
    .then(data=>{{
      img.src='data:image/jpeg;base64,'+data.image;
      document.getElementById('title').textContent=
        `Court Annotation — ${{VIDEO_NAME}} — frame ${{data.frame_no}} — ${{VW}}×${{VH}}`
        + (data.remaining!==undefined ? ` — ${{data.remaining}} alternative(s) left` : '');
      pts=[];
      document.querySelectorAll('.dot').forEach(d=>d.remove());
      update();
      document.getElementById('nextframe').disabled=false;
    }});
}}
function save(){{
  fetch('/save',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(pts)}})
    .then(()=>{{document.getElementById('next').textContent='✅ Saved! You can close this tab.';}});
}}
function update(){{
  const n=pts.length;
  document.getElementById('save').style.display=n>={len(LABELS)}?'inline-block':'none';
  document.getElementById('next').textContent=
    n<{len(LABELS)}
      ? `Click ${{LABELS[n]}} — ${{DESCS[n]}} (${{n+1}} / {len(LABELS)})`
      : 'All 8 points placed —';
}}
</script>
</body></html>"""

# ── HTTP server ────────────────────────────────────────────────────────────────
# Threaded + a per-request timeout: the plain single-threaded HTTPServer
# handles one request at a time on the main thread -- if a client's
# connection stalls mid-response (slow/flaky network, browser tab that never
# finishes reading), wfile.write() can block indefinitely with no timeout,
# freezing the entire server for every other request including "Try
# Different Frame"/"Save" from the SAME browser tab. Verified: this hung a
# real session for 5+ minutes with the process alive and the socket still
# accepting connections, but never responding. ThreadingHTTPServer isolates
# each request to its own thread; `timeout` bounds how long any one of them
# can block.
server_ref = None   # set after ThreadingHTTPServer is created
STATE_LOCK = threading.Lock()

class Handler(BaseHTTPRequestHandler):
    timeout = 30

    def log_message(self, *a): pass

    def do_GET(self):
        body = HTML.encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body   = self.rfile.read(length)

        # ThreadingHTTPServer runs each request on its own thread -- these
        # all mutate shared state (points/bgr/args.frame/candidate_idx), so
        # serialize them. A single interactive user clicking sequentially
        # won't usually contend, but a double-click or the browser retrying
        # a slow request could otherwise race.
        with STATE_LOCK:
            return self._handle_post(body)

    def _handle_post(self, body):
        if self.path == '/click':
            pt = json.loads(body)
            points.append([pt['x'], pt['y']])

        elif self.path == '/undo':
            if points:
                points.pop()

        elif self.path == '/next_frame':
            global bgr, candidate_idx
            points.clear()
            if candidate_idx + 1 < len(candidate_frames):
                candidate_idx += 1
                fno = candidate_frames[candidate_idx]
                remaining = len(candidate_frames) - candidate_idx - 1
            else:
                # No (more) scored alternatives -- just step forward in time.
                fno = min(VTOTAL - 1, args.frame + NEXT_STEP_FRAMES)
                remaining = None
            args.frame = fno
            bgr = _read_frame_no(fno)
            _, jpg = cv2.imencode('.jpg', bgr, [cv2.IMWRITE_JPEG_QUALITY, 92])
            resp = {'frame_no': fno, 'image': base64.b64encode(jpg.tobytes()).decode()}
            if remaining is not None:
                resp['remaining'] = remaining
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode())
            return

        elif self.path == '/save':
            _save(json.loads(body))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'ok')
            # shut down from a background thread (can't call from handler thread)
            threading.Thread(target=server_ref.shutdown, daemon=True).start()
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')

# ── save ───────────────────────────────────────────────────────────────────────
def _save(pts):
    TL, TR, BR, BL, NL, NR, CL, CR = pts
    data = {
        'frame_no':   args.frame,
        'frame_size': {'width': VW, 'height': VH},
        'corners': {'TL': TL, 'TR': TR, 'BR': BR, 'BL': BL},
        'net': {
            'net_Y':        (NL[1] + NR[1]) / 2,
            'net_top_Y':    (CL[1] + CR[1]) / 2,
            'left_bottom':  NL,
            'right_bottom': NR,
            'cable_left':   CL,
            'cable_right':  CR,
        },
        'source': 'manual',
    }
    with open(args.out, 'w') as f:
        json.dump(data, f, indent=2)
    print(f'\nSaved → {args.out}')
    for lbl, (x, y) in zip(LABELS, pts):
        print(f'  {lbl}: ({x}, {y})')

    preview = args.out.replace('.json', '_preview.jpg')
    img = bgr.copy()
    for i, (x, y) in enumerate(pts):
        h = COLORS[i].lstrip('#')
        col = (int(h[4:6],16), int(h[2:4],16), int(h[0:2],16))  # BGR
        cv2.circle(img, (int(x), int(y)), 8, col, -1)
        cv2.putText(img, LABELS[i], (int(x)+12, int(y)+6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, col, 2)
    cv2.imwrite(preview, img)
    print(f'Preview → {preview}')

# ── run ────────────────────────────────────────────────────────────────────────
try:
    server = ThreadingHTTPServer(('0.0.0.0', args.port), Handler)
except OSError as e:
    raise SystemExit(f'Cannot bind port {args.port}: {e}\nTry --port 5051 or kill the process using that port.')
server.daemon_threads = True  # a stalled request thread can't block Ctrl+C exit

server_ref = server
print(f'Server running — open this in your browser:')
print(f'\n    http://localhost:{args.port}\n')
print(f'Video : {args.video}  (frame {args.frame}, {VW}×{VH})')
print(f'Output: {args.out}')
print('Click 8 court points in the browser, then hit Save.')
if candidate_frames:
    print(f'Not the right frame? Click "Try Different Frame" -- '
         f'{len(candidate_frames) - 1} other scored candidate(s) available, '
         f'then falls back to stepping forward {args.search_step_sec}s at a time.')
else:
    print(f'Not the right frame? Click "Try Different Frame" to step forward '
         f'{args.search_step_sec}s at a time.')
print('Press Ctrl+C to quit without saving.\n')

server.serve_forever()
print('Done.')
