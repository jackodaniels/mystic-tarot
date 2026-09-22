import base64
import json
import random
import re
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
# PATHS
# ============================================================

BASE_DIR = Path(__file__).parent

DATA_FILE = BASE_DIR / "data" / "tarot_cards.json"

# Recommended for GitHub / Streamlit Cloud
IMAGE_DIR = BASE_DIR / "assets" / "tarot"

# Local Windows fallback
WINDOWS_IMAGE_DIR = Path(
    r"C:\Users\HDPlanco\Downloads\tarot"
)

CARD_BACK_NAME = "berlin-card-back.png"


# ============================================================
# LOAD TAROT DECK
# ============================================================

if not DATA_FILE.exists():

    st.error(
        f"Tarot deck file not found:\n\n{DATA_FILE}"
    )

    st.stop()


try:

    DECK = json.loads(
        DATA_FILE.read_text(
            encoding="utf-8"
        )
    )

except Exception as e:

    st.error(
        f"Unable to load tarot_cards.json:\n\n{e}"
    )

    st.stop()


# ============================================================
# FIND IMAGE DIRECTORY
# ============================================================

if IMAGE_DIR.exists():

    ACTIVE_IMAGE_DIR = IMAGE_DIR

elif WINDOWS_IMAGE_DIR.exists():

    ACTIVE_IMAGE_DIR = WINDOWS_IMAGE_DIR

else:

    ACTIVE_IMAGE_DIR = IMAGE_DIR


# ============================================================
# IMAGE HELPERS
# ============================================================

def normalize_name(value):

    value = value.lower().strip()

    value = value.replace(
        "_",
        "-"
    )

    value = re.sub(
        r"[^a-z0-9]+",
        "-",
        value
    )

    value = re.sub(
        r"-+",
        "-",
        value
    )

    return value.strip("-")


def extract_card_name_from_filename(filename):

    """
    Converts filenames such as:

    03-The-Empress-Tarot-card-img-182x300-1.jpg.jpeg

    into:

    the-empress
    """

    stem = filename

    # Remove extension(s)
    stem = re.sub(
        r"\.(jpeg|jpg|png|webp)$",
        "",
        stem,
        flags=re.IGNORECASE
    )

    stem = re.sub(
        r"\.(jpeg|jpg|png|webp)$",
        "",
        stem,
        flags=re.IGNORECASE
    )

    # Remove leading number
    stem = re.sub(
        r"^\d+-",
        "",
        stem
    )

    # Remove image suffix
    stem = re.sub(
        r"-tarot-card-img.*$",
        "",
        stem,
        flags=re.IGNORECASE
    )

    return normalize_name(stem)


def build_image_map():

    image_map = {}

    if not ACTIVE_IMAGE_DIR.exists():

        return image_map

    extensions = [
        "*.jpg",
        "*.jpeg",
        "*.png",
        "*.webp",
    ]

    files = []

    for extension in extensions:

        files.extend(
            ACTIVE_IMAGE_DIR.glob(extension)
        )

    for file in files:

        key = extract_card_name_from_filename(
            file.name
        )

        if key:

            image_map[key] = file

    return image_map


CARD_IMAGES = build_image_map()


def get_card_image(card_name):

    key = normalize_name(
        card_name
    )

    return CARD_IMAGES.get(
        key
    )


