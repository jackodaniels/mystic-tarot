import json
import random
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Mystic Tarot", page_icon="🔮", layout="wide")

DATA = Path(__file__).parent / "data" / "tarot_cards.json"
DECK = json.loads(DATA.read_text(encoding="utf-8"))

CATEGORIES = {
    "💼 Career": "career",
    "❤️ Love": "love",
    "💰 Money": "money",
    "🌱 Personal Growth": "growth",
    "🔮 Future": "future",
}

SPREADS = {
    "1 Card": ["Guidance"],
    "3 Cards": ["Past / Foundation", "Present / Energy", "Future / Direction"],
    "5 Cards": ["Situation", "Challenge", "Hidden Influence", "Advice", "Direction"],
}

st.markdown("""
<style>
.stApp { background: radial-gradient(circle at top, #17102b 0%, #090711 52%, #05040a 100%); }
.block-container { max-width: 1200px; padding-top: 2rem; }
.hero { text-align:center; padding: 1rem 0 1.5rem; }
.hero h1 { font-size: 3rem; margin: 0; letter-spacing: .03em; }
.hero p { color:#aaa4bd; margin-top:.5rem; }
.section { color:#d7d0e6; font-weight:700; margin:1rem 0 .6rem; }
.card-box {
    border: 1px solid rgba(255,255,255,.13);
    border-radius: 18px;
    padding: 18px 12px;
    min-height: 225px;
    text-align:center;
    background: linear-gradient(145deg, rgba(33,24,56,.95), rgba(13,10,23,.95));
    box-shadow: 0 12px 35px rgba(0,0,0,.3);
}
.card-back { font-size: 4rem; margin: 18px 0 12px; }
.card-selected { border: 2px solid #b69cff; background: linear-gradient(145deg,#2b2050,#12101e); }
.card-revealed { border: 1px solid rgba(255,255,255,.18); min-height: 300px; }
.card-title { font-size:1.2rem; font-weight:800; margin:.4rem 0; }
.position { font-size:.82rem; color:#aaa4bd; text-transform:uppercase; letter-spacing:.08em; }
.orientation { font-size:.8rem; color:#c9b7ff; text-transform:uppercase; letter-spacing:.1em; }
.meaning { color:#c0bacd; font-size:.9rem; line-height:1.45; margin-top:.7rem; }
</style>
""", unsafe_allow_html=True)

def init():
    defaults = {
        "phase": "setup",
        "pool": [],
        "selected": [],
        "reading": [],
        "question": "",
        "category": "💼 Career",
        "spread": "3 Cards",
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def start_reading():
    question = st.session_state.question.strip()
    if not question:
        st.session_state.error = "Please enter a question before starting."
        return
    count = len(SPREADS[st.session_state.spread])
    st.session_state.pool = random.sample(range(len(DECK)), min(24, len(DECK)))
    st.session_state.selected = []
    st.session_state.reading = []
    st.session_state.phase = "select"
    st.session_state.error = ""

def select_card(card_index):
    if card_index in st.session_state.selected:
        st.session_state.selected.remove(card_index)
    elif len(st.session_state.selected) < len(SPREADS[st.session_state.spread]):
        st.session_state.selected.append(card_index)

def reveal():
    positions = SPREADS[st.session_state.spread]
    cards = []
    for pos, idx in zip(positions, st.session_state.selected):
        c = DECK[idx]
        orientation = random.choice(["Upright", "Reversed"])
        cards.append({
            "position": pos,
            "name": c["name"],
            "orientation": orientation,
            "meaning": c["upright"] if orientation == "Upright" else c["reversed"],
        })
    st.session_state.reading = cards
    st.session_state.phase = "reveal"

def new_reading():
    for k in ["pool","selected","reading"]:
        st.session_state[k] = []
    st.session_state.phase = "setup"
    st.session_state.error = ""

init()

st.markdown('<div class="hero"><h1>🔮 Mystic Tarot</h1><p>Choose your question. Pick your own cards. Reveal your reading.</p></div>', unsafe_allow_html=True)

if st.session_state.phase == "setup":
    st.markdown('<div class="section">1. Choose your reading</div>', unsafe_allow_html=True)
    st.session_state.category = st.selectbox("Reading category", list(CATEGORIES.keys()), label_visibility="collapsed")
    st.session_state.spread = st.selectbox("Spread", list(SPREADS.keys()), label_visibility="collapsed")
    st.session_state.question = st.text_area(
        "Question",
        value=st.session_state.question,
        placeholder="Example: What do I need to know about my career right now?",
        height=100,
    )
    if getattr(st.session_state, "error", ""):
        st.error(st.session_state.error)
    if st.button("✨ Start & Shuffle the Deck", type="primary", use_container_width=True):
        start_reading()
        st.rerun()

elif st.session_state.phase == "select":
    need = len(SPREADS[st.session_state.spread])
    st.markdown(f'<div class="section">2. Pick {need} card{"s" if need > 1 else ""}</div>', unsafe_allow_html=True)
    st.caption(f"Selected: {len(st.session_state.selected)} / {need} — Tap a face-down card to select or deselect it.")

    cols_per_row = 6
    pool = st.session_state.pool
    for row_start in range(0, len(pool), cols_per_row):
        row = pool[row_start:row_start+cols_per_row]
        cols = st.columns(len(row))
        for col, idx in zip(cols, row):
            with col:
                selected = idx in st.session_state.selected
                label = "✓ Selected" if selected else "🂠 Pick"
                st.markdown(f'<div class="card-box {"card-selected" if selected else ""}"><div class="card-back">✦</div><div>{"Card chosen" if selected else "Face down"}</div></div>', unsafe_allow_html=True)
                if st.button(label, key=f"pick_{idx}", use_container_width=True):
                    select_card(idx)
                    st.rerun()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("✨ Reveal My Cards", type="primary", disabled=len(st.session_state.selected) != need, use_container_width=True):
            reveal()
            st.rerun()
    with c2:
        if st.button("↻ Reshuffle", use_container_width=True):
            st.session_state.pool = random.sample(range(len(DECK)), min(24, len(DECK)))
            st.session_state.selected = []
            st.rerun()

elif st.session_state.phase == "reveal":
    st.markdown('<div class="section">3. Your cards</div>', unsafe_allow_html=True)
    st.write(f"**{st.session_state.category}** · {st.session_state.spread}")
    st.write(f"**Question:** {st.session_state.question}")

    cards = st.session_state.reading
    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        with col:
            st.markdown(f"""
            <div class="card-box card-revealed">
                <div class="position">{card["position"]}</div>
                <div style="font-size:2.7rem;margin:.6rem">✦</div>
                <div class="card-title">{card["name"]}</div>
                <div class="orientation">{card["orientation"]}</div>
                <div class="meaning">{card["meaning"]}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### 🔮 Reading")
    if st.session_state.category == "🔮 Future":
        intro = "This Future reading is best treated as a symbolic look at possible themes and preparation points—not a guaranteed prediction."
    else:
        intro = "Use these cards as symbolic prompts for reflection and decision-making."
    st.info(intro)

    for card in cards:
        st.markdown(f"**{card['position']} — {card['name']} ({card['orientation']})**")
        st.write(card["meaning"])

    st.divider()
    if st.button("🔄 Start a New Reading", type="primary", use_container_width=True):
        new_reading()
        st.rerun()

st.caption("🔮 Tarot is presented as a reflective/divination practice, not a guaranteed prediction.")
