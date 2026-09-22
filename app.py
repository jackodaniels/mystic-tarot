import json
import random
from pathlib import Path

import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Berlin Tarot Reading",
    page_icon="🔮",
    layout="wide",
)


# ============================================================
# LOAD TAROT DECK
# ============================================================

DATA = Path(__file__).parent / "data" / "tarot_cards.json"

DECK = json.loads(
    DATA.read_text(encoding="utf-8")
)


# ============================================================
# READING CATEGORIES
# ============================================================

CATEGORIES = {
    "💼 Career": "career",
    "❤️ Love": "love",
    "💰 Money": "money",
    "🌱 Personal Growth": "growth",
    "🔮 Future": "future",
}


# ============================================================
# TAROT SPREADS
# ============================================================

SPREADS = {
    "1 Card": [
        "Guidance"
    ],

    "3 Cards": [
        "Past / Foundation",
        "Present / Energy",
        "Future / Direction",
    ],

    "5 Cards": [
        "Situation",
        "Challenge",
        "Hidden Influence",
        "Advice",
        "Direction",
    ],
}


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at top,
                #17102b 0%,
                #090711 52%,
                #05040a 100%
            );
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        text-align: center;
        padding: 1rem 0 1.5rem;
    }

    .hero h1 {
        font-size: 3rem;
        margin: 0;
        letter-spacing: .03em;
    }

    .hero p {
        color: #aaa4bd;
        margin-top: .5rem;
        font-size: 1.05rem;
    }

    .section {
        color: #d7d0e6;
        font-weight: 700;
        margin: 1rem 0 .6rem;
        font-size: 1.15rem;
    }

    .card-box {
        border: 1px solid rgba(255,255,255,.13);
        border-radius: 18px;
        padding: 18px 12px;
        min-height: 225px;
        text-align: center;

        background:
            linear-gradient(
                145deg,
                rgba(33,24,56,.95),
                rgba(13,10,23,.95)
            );

        box-shadow:
            0 12px 35px rgba(0,0,0,.3);

        transition:
            transform .2s ease,
            border-color .2s ease;
    }

    .card-box:hover {
        transform: translateY(-3px);
        border-color: rgba(182,156,255,.5);
    }

    .card-back {
        font-size: 4rem;
        margin: 18px 0 12px;
    }

    .card-selected {
        border: 2px solid #b69cff;

        background:
            linear-gradient(
                145deg,
                #2b2050,
                #12101e
            );
    }

    .card-revealed {
        border: 1px solid rgba(255,255,255,.18);
        min-height: 300px;
    }

    .card-title {
        font-size: 1.2rem;
        font-weight: 800;
        margin: .4rem 0;
    }

    .position {
        font-size: .82rem;
        color: #aaa4bd;
        text-transform: uppercase;
        letter-spacing: .08em;
    }

    .orientation {
        font-size: .8rem;
        color: #c9b7ff;
        text-transform: uppercase;
        letter-spacing: .1em;
    }

    .meaning {
        color: #c0bacd;
        font-size: .9rem;
        line-height: 1.45;
        margin-top: .7rem;
    }

    .instruction-box {
        border: 1px solid rgba(182,156,255,.25);
        border-radius: 16px;
        padding: 20px;
        background: rgba(30,22,52,.55);
        margin-top: 1rem;
    }

    .instruction-box h3 {
        margin-top: 0;
    }

    .chatgpt-prompt {
        border-left: 3px solid #b69cff;
        padding-left: 14px;
        color: #cfc8dc;
        font-style: italic;
    }

    .footer {
        text-align: center;
        color: #777185;
        margin-top: 2rem;
        font-size: .85rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

def init():

    defaults = {
        "phase": "setup",
        "pool": [],
        "selected": [],
        "reading": [],
        "question": "",
        "category": "💼 Career",
        "spread": "3 Cards",
        "error": "",
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================
# START READING
# ============================================================

def start_reading():

    question = st.session_state.question.strip()

    if not question:

        st.session_state.error = (
            "Please enter a question before starting."
        )

        return

    st.session_state.pool = random.sample(
        range(len(DECK)),
        min(24, len(DECK)),
    )

    st.session_state.selected = []

    st.session_state.reading = []

    st.session_state.phase = "select"

    st.session_state.error = ""


# ============================================================
# SELECT / DESELECT CARD
# ============================================================

def select_card(card_index):

    maximum_cards = len(
        SPREADS[st.session_state.spread]
    )

    if card_index in st.session_state.selected:

        st.session_state.selected.remove(
            card_index
        )

    elif len(st.session_state.selected) < maximum_cards:

        st.session_state.selected.append(
            card_index
        )


# ============================================================
# REVEAL CARDS
# ============================================================

def reveal():

    positions = SPREADS[
        st.session_state.spread
    ]

    cards = []

    for position, index in zip(
        positions,
        st.session_state.selected,
    ):

        card = DECK[index]

        orientation = random.choice(
            [
                "Upright",
                "Reversed",
            ]
        )

        if orientation == "Upright":

            meaning = card["upright"]

        else:

            meaning = card["reversed"]

        cards.append(
            {
                "position": position,
                "name": card["name"],
                "orientation": orientation,
                "meaning": meaning,
            }
        )

    st.session_state.reading = cards

    st.session_state.phase = "reveal"


# ============================================================
# NEW READING
# ============================================================

def new_reading():

    st.session_state.pool = []

    st.session_state.selected = []

    st.session_state.reading = []

    st.session_state.question = ""

    st.session_state.phase = "setup"

    st.session_state.error = ""


# ============================================================
# CREATE CHATGPT COPY TEXT
# ============================================================

def create_chatgpt_prompt():

    category = st.session_state.category
    spread = st.session_state.spread
    question = st.session_state.question

    prompt = f"""
Please explain this tarot reading in simple,
easy-to-understand language.

I want you to:

1. Explain what each card means in its position.
2. Explain whether each card is upright or reversed.
3. Explain how the cards relate to each other.
4. Explain the overall message of the reading.
5. Relate the interpretation to my question.
6. Give me practical things I can reflect on or consider.
7. Clearly separate symbolic interpretation from facts.
8. Do not present tarot as a guaranteed prediction
   of the future.

Reading Category:
{category}

Spread:
{spread}

Question:
{question}

Cards:
"""

    for card in st.session_state.reading:

        prompt += (
            f"\n\n"
            f"Position: {card['position']}\n"
            f"Card: {card['name']}\n"
            f"Orientation: {card['orientation']}\n"
            f"Meaning: {card['meaning']}\n"
        )

    prompt += """

Please explain the reading in a warm,
clear and simple way.

Avoid complicated tarot terminology unless
you explain the terminology first.
"""

    return prompt.strip()


# ============================================================
# INITIALIZE
# ============================================================

init()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">

        <h1>🔮 Berlin Tarot Reading</h1>

        <p>
            Choose your question.
            Pick your own cards.
            Reveal your reading.
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SETUP SCREEN
# ============================================================

if st.session_state.phase == "setup":

    st.markdown(
        '<div class="section">'
        '1. Choose your reading'
        '</div>',
        unsafe_allow_html=True,
    )

    st.session_state.category = st.selectbox(
        "Reading category",
        list(CATEGORIES.keys()),
    )

    st.session_state.spread = st.selectbox(
        "Spread",
        list(SPREADS.keys()),
    )

    st.session_state.question = st.text_area(
        "Your question",
        value=st.session_state.question,
        placeholder=(
            "Example: What do I need to know "
            "about my career right now?"
        ),
        height=100,
    )

    if st.session_state.error:

        st.error(
            st.session_state.error
        )

    st.markdown(
        """
        <div class="instruction-box">

        <h3>🔮 How it works</h3>

        <p>
        Choose a category and ask your question.
        The deck will be shuffled and you will
        personally choose your cards.
        </p>

        <p>
        After choosing your cards, reveal them
        to see your reading.
        </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "✨ Start & Shuffle the Deck",
        type="primary",
        use_container_width=True,
    ):

        start_reading()

        st.rerun()


# ============================================================
# CARD SELECTION SCREEN
# ============================================================

elif st.session_state.phase == "select":

    required_cards = len(
        SPREADS[st.session_state.spread]
    )

    selected_cards = len(
        st.session_state.selected
    )

    card_word = (
        "card"
        if required_cards == 1
        else "cards"
    )

    st.markdown(
        f"""
        <div class="section">
            2. Pick {required_cards} {card_word}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        f"Selected: {selected_cards} / "
        f"{required_cards} — "
        "Tap a face-down card to select or deselect it."
    )

    pool = st.session_state.pool

    for row_start in range(
        0,
        len(pool),
        6,
    ):

        row = pool[
            row_start:row_start + 6
        ]

        columns = st.columns(
            len(row)
        )

        for column, index in zip(
            columns,
            row,
        ):

            with column:

                selected = (
                    index
                    in st.session_state.selected
                )

                css_class = (
                    "card-selected"
                    if selected
                    else ""
                )

                card_label = (
                    "Card chosen"
                    if selected
                    else "Face down"
                )

                button_label = (
                    "✓ Selected"
                    if selected
                    else "🂠 Pick"
                )

                st.markdown(
                    f"""
                    <div class="card-box {css_class}">

                        <div class="card-back">
                            ✦
                        </div>

                        <div>
                            {card_label}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button(
                    button_label,
                    key=f"pick_{index}",
                    use_container_width=True,
                ):

                    select_card(index)

                    st.rerun()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "✨ Reveal My Cards",
            type="primary",
            disabled=(
                selected_cards
                != required_cards
            ),
            use_container_width=True,
        ):

            reveal()

            st.rerun()

    with col2:

        if st.button(
            "↻ Reshuffle",
            use_container_width=True,
        ):

            st.session_state.pool = random.sample(
                range(len(DECK)),
                min(24, len(DECK)),
            )

            st.session_state.selected = []

            st.rerun()


# ============================================================
# READING SCREEN
# ============================================================

elif st.session_state.phase == "reveal":

    st.markdown(
        '<div class="section">'
        '3. Your cards'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write(
        f"**{st.session_state.category}** "
        f"· {st.session_state.spread}"
    )

    st.write(
        f"**Question:** "
        f"{st.session_state.question}"
    )

    cards = st.session_state.reading

    columns = st.columns(
        len(cards)
    )

    for column, card in zip(
        columns,
        cards,
    ):

        with column:

            st.markdown(
                f"""
                <div class="card-box card-revealed">

                    <div class="position">
                        {card["position"]}
                    </div>

                    <div
                        style="
                            font-size:2.7rem;
                            margin:.6rem
                        "
                    >
                        ✦
                    </div>

                    <div class="card-title">
                        {card["name"]}
                    </div>

                    <div class="orientation">
                        {card["orientation"]}
                    </div>

                    <div class="meaning">
                        {card["meaning"]}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


    # ========================================================
    # READING INTERPRETATION
    # ========================================================

    st.markdown(
        "### 🔮 Reading"
    )

    if (
        st.session_state.category
        == "🔮 Future"
    ):

        intro = (
            "This Future reading is best treated "
            "as a symbolic look at possible themes "
            "and preparation points — not a guaranteed "
            "prediction."
        )

    else:

        intro = (
            "Use these cards as symbolic prompts "
            "for reflection and decision-making."
        )

    st.info(intro)


    # ========================================================
    # CARD-BY-CARD INTERPRETATION
    # ========================================================

    for card in cards:

        st.markdown(
            f"**{card['position']} — "
            f"{card['name']} "
            f"({card['orientation']})**"
        )

        st.write(
            card["meaning"]
        )


    # ========================================================
    # CHATGPT EXPLANATION
    # ========================================================

    st.divider()

    st.markdown(
        "### 💬 Want a simpler explanation?"
    )

    st.write(
        """
        Your tarot result can have several symbolic
        interpretations.

        You can copy the reading below and paste it
        into ChatGPT to get a simpler explanation
        connected to your question.
        """
    )


    st.markdown(
        """
        <div class="instruction-box">

        <h3>🤖 How to use ChatGPT</h3>

        <p>
        <strong>1️⃣ Copy</strong> the reading below.
        </p>

        <p>
        <strong>2️⃣ Open ChatGPT.</strong>
        </p>

        <p>
        <strong>3️⃣ Paste</strong> the reading.
        </p>

        <p>
        <strong>4️⃣ Send it.</strong>
        </p>

        <p>
        ChatGPT will explain the cards in simpler
        language and relate them to your question.
        </p>

        <p class="chatgpt-prompt">
        "Explain this tarot reading to me in simple
        language. Relate it to my question, explain
        each card and the overall message, and give
        me practical things to reflect on. Do not
        treat it as a guaranteed prediction."
        </p>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # ========================================================
    # COPY-READY TEXT
    # ========================================================

    chatgpt_prompt = create_chatgpt_prompt()

    st.text_area(
        "📋 Copy this and paste it into ChatGPT",
        value=chatgpt_prompt,
        height=350,
    )

    st.info(
        "💡 Tip: Click inside the text box, "
        "press Ctrl+A, then Ctrl+C. "
        "Open ChatGPT, paste with Ctrl+V, "
        "and send it."
    )


    # ========================================================
    # NEW READING
    # ========================================================

    st.divider()

    if st.button(
        "🔄 Start a New Reading",
        type="primary",
        use_container_width=True,
    ):

        new_reading()

        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

    🔮 Berlin Tarot Reading ·
    Tarot is presented as a reflective/divination
    practice, not a guaranteed prediction.

    </div>
    """,
    unsafe_allow_html=True,
)