def get_card_back():

    path = (
        ACTIVE_IMAGE_DIR
        / CARD_BACK_NAME
    )

    if path.exists():

        return path

    # Try other common formats
    for filename in [
        "berlin-card-back.jpg",
        "berlin-card-back.jpeg",
        "berlin-card-back.webp",
    ]:

        alternative = (
            ACTIVE_IMAGE_DIR
            / filename
        )

        if alternative.exists():

            return alternative

    return None


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
        "Guidance",
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

    /* =======================================================
       MAIN APP
       ======================================================= */

    .stApp {

        background:
            radial-gradient(
                circle at top,
                #1b1033 0%,
                #0b0717 45%,
                #05030b 100%
            );

        color: #f5efff;
    }


    .block-container {

        max-width: 1400px;

        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }


    /* =======================================================
       HEADER
       ======================================================= */

    .hero {

        text-align: center;

        padding:
            1rem
            1rem
            1.8rem;

        border-bottom:
            1px solid
            rgba(196, 157, 255, .22);

        margin-bottom: 1.5rem;
    }


    .hero h1 {

        font-size: 3.1rem;

        margin:
            0;

        letter-spacing:
            .03em;

        background:
            linear-gradient(
                90deg,
                #d9b7ff,
                #ffffff,
                #c59cff
            );

        -webkit-background-clip:
            text;

        -webkit-text-fill-color:
            transparent;
    }


    .hero p {

        color:
            #aaa0bd;

        font-size:
            1.05rem;

        margin-top:
            .6rem;
    }


    /* =======================================================
       SECTIONS
       ======================================================= */

    .section {

        color:
            #e1d5f5;

        font-weight:
            800;

        margin:
            1.2rem
            0
            .7rem;

        font-size:
            1.3rem;
    }


    /* =======================================================
       SETUP BOX
       ======================================================= */

    .setup-box {

        border:
            1px solid
            rgba(182, 156, 255, .28);

        border-radius:
            18px;

        padding:
            20px;

        background:
            linear-gradient(
                145deg,
                rgba(35, 23, 60, .88),
                rgba(13, 8, 25, .88)
            );

        box-shadow:
            0 15px 40px
            rgba(0, 0, 0, .30);
    }


    /* =======================================================
       CARD SELECTION
       ======================================================= */

    .selection-info {

        text-align:
            center;

        color:
            #bcb1ce;

        margin-bottom:
            1rem;
    }


    .selection-card {

        text-align:
            center;

        padding:
            6px;

        border-radius:
            18px;

        background:
            linear-gradient(
                145deg,
                rgba(31, 20, 54, .92),
                rgba(11, 7, 22, .95)
            );

        border:
            1px solid
            rgba(255, 255, 255, .10);

        box-shadow:
            0 10px 30px
            rgba(0, 0, 0, .30);

        transition:
            all .2s ease;
    }


    .selection-card:hover {

        transform:
            translateY(-5px);

        border-color:
            rgba(193, 155, 255, .65);

        box-shadow:
            0 15px 35px
            rgba(113, 65, 180, .25);
    }


    .selected-card {

        border:
            2px solid
            #c59cff;

        box-shadow:
            0 0 25px
            rgba(197, 156, 255, .55);
    }


    .card-number {

        text-align:
            center;

        color:
            #bda9d7;

        font-size:
            .85rem;

        margin-top:
            5px;

        letter-spacing:
            .08em;
    }


    /* =======================================================
       REVEALED CARDS
       ======================================================= */

    .reading-card {

        background:
            linear-gradient(
                145deg,
                rgba(34, 22, 57, .96),
                rgba(10, 7, 19, .97)
            );

        border:
            1px solid
            rgba(201, 165, 255, .28);

        border-radius:
            20px;

        padding:
            16px;

        text-align:
            center;

        min-height:
            560px;

        box-shadow:
            0 18px 45px
            rgba(0, 0, 0, .35);
    }


    .reading-position {

        color:
            #d8c8ec;

        font-size:
            .83rem;

        font-weight:
            700;

        text-transform:
            uppercase;

        letter-spacing:
            .08em;

        margin-bottom:
            10px;
    }


    .reading-card-title {

        font-size:
            1.35rem;

        font-weight:
            800;

        margin-top:
            10px;

        color:
            #f3eaff;
    }


    .orientation {

        display:
            inline-block;

        margin-top:
            8px;

        padding:
            5px 13px;

        border-radius:
            20px;

        color:
            #d8c1ff;

        background:
            rgba(142, 95, 214, .16);

        border:
            1px solid
            rgba(194, 155, 255, .25);

        font-size:
            .78rem;

        font-weight:
            700;

        text-transform:
            uppercase;

        letter-spacing:
            .08em;
    }


    .meaning {

        color:
            #c7bfd2;

        font-size:
            .94rem;

        line-height:
            1.6;

        margin-top:
            14px;

        text-align:
            left;
    }


    /* =======================================================
       CHATGPT BOX
       ======================================================= */

    .instruction-box {

        border:
            1px solid
            rgba(182, 156, 255, .28);

        border-radius:
            18px;

        padding:
            20px;

        background:
            rgba(30, 20, 51, .65);

        margin-top:
            1rem;
    }


    .instruction-box h3 {

        margin-top:
            0;

        color:
            #eee5ff;
    }


    .chatgpt-prompt {

        border-left:
            3px solid
            #b69cff;

        padding-left:
            14px;

        color:
            #cfc6dd;

        font-style:
            italic;
    }


    /* =======================================================
       FOOTER
       ======================================================= */

    .footer {

        text-align:
            center;

        color:
            #71677d;

        margin-top:
            2.5rem;

        font-size:
            .85rem;
    }


    /* =======================================================
       MOBILE
       ======================================================= */

    @media (max-width: 768px) {

        .hero h1 {

            font-size:
                2rem;
        }

        .reading-card {

            min-height:
                auto;
        }

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

        "phase":
            "setup",

        "pool":
            [],

        "selected":
            [],

        "reading":
            [],

        "question":
            "",

        "category":
            "💼 Career",

        "spread":
            "3 Cards",

        "error":
            "",

    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


init()


# ============================================================
# START READING
# ============================================================

def start_reading():

    question = (
        st.session_state.question
        .strip()
    )

    if not question:

        st.session_state.error = (
            "Please enter a question before starting."
        )

        return

    # ONLY 8 visible cards
    st.session_state.pool = random.sample(
        range(len(DECK)),
        min(8, len(DECK)),
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
        SPREADS[
            st.session_state.spread
        ]
    )

    if card_index in st.session_state.selected:

        st.session_state.selected.remove(
            card_index
        )

    elif (
        len(st.session_state.selected)
        < maximum_cards
    ):

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

            meaning = card.get(
                "upright",
                ""
            )

        else:

            meaning = card.get(
                "reversed",
                ""
            )

        cards.append(
            {
                "position":
                    position,

                "name":
                    card["name"],

                "orientation":
                    orientation,

                "meaning":
                    meaning,
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
# CREATE CHATGPT PROMPT
# ============================================================

def create_chatgpt_prompt():

    category = (
        st.session_state.category
    )

    spread = (
        st.session_state.spread
    )

    question = (
        st.session_state.question
    )

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

    st.markdown(
        '<div class="setup-box">',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:

        st.session_state.category = (
            st.selectbox(
                "Reading category",
                list(
                    CATEGORIES.keys()
                ),
            )
        )

    with col2:

        st.session_state.spread = (
            st.selectbox(
                "Spread",
                list(
                    SPREADS.keys()
                ),
            )
        )

    st.session_state.question = (
        st.text_area(
            "Your question",

            value=(
                st.session_state.question
            ),

            placeholder=(
                "Example: "
                "What will happen "
                "in the next 3 months?"
            ),

            height=100,
        )
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
        Think about your question while choosing
        your reading category and spread.
        </p>

        <p>
        The deck will shuffle and show you
        <strong>8 Berlin Tarot card backs</strong>.
        Choose your cards personally.
        </p>

        <p>
        Your selected cards will then be revealed
        as actual Tarot card images.
        </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )

    if st.button(
        "✨ Start & Shuffle the Deck",
        type="primary",
        use_container_width=True,
    ):

        start_reading()

        st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# CARD SELECTION SCREEN
# ============================================================

elif st.session_state.phase == "select":

    required_cards = len(
        SPREADS[
            st.session_state.spread
        ]
    )

    selected_cards = len(
        st.session_state.selected
    )

    st.markdown(
        f"""
        <div class="section">
            2. Pick {required_cards}
            {"card" if required_cards == 1 else "cards"}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="selection-info">

            Select <strong>{required_cards}</strong>
            card{"s" if required_cards != 1 else ""}

            from the
            <strong>8 Berlin cards</strong>
            below.

            <br>

            Selected:
            <strong>
                {selected_cards} / {required_cards}
            </strong>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # ========================================================
    # CARD BACK
    # ========================================================

    card_back = get_card_back()

    if card_back is None:

        st.warning(
            "⚠️ Berlin card-back image not found."
        )

        st.caption(
            "Expected file: "
            "assets/tarot/berlin-card-back.png"
        )

    # ========================================================
    # 8 CARD POSITIONS
    # ========================================================

    pool = st.session_state.pool

    columns = st.columns(
        8,
        gap="small",
    )

    for position_number, (
        column,
        index
    ) in enumerate(
        zip(columns, pool),
        start=1,
    ):

        with column:

            selected = (
                index
                in st.session_state.selected
            )

            css_class = (
                "selected-card"
                if selected
                else "selection-card"
            )

            st.markdown(
                f"""
                <div class="{css_class}">
                """,
                unsafe_allow_html=True,
            )

            # Actual Berlin card-back image
            if card_back is not None:

                st.image(
                    str(card_back),
                    use_container_width=True,
                )

            else:

                st.markdown(
                    """
                    <div style="
                        height:260px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        font-size:4rem;
                    ">
                        👑
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                f"""
                <div class="card-number">
                    CARD {position_number}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

            if selected:

                button_label = (
                    "✓ Selected"
                )

            else:

                button_label = (
                    "🃏 Pick"
                )

            if st.button(
                button_label,
                key=f"pick_{index}",
                use_container_width=True,
            ):

                select_card(index)

                st.rerun()

    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )

    # ========================================================
    # ACTION BUTTONS
    # ========================================================

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
            "↻ Reshuffle 8 Cards",
            use_container_width=True,
        ):

            st.session_state.pool = (
                random.sample(
                    range(len(DECK)),
                    min(8, len(DECK)),
                )
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
        f" · "
        f"{st.session_state.spread}"
    )

    st.write(
        f"**Question:** "
        f"{st.session_state.question}"
    )

    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )

    cards = (
        st.session_state.reading
    )

    # ========================================================
    # REVEALED TAROT CARDS
    # ========================================================

    columns = st.columns(
        len(cards),
        gap="large",
    )

    for column, card in zip(
        columns,
        cards,
    ):

        with column:

            image_path = get_card_image(
                card["name"]
            )

            st.markdown(
                f"""
                <div class="reading-card">

                    <div class="reading-position">
                        {card["position"]}
                    </div>

                """,
                unsafe_allow_html=True,
            )

            # ------------------------------------------------
            # CARD IMAGE
            # ------------------------------------------------

            if image_path is not None:

                if (
                    card["orientation"]
                    == "Reversed"
                ):

                    # Display reversed card
                    image_bytes = (
                        image_path.read_bytes()
                    )

                    encoded = (
                        base64.b64encode(
                            image_bytes
                        ).decode(
                            "utf-8"
                        )
                    )

                    suffix = (
                        image_path.suffix
                        .lower()
                    )

                    if suffix == ".png":

                        mime = "image/png"

                    elif suffix in [
                        ".jpg",
                        ".jpeg",
                    ]:

                        mime = "image/jpeg"

                    else:

                        mime = "image/webp"

                    st.markdown(
                        f"""
                        <div style="
                            display:flex;
                            justify-content:center;
                            margin:10px auto;
                        ">

                            <img
                                src="data:{mime};base64,{encoded}"
                                style="
                                    width:100%;
                                    max-width:270px;
                                    border-radius:12px;
                                    border:3px solid #c9a86a;
                                    box-shadow:
                                        0 15px 40px
                                        rgba(0,0,0,.55);
                                    transform:rotate(180deg);
                                "
                            >

                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                else:

                    st.image(
                        str(image_path),
                        use_container_width=True,
                    )

            else:

                st.error(
                    f"Image not found for "
                    f"**{card['name']}**"
                )

                st.caption(
                    f"Looking in: "
                    f"{ACTIVE_IMAGE_DIR}"
                )

            # ------------------------------------------------
            # CARD NAME
            # ------------------------------------------------

            st.markdown(
                f"""
                    <div class="reading-card-title">

                        {card["name"]}

                    </div>

                    <div class="orientation">

                        ✦ {card["orientation"]} ✦

                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            # ------------------------------------------------
            # MEANING
            # ------------------------------------------------

            st.markdown(
                f"""
                <div class="meaning">

                    {card["meaning"]}

                </div>
                """,
                unsafe_allow_html=True,
            )

    # ========================================================
    # READING INTERPRETATION
    # ========================================================

    st.divider()

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

    st.info(
        intro
    )

    # ========================================================
    # CARD-BY-CARD INTERPRETATION
    # ========================================================

    for card in cards:

        st.markdown(
            f"""
            **{card['position']} — "
            f"{card['name']} "
            f"({card['orientation']})**
            """.replace(
                '"',
                ""
            )
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
        Your Tarot result can have several
        symbolic interpretations.

        Copy the reading below and paste it into
        ChatGPT to get a simpler explanation
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

    chatgpt_prompt = (
        create_chatgpt_prompt()
    )

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

        🔮 Berlin Tarot Reading

        <br>

        Tarot is presented as a reflective
        and symbolic practice, not a guaranteed
        prediction.

    </div>
    """,
    unsafe_allow_html=True,
)