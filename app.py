"""
TreeLab - Binary Tree Traversal Simulator  (DAA mini-project)

Run:
    pip install streamlit
    streamlit run app.py

What it demonstrates (not just static output):
  * the REAL recursive call sequence of Inorder / Preorder / Postorder
  * live call stack, highlighted pseudocode line, base cases (None checks)
  * visit order badges on nodes, output sequence, recursion-call counters
  * complexity analysis, comparison of all 3 traversals, practice quiz
"""

import inspect
import random
import re
import time

import streamlit as st

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="TreeLab - Tree Traversal Simulator",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# COMPATIBILITY HELPERS (work on old and new Streamlit versions)
# ============================================================

def stretch_kwargs(fn):
    """Return the right 'fill width' kwarg for this Streamlit version."""
    try:
        params = inspect.signature(fn).parameters
        if "width" in params:
            return {"width": "stretch"}
        if "use_container_width" in params:
            return {"use_container_width": True}
    except (TypeError, ValueError):
        pass
    return {}


BTN = stretch_kwargs(st.button)
GRAPH = stretch_kwargs(st.graphviz_chart)


def html(markup):
    """
    Render HTML safely. Markdown treats blank lines / indented lines inside
    HTML as code blocks, so we collapse the markup into one clean line.
    """
    st.markdown(re.sub(r"\n\s*", "", markup.strip()), unsafe_allow_html=True)


# ============================================================
# THEME  (light blue + lavender)
# ============================================================

st.markdown(
    """
<style>
.stApp { background: #F5F8FC; }
.main .block-container { max-width: 1400px; padding-top: 1.1rem; padding-bottom: 2rem; }
#MainMenu, footer { visibility: hidden; }

/* ---------- hero ---------- */
.hero {
    background: linear-gradient(120deg, #E3F2FF, #EFE8FF);
    border: 1px solid #D6E3F1; border-radius: 18px;
    padding: 20px 26px; margin-bottom: 14px;
    box-shadow: 0 4px 16px rgba(60,90,120,0.07);
}
.hero-title { font-size: 29px; font-weight: 800; color: #385978; }
.hero-subtitle { color: #6F8096; font-size: 13px; margin-top: 4px; }
.badge {
    display: inline-block; background: #fff; border: 1px solid #D9CFF3;
    color: #6C55A5; font-size: 10px; font-weight: 800; letter-spacing: .6px;
    text-transform: uppercase; padding: 3px 10px; border-radius: 20px; margin-right: 6px;
}

/* ---------- stat cards ---------- */
.stat {
    background: white; border: 1px solid #DDE6EF; border-radius: 13px;
    padding: 11px 15px; box-shadow: 0 3px 10px rgba(70,100,130,0.05);
}
.stat-label { color: #8793A2; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; }
.stat-value { color: #4B7196; font-size: 21px; font-weight: 800; margin-top: 2px; }

/* ---------- cards / titles ---------- */
.card-title { color: #50647B; font-size: 15px; font-weight: 800; margin: 6px 0 8px 0; }
.legend { display: flex; flex-wrap: wrap; gap: 14px; margin-bottom: 4px; font-size: 11px; color: #70829A; }
.dot { display: inline-block; width: 11px; height: 11px; border-radius: 50%; margin-right: 5px; vertical-align: -1px; border: 2px solid; }

/* ---------- operation box ---------- */
.operation {
    background: #EEF7FF; border: 1px solid #D8E9F7; border-left: 5px solid #8E73D8;
    border-radius: 11px; padding: 12px 15px; color: #4F647B; font-size: 13.5px; margin-top: 6px;
}
.op-kind {
    display: inline-block; background: #E5DAFF; color: #5B3FB0; font-weight: 800; font-size: 10px;
    letter-spacing: .6px; text-transform: uppercase; padding: 2px 9px; border-radius: 12px; margin-right: 8px;
}

/* ---------- output sequence ---------- */
.sequence {
    background: #F7F4FF; border: 1px solid #E3DAF3; border-radius: 12px;
    padding: 10px; min-height: 48px; line-height: 2.5;
}
.seq {
    display: inline-flex; align-items: center; justify-content: center;
    min-width: 36px; height: 34px; padding: 0 4px; margin: 2px; border-radius: 9px;
    background: #E3F1FF; border: 1px solid #B5D2EA; color: #3F6688; font-size: 13px; font-weight: 800;
}
.seq-current { background: #8E73D8; border-color: #5B3FB0; color: white; box-shadow: 0 0 0 3px #E5DAFF; }
.seq-ghost { background: transparent; border: 1px dashed #C9D3DF; color: #B2BDCA; }
.seq-arrow { color: #A5B0BE; margin: 0 1px; }

/* ---------- pseudocode ---------- */
.code {
    background: #FCFBFF; border: 1px solid #E3DAF3; border-radius: 12px; padding: 8px 0;
    font-family: 'JetBrains Mono', Menlo, Consolas, monospace; font-size: 12.5px;
}
.cl { padding-top: 4px; padding-bottom: 4px; padding-right: 10px; color: #55677D; border-left: 4px solid transparent; }
.cl-on { background: #E9E0FF; border-left-color: #8E73D8; color: #3F2D75; font-weight: 700; }
.ln { color: #A9B4C2; display: inline-block; width: 22px; font-size: 11px; }

/* ---------- call stack ---------- */
.stack-box {
    background: #F4F9FF; border: 1px solid #D8E6F3; border-radius: 12px;
    padding: 9px; min-height: 54px;
}
.frame {
    display: flex; justify-content: space-between; align-items: center;
    background: #DDEEFF; border: 1px solid #A9CBE6; color: #3F678B;
    border-radius: 8px; padding: 6px 11px; margin-bottom: 5px;
    font-family: Menlo, Consolas, monospace; font-size: 12px; font-weight: 700;
}
.frame-top { background: #E5DAFF; border-color: #8E73D8; color: #4F368F; }
.frame-tag { font-size: 9px; letter-spacing: .6px; }
.stack-empty { color: #9AA6B5; font-size: 12px; text-align: center; padding: 8px; }

/* ---------- info grid ---------- */
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.info-box { background: white; border: 1px solid #DEE7F0; border-radius: 11px; padding: 9px 12px; }
.info-label { color: #8793A3; font-size: 9.5px; text-transform: uppercase; font-weight: 700; letter-spacing: .5px; }
.info-value { color: #4B6580; font-size: 13px; font-weight: 800; margin-top: 2px; }

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #EDF7FF 0%, #F4F0FF 100%);
    border-right: 1px solid #D8E3EF;
}
.sidebar-brand {
    background: rgba(255,255,255,.65); border: 1px solid #DDE6EF;
    border-radius: 14px; padding: 13px; margin-bottom: 14px;
}
.sidebar-brand-title { color: #405A77; font-size: 17px; font-weight: 800; }
.sidebar-brand-text { color: #8490A0; font-size: 11px; margin-top: 3px; }
.sidebar-section {
    color: #69788B; font-size: 10px; font-weight: 800; text-transform: uppercase;
    letter-spacing: .8px; margin-top: 14px; margin-bottom: 5px;
}

/* ---------- buttons ---------- */
div.stButton > button {
    border-radius: 10px !important; border: 1px solid #CCDCEB !important;
    background: white !important; color: #506B84 !important;
    font-weight: 700 !important; min-height: 38px !important; transition: all .15s ease;
}
div.stButton > button:hover:not(:disabled) {
    background: #F1ECFF !important; border-color: #9F86D8 !important; transform: translateY(-1px);
}
div.stButton > button:disabled { opacity: .45; }

/* ---------- progress ---------- */
div[data-testid="stProgress"] > div { background: #E4EAF1; }
div[data-testid="stProgress"] > div > div { background: linear-gradient(90deg, #7FB7DF, #A389D0); }
.step-text { text-align: center; color: #8792A1; font-size: 11px; margin-top: 2px; }

/* ---------- tabs ---------- */
button[data-baseweb="tab"] { font-weight: 700; }
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# TREE DATA STRUCTURE
# ============================================================

def make_node(value):
    return {"id": None, "value": value, "left": None, "right": None}


def assign_ids(root):
    """Give every node a unique id (breadth-first) - so duplicate values never confuse the UI."""
    queue, i = [root], 0
    while queue:
        node = queue.pop(0)
        node["id"] = i
        i += 1
        for child in (node["left"], node["right"]):
            if child:
                queue.append(child)
    return root


def build_balanced(sorted_vals):
    if not sorted_vals:
        return None
    mid = len(sorted_vals) // 2
    node = make_node(sorted_vals[mid])
    node["left"] = build_balanced(sorted_vals[:mid])
    node["right"] = build_balanced(sorted_vals[mid + 1:])
    return node


def bst_from(values):
    root = None
    for v in values:
        new = make_node(v)
        if root is None:
            root = new
            continue
        cur = root
        while True:
            side = "left" if v < cur["value"] else "right"
            if cur[side] is None:
                cur[side] = new
                break
            cur = cur[side]
    return root


def all_nodes(node):
    if node is None:
        return []
    return [node] + all_nodes(node["left"]) + all_nodes(node["right"])


def tree_height(node):
    return 0 if node is None else 1 + max(tree_height(node["left"]), tree_height(node["right"]))


def default_tree():
    return assign_ids(build_balanced([20, 30, 40, 50, 60, 70, 80]))


# ============================================================
# TRAVERSAL ALGORITHMS + STEP-BY-STEP TRACE
# ============================================================

METHODS = ["Inorder", "Preorder", "Postorder"]
ORDERS = {"Preorder": "VLR", "Inorder": "LVR", "Postorder": "LRV"}
RULES = {
    "Preorder": "Root → Left → Right",
    "Inorder": "Left → Root → Right",
    "Postorder": "Left → Right → Root",
}
USES = {
    "Preorder": "Copying / serialising a tree, prefix expressions.",
    "Inorder": "Gives sorted order in a BST, range queries.",
    "Postorder": "Deleting a tree, evaluating postfix expressions.",
}


def sequence_of(node, method):
    """Plain recursive traversal -> list of node ids."""
    if node is None:
        return []
    left = sequence_of(node["left"], method)
    right = sequence_of(node["right"], method)
    me = [node["id"]]
    return {"Preorder": me + left + right,
            "Inorder": left + me + right,
            "Postorder": left + right + me}[method]


def make_pseudo(method):
    name = method.lower()
    lines = [(0, f"def {name}(node):"), (1, "if node is None: return   # base case")]
    text = {"L": f"{name}(node.left)", "V": "visit(node)   # output value", "R": f"{name}(node.right)"}
    for ch in ORDERS[method]:
        lines.append((1, text[ch]))
    lines.append((1, "return   # pop stack frame"))
    return lines


def build_trace(root, method):
    """
    Run the real recursion and record EVERY step:
    call, go_left/go_right, base case (None), visit, return.
    Each step stores the call stack and visited list at that moment.
    """
    order = ORDERS[method]
    name = method.lower()
    line_of = {ch: 2 + k for k, ch in enumerate(order)}   # pseudocode line for L / V / R
    LINE_BASE, LINE_RET = 1, 5
    id_val = {n["id"]: n["value"] for n in all_nodes(root)}

    steps, stack, visited = [], [], []
    counters = {"calls": 0, "maxd": 0}

    def add(kind, node_id, line, text):
        steps.append({
            "kind": kind, "node": node_id, "line": line, "text": text,
            "stack": list(stack), "visited": list(visited),
            "calls": counters["calls"], "maxd": counters["maxd"],
        })

    add("start", None, -1,
        f"Ready. {method} visits nodes in <b>{RULES[method]}</b> order. "
        "Press <b>▶ Play</b> or <b>Next</b> to watch the recursion unfold.")

    def rec(node):
        nid, v = node["id"], node["value"]
        stack.append(nid)
        counters["calls"] += 1
        counters["maxd"] = max(counters["maxd"], len(stack))
        add("call", nid, 0, f"Call <b>{name}({v})</b>: a new frame is pushed on the call stack (depth {len(stack)}).")

        for ch in order:
            if ch == "V":
                visited.append(nid)
                add("visit", nid, line_of["V"], f"<b>Visit {v}</b>: its value is appended to the output sequence.")
                continue
            side = "left" if ch == "L" else "right"
            child = node[side]
            if child is None:
                counters["calls"] += 1
                add("null", nid, LINE_BASE,
                    f"The {side} child of {v} is <b>None</b>: <b>{name}(None)</b> hits the base case and returns at once.")
            else:
                add("go_" + side, nid, line_of[ch],
                    f"Recurse into the <b>{side}</b> child: call {name}({child['value']}).")
                rec(child)

        add("return", nid, LINE_RET, f"Node {v} is finished: its frame is <b>popped</b> and control returns to the caller.")
        stack.pop()

    rec(root)
    result = " → ".join(str(id_val[i]) for i in visited)
    add("done", None, -1, f"🎉 <b>{method} traversal complete!</b> Output: {result}")
    return steps


DETAILS = {
    "Full recursion trace": {"start", "call", "go_left", "go_right", "null", "visit", "return", "done"},
    "Calls & visits": {"start", "call", "visit", "done"},
    "Visits only": {"start", "visit", "done"},
}
SPEEDS = {"Slow": 1.1, "Normal": 0.6, "Fast": 0.25, "Turbo": 0.1}

KIND_META = {
    "start": ("🌱", "Ready"), "call": ("📥", "Call"), "go_left": ("⬅️", "Go left"),
    "go_right": ("➡️", "Go right"), "visit": ("✅", "Visit"), "null": ("⛔", "Base case"),
    "return": ("↩️", "Return"), "done": ("🎉", "Done"),
}


# ============================================================
# GRAPHVIZ (DOT) TREE DRAWING
# ============================================================

def build_dot(root, stack, visited, cur):
    stack_set = set(stack)
    order = {nid: k + 1 for k, nid in enumerate(visited)}
    out = [
        "digraph T {",
        'graph [rankdir=TB, bgcolor="transparent", nodesep=0.45, ranksep=0.6, pad=0.2, ordering=out];',
        'node [shape=circle, fixedsize=true, width=0.64, height=0.64, style=filled, '
        'fontname="Helvetica", fontsize=14, penwidth=2];',
        'edge [color="#C3D2E1", penwidth=1.8, arrowsize=0.7];',
    ]
    nodes = all_nodes(root)

    for n in nodes:
        nid, v = n["id"], n["value"]
        if nid == cur:
            attrs = 'fillcolor="#8E73D8", color="#5B3FB0", fontcolor="white", penwidth=3.5'
        elif nid in stack_set:
            attrs = 'fillcolor="#EDE5FF", color="#A68CE0", fontcolor="#5D479A", style="filled,dashed", penwidth=2.5'
        elif nid in order:
            attrs = 'fillcolor="#A9D3F5", color="#5B9BD0", fontcolor="#1B4A75"'
        else:
            attrs = 'fillcolor="#F0F6FC", color="#B7CCE0", fontcolor="#5F7A94"'
        if nid in order:
            label = f'<<B>{v}</B><BR/><FONT POINT-SIZE="9">#{order[nid]}</FONT>>'
        else:
            label = f'"{v}"'
        out.append(f"n{nid} [label={label}, {attrs}];")

    for n in nodes:
        kids = [("L", n["left"]), ("R", n["right"])]
        real = [c for _, c in kids if c]
        for side, child in kids:
            if child:
                on_path = n["id"] in stack_set and child["id"] in stack_set
                style = ' [color="#8E73D8", penwidth=3]' if on_path else ""
                out.append(f'n{n["id"]} -> n{child["id"]}{style};')
            elif len(real) == 1:
                # invisible placeholder keeps left/right orientation correct
                ghost = f'g{n["id"]}{side}'
                out.append(f'{ghost} [style=invis, label="", width=0.05, height=0.05];')
                out.append(f'n{n["id"]} -> {ghost} [style=invis];')
    out.append("}")
    return "\n".join(out)


# ============================================================
# HTML BUILDERS
# ============================================================

def pseudo_html(method, active):
    parts = ['<div class="code">']
    for idx, (indent, text) in enumerate(make_pseudo(method)):
        cls = "cl cl-on" if idx == active else "cl"
        parts.append(
            f'<div class="{cls}" style="padding-left:{8 + indent * 20}px">'
            f'<span class="ln">{idx + 1}</span>{text}</div>'
        )
    parts.append("</div>")
    return "".join(parts)


def stack_html(stack, id_val, method):
    if not stack:
        return '<div class="stack-box"><div class="stack-empty">call stack is empty</div></div>'
    name = method.lower()
    frames = []
    for pos in range(len(stack) - 1, -1, -1):
        top = pos == len(stack) - 1
        cls = "frame frame-top" if top else "frame"
        tag = "TOP" if top else ""
        frames.append(f'<div class="{cls}"><span>{name}({id_val[stack[pos]]})</span><span class="frame-tag">{tag}</span></div>')
    return '<div class="stack-box">' + "".join(frames) + "</div>"


def ribbon_html(visited, current_is_visit, total, id_val):
    parts = ['<div class="sequence">']
    for k, nid in enumerate(visited):
        if k:
            parts.append('<span class="seq-arrow">→</span>')
        cls = "seq seq-current" if (k == len(visited) - 1 and current_is_visit) else "seq"
        parts.append(f'<span class="{cls}">{id_val[nid]}</span>')
    for _ in range(total - len(visited)):
        if len(parts) > 1:
            parts.append('<span class="seq-arrow">→</span>')
        parts.append('<span class="seq seq-ghost">?</span>')
    parts.append("</div>")
    return "".join(parts)


def stat_html(label, value, small=False):
    size = ' style="font-size:17px;"' if small else ""
    return f'<div class="stat"><div class="stat-label">{label}</div><div class="stat-value"{size}>{value}</div></div>'


def info_html(label, value):
    return f'<div class="info-box"><div class="info-label">{label}</div><div class="info-value">{value}</div></div>'


LEGEND = (
    '<div class="legend">'
    '<span><span class="dot" style="background:#F0F6FC;border-color:#B7CCE0"></span>Not visited</span>'
    '<span><span class="dot" style="background:#EDE5FF;border-color:#A68CE0;border-style:dashed"></span>On call stack</span>'
    '<span><span class="dot" style="background:#A9D3F5;border-color:#5B9BD0"></span>Visited (#order)</span>'
    '<span><span class="dot" style="background:#8E73D8;border-color:#5B3FB0"></span>Current node</span>'
    "</div>"
)


# ============================================================
# SESSION STATE + CALLBACKS
# ============================================================

SRC_P7 = "Perfect tree · 7 nodes (3 levels)"
SRC_P15 = "Perfect tree · 15 nodes (4 levels)"
SRC_RB = "Random balanced tree"
SRC_RT = "Random BST (any shape)"
SRC_CU = "Custom values"
SOURCES = [SRC_P7, SRC_P15, SRC_RB, SRC_RT, SRC_CU]

for key, default in {
    "tree": None, "tree_ver": 0, "tree_msg": None,
    "step": 0, "playing": False, "sig": None, "n_steps": 1, "finished": False,
    "quiz_method": random.choice(METHODS), "quiz_ok": 0, "quiz_try": 0, "quiz_msg": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default
if st.session_state.tree is None:
    st.session_state.tree = default_tree()


def build_tree_cb():
    ss = st.session_state
    src = ss.get("src", SRC_P7)
    root, msg = None, None
    if src == SRC_P7:
        root = build_balanced([20, 30, 40, 50, 60, 70, 80])
    elif src == SRC_P15:
        root = build_balanced(list(range(10, 160, 10)))
    elif src == SRC_RB:
        n = ss.get("rand_n", 9)
        root = build_balanced(sorted(random.sample(range(5, 100), n)))
    elif src == SRC_RT:
        n = ss.get("rand_n", 9)
        root = bst_from(random.sample(range(5, 100), n))
    else:
        text = ss.get("custom_txt", "50, 30, 70, 20, 40, 60, 80")
        vals, bad = [], False
        for tok in re.split(r"[,\s]+", text.strip()):
            if not tok:
                continue
            try:
                v = int(tok)
            except ValueError:
                bad = True
                break
            if v not in vals:
                vals.append(v)
        if bad:
            ss.tree_msg = ("error", "Please enter whole numbers separated by commas.")
        elif not 3 <= len(vals) <= 15:
            ss.tree_msg = ("error", "Enter between 3 and 15 distinct numbers.")
        else:
            root = bst_from(vals)
            msg = ("success", f"Built a BST from {len(vals)} values (inserted in the order given).")
    if root is None:
        return  # keep the old tree if input was invalid
    ss.tree = assign_ids(root)
    ss.tree_ver += 1
    ss.tree_msg = msg
    ss.quiz_msg = None


def cb_prev():
    st.session_state.playing = False
    st.session_state.step = max(0, st.session_state.step - 1)


def cb_next():
    st.session_state.playing = False
    st.session_state.step = min(st.session_state.n_steps - 1, st.session_state.step + 1)


def cb_play():
    if st.session_state.playing:
        st.session_state.playing = False
    else:
        if st.session_state.step >= st.session_state.n_steps - 1:
            st.session_state.step = 0
        st.session_state.playing = True


def cb_restart():
    st.session_state.playing = False
    st.session_state.step = 0


def cb_end():
    st.session_state.playing = False
    st.session_state.step = st.session_state.n_steps - 1


def cb_scrub():
    st.session_state.playing = False
    st.session_state.step = st.session_state.scrub


def parse_ints(text):
    toks = [t for t in re.split(r"[,\s→>\-]+", text.strip()) if t]
    if not toks or not all(t.isdigit() for t in toks):
        return None
    return [int(t) for t in toks]


def quiz_answer():
    root = st.session_state.tree
    id_val = {n["id"]: n["value"] for n in all_nodes(root)}
    return [id_val[i] for i in sequence_of(root, st.session_state.quiz_method)]


def cb_quiz_check():
    ss = st.session_state
    mine = parse_ints(ss.get("quiz_ans", ""))
    if mine is None:
        ss.quiz_msg = ("warning", "Type the node values separated by commas, e.g. 20, 30, 40")
        return
    right = quiz_answer()
    ss.quiz_try += 1
    if mine == right:
        ss.quiz_ok += 1
        ss.quiz_msg = ("success", "🎉 Correct! Perfect traversal.")
    else:
        wrong_at = next((k for k in range(min(len(mine), len(right))) if mine[k] != right[k]), min(len(mine), len(right)))
        ss.quiz_msg = ("error", f"Not quite: your first wrong value is at position {wrong_at + 1}. "
                                f"Try tracing {RULES[ss.quiz_method]} again, or press Hint.")


def cb_quiz_hint():
    m = st.session_state.quiz_method
    st.session_state.quiz_msg = ("info", f"💡 {m} rule: **{RULES[m]}**. Always finish the whole left subtree before going right.")


def cb_quiz_reveal():
    st.session_state.quiz_msg = ("info", "Answer: " + " → ".join(map(str, quiz_answer())))


def cb_quiz_new():
    ss = st.session_state
    ss.quiz_method = random.choice([m for m in METHODS if m != ss.quiz_method])
    ss.quiz_ans = ""
    ss.quiz_msg = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    html("""
    <div class="sidebar-brand">
      <div style="font-size:22px;"></div>
      <div class="sidebar-brand-title">TreeLab</div>
      <div class="sidebar-brand-text">Binary Tree Traversal Simulator</div>
    </div>
    """)

    html('<div class="sidebar-section">Tree</div>')
    st.selectbox("Tree source", SOURCES, key="src", on_change=build_tree_cb, label_visibility="collapsed")
    src = st.session_state.src
    if src in (SRC_RB, SRC_RT):
        st.slider("Number of nodes", 3, 15, 9, key="rand_n", on_change=build_tree_cb)
        st.button("🎲  New random tree", on_click=build_tree_cb, **BTN)
    elif src == SRC_CU:
        st.text_input("Values (3–15 numbers, comma separated)", "50, 30, 70, 20, 40, 60, 80",
                      key="custom_txt", on_change=build_tree_cb)
        st.button("🔨  Build tree", on_click=build_tree_cb, **BTN)
    if st.session_state.tree_msg:
        kind, text = st.session_state.tree_msg
        (st.success if kind == "success" else st.error)(text)

    html('<div class="sidebar-section">Traversal Algorithm</div>')
    st.selectbox("Traversal", METHODS, key="method", label_visibility="collapsed")

    html('<div class="sidebar-section">Detail Level</div>')
    st.selectbox("Detail", list(DETAILS), key="detail", label_visibility="collapsed")

    html('<div class="sidebar-section">Animation Speed</div>')
    st.select_slider("Speed", list(SPEEDS), value="Normal", key="speed", label_visibility="collapsed")

    html('<div class="sidebar-section">Traversal Rules</div>')
    st.info(
        "**Preorder**  \nRoot → Left → Right\n\n"
        "**Inorder**  \nLeft → Root → Right\n\n"
        "**Postorder**  \nLeft → Right → Root"
    )


# ============================================================
# COMPUTE TRACE FOR CURRENT SETTINGS
# ============================================================

TREE = st.session_state.tree
METHOD = st.session_state.method
NODES = all_nodes(TREE)
N_NODES = len(NODES)
HEIGHT = tree_height(TREE)
ID_VAL = {n["id"]: n["value"] for n in NODES}

FULL_TRACE = build_trace(TREE, METHOD)
keep = DETAILS[st.session_state.detail]
TRACE = [s for s in FULL_TRACE if s["kind"] in keep]
N = len(TRACE)
st.session_state.n_steps = N

signature = (st.session_state.tree_ver, METHOD, st.session_state.detail)
if st.session_state.sig != signature:           # tree / algorithm changed -> start over
    st.session_state.sig = signature
    st.session_state.step = 0
    st.session_state.playing = False
st.session_state.step = max(0, min(st.session_state.step, N - 1))

if st.session_state.finished:
    st.session_state.finished = False
    st.toast(f"{METHOD} traversal completed!", icon="🎉")


# ============================================================
# FRAME RENDERER (used for static view AND live animation)
# ============================================================

def render_frame(i):
    s = TRACE[i]
    cur = s["node"]
    icon, label = KIND_META[s["kind"]]

    # ---- stats ----
    cols = st.columns(5)
    stats = [
        ("Nodes", N_NODES, False),
        ("Levels", HEIGHT, False),
        ("Visited", f"{len(s['visited'])} / {N_NODES}", False),
        ("Current", ID_VAL[cur] if cur is not None else "—", False),
        ("Stack depth", f"{len(s['stack'])} / {HEIGHT}", False),
    ]
    for col, (lab, val, small) in zip(cols, stats):
        with col:
            html(stat_html(lab, val, small))
    st.write("")

    tree_col, side_col = st.columns([1.9, 1.15], gap="large")

    with tree_col:
        html('<div class="card-title">🌿 Binary Tree</div>')
        html(LEGEND)
        st.graphviz_chart(build_dot(TREE, s["stack"], s["visited"], cur), **GRAPH)
        html(f'<div class="operation"><span class="op-kind">{icon} {label}</span>{s["text"]}</div>')
        st.write("")
        html(f'<div class="card-title">🔢 Output Sequence &nbsp;<span style="font-weight:600;color:#8A97A8;font-size:12px;">({METHOD}: {RULES[METHOD]})</span></div>')
        html(ribbon_html(s["visited"], s["kind"] == "visit", N_NODES, ID_VAL))

    with side_col:
        html('<div class="card-title">🧾 Pseudocode</div>')
        html(pseudo_html(METHOD, s["line"]))
        st.write("")
        html('<div class="card-title">📚 Recursion Call Stack</div>')
        html(stack_html(s["stack"], ID_VAL, METHOD))
        st.write("")
        html('<div class="card-title">📊 Analysis</div>')
        html(
            '<div class="info-grid">'
            + info_html("Time", "O(n)")
            + info_html("Space", "O(h)")
            + info_html("Calls so far", f"{s['calls']} / {2 * N_NODES + 1}")
            + info_html("Max depth", f"{s['maxd']} (h = {HEIGHT})")
            + "</div>"
        )

    st.progress(i / max(1, N - 1))
    html(f'<div class="step-text">Step {i} of {N - 1}</div>')


# ============================================================
# HEADER
# ============================================================

html("""
<div class="hero">
  <div><span class="badge">DAA</span><span class="badge">Recursion</span><span class="badge">Divide &amp; Conquer</span></div>
  <div class="hero-title" style="margin-top:8px;"> Tree Traversal Simulator</div>
  <div class="hero-subtitle">Watch Inorder, Preorder and Postorder run step by step: recursive calls, call stack, base cases and output.</div>
</div>
""")

tab_sim, tab_cmp, tab_quiz, tab_theory = st.tabs(
    ["Simulator", "Compare All", "Practice", "Theory"]
)


# ============================================================
# TAB 1 - SIMULATOR
# ============================================================

with tab_sim:
    step = st.session_state.step
    playing = st.session_state.playing

    b1, b2, b3, b4, b5 = st.columns([1, 1, 1.3, 1, 1])
    with b1:
        st.button("⏮ Previous", on_click=cb_prev, disabled=step == 0, **BTN)
    with b2:
        st.button("Next ⏭", on_click=cb_next, disabled=step >= N - 1, **BTN)
    with b3:
        st.button("⏸  Pause" if playing else "▶  Play", on_click=cb_play, **BTN)
    with b4:
        st.button("↶ Restart", on_click=cb_restart, disabled=step == 0, **BTN)
    with b5:
        st.button("End ⏭", on_click=cb_end, disabled=step >= N - 1, **BTN)

    if playing:
        st.caption("▶ Playing… press Pause to take manual control.")
    else:
        st.session_state.scrub = step
        st.slider("Step scrubber (drag to jump to any step)", 0, N - 1, key="scrub", on_change=cb_scrub)

    frame_slot = st.empty()
    with frame_slot.container():
        render_frame(step)


# ============================================================
# TAB 2 - COMPARE ALL
# ============================================================

with tab_cmp:
    html('<div class="card-title"> Current tree</div>')
    st.graphviz_chart(build_dot(TREE, [], [], None), **GRAPH)

    cc = st.columns(3, gap="large")
    seqs = {m: sequence_of(TREE, m) for m in METHODS}
    for col, m in zip(cc, ["Preorder", "Inorder", "Postorder"]):
        with col:
            chips = '<span class="seq-arrow">→</span>'.join(f'<span class="seq">{ID_VAL[i]}</span>' for i in seqs[m])
            html(f'<div class="card-title">{m}</div>'
                 f'<div class="info-box"><div class="info-label">Rule</div><div class="info-value">{RULES[m]}</div></div>'
                 f'<div style="height:8px"></div><div class="sequence">{chips}</div>'
                 f'<div style="color:#7B8CA1;font-size:12px;margin-top:6px;">Used for: {USES[m]}</div>')

    st.write("")
    html('<div class="card-title">📍 Visit position of every node</div>')
    pos = {m: {nid: k + 1 for k, nid in enumerate(seqs[m])} for m in METHODS}
    rows = [{"Node": n["value"], "Preorder #": pos["Preorder"][n["id"]],
             "Inorder #": pos["Inorder"][n["id"]], "Postorder #": pos["Postorder"][n["id"]]} for n in NODES]
    rows.sort(key=lambda r: r["Inorder #"])
    st.dataframe(rows, hide_index=True, **GRAPH)

    inorder_vals = [ID_VAL[i] for i in seqs["Inorder"]]
    if inorder_vals == sorted(inorder_vals):
        st.success("✅ Inorder output is sorted ascending: that is the defining property of a Binary Search Tree.")


# ============================================================
# TAB 3 - PRACTICE QUIZ
# ============================================================

with tab_quiz:
    qm = st.session_state.quiz_method
    q1, q2 = st.columns([1.6, 1], gap="large")
    with q1:
        html(f'<div class="card-title">What is the <span style="color:#7A5FC9;">{qm}</span> sequence of this tree?</div>')
        st.graphviz_chart(build_dot(TREE, [], [], None), **GRAPH)
    with q2:
        st.metric("Score", f"{st.session_state.quiz_ok} / {st.session_state.quiz_try}")
        st.text_input("Your answer (comma separated)", key="quiz_ans", placeholder="e.g. 20, 30, 40, 50 ...")
        a, b = st.columns(2)
        with a:
            st.button("✅ Check", on_click=cb_quiz_check, key="q_check", **BTN)
            st.button("👁 Reveal", on_click=cb_quiz_reveal, key="q_reveal", **BTN)
        with b:
            st.button("💡 Hint", on_click=cb_quiz_hint, key="q_hint", **BTN)
            st.button("🔄 New question", on_click=cb_quiz_new, key="q_new", **BTN)
        if st.session_state.quiz_msg:
            kind, text = st.session_state.quiz_msg
            {"success": st.success, "error": st.error, "warning": st.warning, "info": st.info}[kind](text)


# ============================================================
# TAB 4 - THEORY
# ============================================================

with tab_theory:
    t1, t2 = st.columns(2, gap="large")
    with t1:
        st.markdown("### What is tree traversal?")
        st.markdown(
            "Visiting every node of a tree **exactly once** in a systematic order. "
            "The three depth-first traversals differ only in **when the root is visited** "
            "relative to its two subtrees, and each is naturally a *divide-and-conquer* recursion: "
            "solve the left subtree, solve the right subtree, combine with the root."
        )
        st.markdown(
            "| Traversal | Order | Typical use |\n|---|---|---|\n"
            "| Preorder | Root, Left, Right | copy / serialise a tree |\n"
            "| Inorder | Left, Root, Right | sorted output of a BST |\n"
            "| Postorder | Left, Right, Root | delete tree, postfix evaluation |"
        )
        st.markdown("### Recursion & the call stack")
        st.markdown(
            "Every call `traverse(node)` pushes a frame; it is popped when the call returns. "
            "The deepest the stack ever gets equals the **height h** of the tree, "
            "which is why the space cost is O(h)."
        )
    with t2:
        st.markdown("### Time complexity")
        st.latex(r"T(n) = T(k) + T(n-k-1) + O(1) \;\Rightarrow\; T(n) = O(n)")
        st.markdown(
            f"Every node is visited once, and there are exactly **2n + 1** calls "
            f"(n real nodes + n + 1 `None` base cases). "
            f"For the current tree: n = {N_NODES}, so **{2 * N_NODES + 1} calls**."
        )
        st.markdown("### Space complexity")
        st.markdown(
            "| Tree shape | Height h | Stack space |\n|---|---|---|\n"
            "| Balanced | log n | O(log n) |\n"
            "| Skewed (like a linked list) | n | O(n) |"
        )
        st.markdown("### Try it")
        st.markdown(
            "Build a **Random BST**, or enter values like `10, 20, 30, 40` in *Custom values* to see a "
            "skewed tree and watch the call stack grow to depth n."
        )


# ============================================================
# LIVE AUTOPLAY  (runs last so every tab is already drawn)
# ============================================================

if st.session_state.playing:
    delay = SPEEDS[st.session_state.speed]
    for k in range(st.session_state.step + 1, N):
        time.sleep(delay)
        st.session_state.step = k
        with frame_slot.container():
            render_frame(k)
    st.session_state.playing = False
    st.session_state.finished = True
    st.rerun()