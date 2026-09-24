import base64
import json
import random
import re
import time
from datetime import date
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Berlin Tarot Reading",
    page_icon="🔮",
    layout="wide",
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).parent

DATA_FILE = BASE_DIR / "data" / "tarot_cards.json"

IMAGE_DIR = BASE_DIR / "assets" / "tarot"

# Local Windows fallback
WINDOWS_IMAGE_DIR = Path(
    r"C:\Users\HDPlanco\Downloads\tarot"
)

CARD_BACK_FILENAMES = [
    "berlin-card-back.png",
    "berlin-card-back.jpg",
    "berlin-card-back.jpeg",
    "berlin-card-back.webp",
]

BANNER_FILENAMES = [
    "Banner.png",
    "banner.png",
]

WINDOWS_BANNER_PATH = Path(
    r"C:\Users\HDPlanco\Downloads\tarot\Banner.png"
)


# ============================================================
# LOAD TAROT DECK
# ============================================================

if not DATA_FILE.exists():

    st.error(
        f"Tarot data file was not found:\n\n{DATA_FILE}"
    )

    st.stop()


try:

    DECK = json.loads(
        DATA_FILE.read_text(
            encoding="utf-8"
        )
    )

except Exception as error:

    st.error(
        "Unable to load tarot_cards.json."
    )

    st.exception(error)

    st.stop()


# ============================================================
# DETERMINE IMAGE DIRECTORY
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

    value = str(value).lower().strip()

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

    name = filename

    # Remove extension
    name = re.sub(
        r"\.(jpeg|jpg|png|webp)$",
        "",
        name,
        flags=re.IGNORECASE
    )

    # Handle filenames such as .jpg.jpeg
    name = re.sub(
        r"\.(jpeg|jpg|png|webp)$",
        "",
        name,
        flags=re.IGNORECASE
    )

    # Remove leading card number
    name = re.sub(
        r"^\d+-",
        "",
        name
    )

    # Remove common suffix
    name = re.sub(
        r"-tarot-card-img.*$",
        "",
        name,
        flags=re.IGNORECASE
    )

    return normalize_name(name)


def build_card_image_map():

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

    for image_file in files:

        key = extract_card_name_from_filename(
            image_file.name
        )

        if key:

            image_map[key] = image_file

    return image_map


CARD_IMAGES = build_card_image_map()


def get_card_image(card_name):

    key = normalize_name(
        card_name
    )

    # Exact match
    if key in CARD_IMAGES:

        return CARD_IMAGES[key]

    # Flexible matching
    for image_key, image_path in CARD_IMAGES.items():

        if (
            image_key in key
            or key in image_key
        ):

            return image_path

    return None


def get_card_back():

    for filename in CARD_BACK_FILENAMES:

        path = (
            ACTIVE_IMAGE_DIR
            / filename
        )

        if path.exists():

            return path

    return None


def get_banner():

    for filename in BANNER_FILENAMES:

        path = IMAGE_DIR / filename

        if path.exists():

            return path

    if WINDOWS_BANNER_PATH.exists():

        return WINDOWS_BANNER_PATH

    return None


# ============================================================
# READING CATEGORIES
# ============================================================

CATEGORIES = {

    "💼 Career":
        "career",

    "❤️ Love":
        "love",

    "💰 Money":
        "money",

    "🌱 Personal Growth":
        "growth",

    "🔮 Future":
        "future",

}


# ============================================================
# TAROT SPREADS
# ============================================================

SPREADS = {

    "1 Card": [
        "Guidance",
    ],

    "3 Cards": [
        "Situation",
        "Challenge",
        "Guidance",
    ],

    "5 Cards": [
        "Situation",
        "Challenge",
        "Hidden Influence",
        "Advice",
        "Direction",
    ],

}

# Simple explanations shown to users when they choose a spread.
SPREAD_DESCRIPTIONS = {

    "1 Card": {
        "purpose": "Quick, focused guidance for one question or daily reflection.",
        "positions": [
            ("Guidance", "The main symbolic message or energy to reflect on."),
        ],
    },

    "3 Cards": {
        "purpose": "A simple three-part view of your situation: what is happening, what may be difficult, and what to consider next.",
        "positions": [
            ("Situation", "What is happening or influencing you now."),
            ("Challenge", "The main obstacle, tension, or difficulty to consider."),
            ("Guidance", "What you can reflect on or consider moving forward."),
        ],
    },

    "5 Cards": {
        "purpose": "A deeper reflection that explores the situation, challenge, hidden influence, advice, and symbolic direction.",
        "positions": [
            ("Situation", "Your current circumstances or the main energy around the question."),
            ("Challenge", "The main obstacle, tension, or issue to work through."),
            ("Hidden Influence", "Something beneath the surface that may be affecting the situation."),
            ("Advice", "A practical or reflective message to consider."),
            ("Direction", "The symbolic direction or theme to reflect on going forward—not a guaranteed prediction."),
        ],
    },

}


# ============================================================
# ZODIAC
# ============================================================

ZODIAC_SIGNS = [

    {
        "name": "♑ Capricorn",
        "symbol": "♑",
        "start": (12, 22),
        "end": (1, 19),
        "description":
            "Discipline, ambition, responsibility, structure, and long-term goals.",
    },

    {
        "name": "♒ Aquarius",
        "symbol": "♒",
        "start": (1, 20),
        "end": (2, 18),
        "description":
            "Independence, originality, ideas, community, and unconventional thinking.",
    },

    {
        "name": "♓ Pisces",
        "symbol": "♓",
        "start": (2, 19),
        "end": (3, 20),
        "description":
            "Sensitivity, imagination, intuition, compassion, and emotional depth.",
    },

    {
        "name": "♈ Aries",
        "symbol": "♈",
        "start": (3, 21),
        "end": (4, 19),
        "description":
            "Initiative, courage, action, independence, and directness.",
    },

    {
        "name": "♉ Taurus",
        "symbol": "♉",
        "start": (4, 20),
        "end": (5, 20),
        "description":
            "Stability, patience, practicality, comfort, and persistence.",
    },

    {
        "name": "♊ Gemini",
        "symbol": "♊",
        "start": (5, 21),
        "end": (6, 20),
        "description":
            "Curiosity, communication, adaptability, learning, and variety.",
    },

    {
        "name": "♋ Cancer",
        "symbol": "♋",
        "start": (6, 21),
        "end": (7, 22),
        "description":
            "Emotional connection, care, intuition, home, and security.",
    },

    {
        "name": "♌ Leo",
        "symbol": "♌",
        "start": (7, 23),
        "end": (8, 22),
        "description":
            "Confidence, creativity, expression, generosity, and recognition.",
    },

    {
        "name": "♍ Virgo",
        "symbol": "♍",
        "start": (8, 23),
        "end": (9, 22),
        "description":
            "Organization, analysis, service, precision, and practical improvement.",
    },

    {
        "name": "♎ Libra",
        "symbol": "♎",
        "start": (9, 23),
        "end": (10, 22),
        "description":
            "Balance, relationships, diplomacy, beauty, and fairness.",
    },

    {
        "name": "♏ Scorpio",
        "symbol": "♏",
        "start": (10, 23),
        "end": (11, 21),
        "description":
            "Intensity, transformation, determination, privacy, and depth.",
    },

    {
        "name": "♐ Sagittarius",
        "symbol": "♐",
        "start": (11, 22),
        "end": (12, 21),
        "description":
            "Exploration, optimism, freedom, learning, and broader perspective.",
    },

]


def get_zodiac_sign(birthday):

    month = birthday.month
    day = birthday.day

    for sign in ZODIAC_SIGNS:

        start_month, start_day = sign["start"]
        end_month, end_day = sign["end"]

        # Capricorn crosses the year boundary
        if start_month == 12:

            if (
                (month == 12 and day >= start_day)
                or
                (month == 1 and day <= end_day)
            ):

                return sign

        else:

            if (
                (month == start_month and day >= start_day)
                or
                (month == end_month and day <= end_day)
                or
                (
                    start_month < month < end_month
                )
            ):

                return sign

    return ZODIAC_SIGNS[0]


# ============================================================
# HOROSCOPE CONTENT
# ============================================================

HOROSCOPE_THEMES = {

    "career": {

        "title":
            "💼 Career",

        "themes": [

            "Focus on priorities rather than trying to solve everything at once.",

            "A practical conversation may help clarify your next step.",

            "Review your current goals and decide which one deserves the most attention.",

            "Consistency may be more useful than rushing into a new direction.",

            "Look for opportunities to improve a skill or strengthen your professional position.",

        ],
    },

    "love": {

        "title":
            "❤️ Love & Relationships",

        "themes": [

            "Clear communication can help reduce misunderstandings.",

            "Pay attention to what you need as well as what others need.",

            "A calm conversation may reveal something important about a relationship.",

            "Give relationships room for honesty, boundaries, and mutual respect.",

            "If you are single, focus on the qualities you genuinely value in a connection.",

        ],
    },

    "money": {

        "title":
            "💰 Money",

        "themes": [

            "Review your spending and prioritize practical financial decisions.",

            "Avoid making financial decisions purely from emotion or pressure.",

            "A small improvement in financial organization can have a useful effect over time.",

            "Consider which expenses are necessary and which can be reduced.",

            "Focus on stability and informed choices rather than quick results.",

        ],
    },

    "growth": {

        "title":
            "🌱 Personal Growth",

        "themes": [

            "Give yourself permission to change your approach when something is no longer working.",

            "Reflection can help you recognize patterns that deserve attention.",

            "Set one realistic goal and take a concrete step toward it.",

            "Protect time for rest, learning, and activities that help you reconnect with yourself.",

            "Growth does not always require a dramatic change; small consistent steps matter.",

        ],
    },

}


def generate_horoscope(sign, birthday):

    # Deterministic daily seed based on date + birthday + sign
    today = date.today()

    seed_text = (
        f"{today.isoformat()}-"
        f"{birthday.isoformat()}-"
        f"{sign['name']}"
    )

    rng = random.Random(
        seed_text
    )

    selected = {}

    for category, data in HOROSCOPE_THEMES.items():

        selected[category] = rng.choice(
            data["themes"]
        )

    return selected


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session():

    defaults = {

        "mode":
            "Tarot Reading",

        "phase":
            "setup",

        "pool":
            [],

        "selected":
            [],

        "selected_details":
            {},

        "reading":
            [],

        "question":
            "",

        "category":
            "💼 Career",

        "spread":
            "3 Cards",

        "name":
            "",

        "birthday":
            None,

        "zodiac":
            None,

        "horoscope":
            {},

        "error":
            "",

    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


initialize_session()


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   APP
   ============================================================ */

.stApp {

    background:
        radial-gradient(
            circle at top,
            #1d1235 0%,
            #0b0717 45%,
            #05030b 100%
        );

    color: #f4edff;
}


.block-container {

    max-width: 1400px;

    padding-top: 0.75rem;
    padding-bottom: 2rem;
    padding-left: 1rem;
    padding-right: 1rem;
}


/* ============================================================
   HERO
   ============================================================ */

.hero {

    text-align: center;

    padding:
        1rem
        1rem
        1.7rem;

    margin-bottom:
        1.5rem;

    border-bottom:
        1px solid
        rgba(194, 155, 255, .25);
}


.hero h1 {

    font-size:
        3rem;

    font-weight:
        800;

    margin:
        0;

    letter-spacing:
        .03em;

    background:
        linear-gradient(
            90deg,
            #d7b5ff,
            #ffffff,
            #c89eff
        );

    -webkit-background-clip:
        text;

    -webkit-text-fill-color:
        transparent;
}


.hero-subtitle {

    color:
        #aaa0bd;

    font-size:
        1.05rem;

    margin-top:
        .6rem;
}


/* ============================================================
   MODE TABS
   ============================================================ */

.mode-description {

    text-align:
        center;

    color:
        #aaa0bd;

    margin-bottom:
        1rem;
}


/* ============================================================
   SECTION
   ============================================================ */

.section-title {

    font-size:
        1.3rem;

    font-weight:
        800;

    color:
        #e6d9f8;

    margin-top:
        1.2rem;

    margin-bottom:
        .8rem;
}


/* ============================================================
   INFO BOX
   ============================================================ */

.info-box {

    border:
        1px solid
        rgba(182, 156, 255, .25);

    border-radius:
        16px;

    padding:
        18px;

    background:
        rgba(28, 18, 49, .65);

    margin-top:
        1rem;
}


.info-title {

    font-size:
        1.15rem;

    font-weight:
        800;

    color:
        #eee5ff;

    margin-bottom:
        .6rem;
}


.info-text {

    color:
        #c9bfd5;

    line-height:
        1.6;
}


/* ============================================================
   CARD BACK
   ============================================================ */

.card-back-wrapper {

    background:
        linear-gradient(
            145deg,
            rgba(40, 25, 65, .9),
            rgba(10, 6, 20, .95)
        );

    border:
        1px solid
        rgba(191, 151, 255, .22);

    border-radius:
        16px;

    padding:
        6px;

    box-shadow:
        0 12px 30px
        rgba(0, 0, 0, .4);

    transition:
        all .2s ease;
}


.card-back-wrapper:hover {

    transform:
        translateY(-5px);

    border-color:
        rgba(202, 165, 255, .65);

    box-shadow:
        0 18px 38px
        rgba(119, 68, 190, .28);
}


.selected-wrapper {

    background:
        linear-gradient(
            145deg,
            #35205d,
            #130b25
        );

    border:
        2px solid
        #c69cff;

    border-radius:
        16px;

    padding:
        5px;

    box-shadow:
        0 0 28px
        rgba(193, 150, 255, .55);
}


.card-number {

    text-align:
        center;

    color:
        #bcaed0;

    font-size:
        .72rem;

    letter-spacing:
        .08em;

    margin-top:
        3px;
}


/* ============================================================
   READING CARD
   ============================================================ */

.reading-card {

    background:
        linear-gradient(
            145deg,
            rgba(35, 23, 58, .97),
            rgba(10, 7, 19, .98)
        );

    border:
        1px solid
        rgba(198, 161, 255, .30);

    border-radius:
        20px;

    padding:
        16px;

    text-align:
        center;

    box-shadow:
        0 18px 45px
        rgba(0, 0, 0, .4);
}


.reading-position {

    color:
        #d9c8ec;

    font-size:
        .78rem;

    font-weight:
        800;

    text-transform:
        uppercase;

    letter-spacing:
        .08em;

    margin-bottom:
        10px;
}


.reading-card-title {

    color:
        #f4eaff;

    font-size:
        1.3rem;

    font-weight:
        800;

    margin-top:
        10px;
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

    border:
        1px solid
        rgba(195, 157, 255, .30);

    background:
        rgba(134, 87, 207, .18);

    color:
        #d9c0ff;

    font-size:
        .75rem;

    font-weight:
        800;

    text-transform:
        uppercase;

    letter-spacing:
        .08em;
}


.meaning {

    color:
        #c8bfd2;

    font-size:
        .92rem;

    line-height:
        1.6;

    margin-top:
        12px;

    text-align:
        left;
}


/* ============================================================
   HOROSCOPE
   ============================================================ */

.zodiac-card {

    text-align:
        center;

    padding:
        25px;

    border-radius:
        20px;

    background:
        linear-gradient(
            145deg,
            rgba(45, 26, 73, .95),
            rgba(12, 7, 23, .98)
        );

    border:
        1px solid
        rgba(202, 165, 255, .30);

    box-shadow:
        0 18px 45px
        rgba(0, 0, 0, .35);

    margin:
        1rem 0;
}


.zodiac-symbol {

    font-size:
        4rem;

    margin-bottom:
        .5rem;
}


.zodiac-name {

    font-size:
        2rem;

    font-weight:
        800;

    color:
        #eadbff;
}


.zodiac-description {

    color:
        #bcb1ca;

    margin-top:
        .5rem;

    line-height:
        1.6;
}


.horoscope-section {

    border:
        1px solid
        rgba(182, 156, 255, .22);

    border-radius:
        16px;

    padding:
        18px;

    margin:
        1rem 0;

    background:
        rgba(28, 18, 49, .55);
}


.horoscope-section h3 {

    margin-top:
        0;

    color:
        #eadcff;
}


.horoscope-section p {

    color:
        #c9bfd5;

    line-height:
        1.6;
}


/* ============================================================
   CHATGPT
   ============================================================ */

.chat-box {

    border:
        1px solid
        rgba(182, 156, 255, .28);

    border-radius:
        18px;

    padding:
        20px;

    background:
        rgba(30, 20, 52, .65);

    margin-top:
        1rem;
}


.chat-title {

    color:
        #eee4ff;

    font-size:
        1.2rem;

    font-weight:
        800;
}


.chat-prompt {

    border-left:
        3px solid
        #b69cff;

    padding-left:
        14px;

    color:
        #cec4da;

    font-style:
        italic;

    line-height:
        1.5;
}


/* ============================================================
   FOOTER
   ============================================================ */

.footer {

    text-align:
        center;

    color:
        #746a80;

    font-size:
        .82rem;

    margin-top:
        2rem;
}


/* ============================================================
   MOBILE
   ============================================================ */

/* ============================================================
   RESPONSIVE / MOBILE
   ============================================================ */

@media (max-width: 900px) {

    .block-container {
        max-width: none !important;
        width: 100% !important;
        padding: 0.35rem 0.35rem 1.5rem !important;
    }

    [data-testid="stAppViewContainer"] > .main {
        width: 100% !important;
    }

    [data-testid="stAppViewContainer"] > .main > div {
        width: 100% !important;
    }

    /* Let Streamlit columns wrap instead of forcing 8 cards
       into an unusably narrow single row. */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        row-gap: 0.75rem !important;
    }

    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
    [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        min-width: 0 !important;
    }

    .hero {
        padding: 0 !important;
        margin: 0 0 1rem 0 !important;
    }

    .hero {
        width: 100vw !important;
        margin-left: calc(50% - 50vw) !important;
        margin-right: calc(50% - 50vw) !important;
    }

    .hero img {
        width: 100vw !important;
        max-width: 100vw !important;
        height: auto !important;
        border-radius: 0 !important;
        display: block !important;
    }

    .section-title {
        font-size: 1.15rem !important;
        margin-top: 0.8rem !important;
    }

    .info-box {
        padding: 13px !important;
        border-radius: 12px !important;
    }

    .zodiac-card {
        padding: 18px 12px !important;
        margin: 0.75rem 0 !important;
    }

    .zodiac-symbol {
        font-size: 3rem !important;
    }

    .zodiac-name {
        font-size: 1.45rem !important;
    }

    .horoscope-section {
        padding: 14px !important;
        margin: 0.7rem 0 !important;
    }

    /* Make Streamlit's input controls comfortable for touch. */
    input, textarea, [role="combobox"] {
        font-size: 16px !important;
    }

    button {
        min-height: 44px !important;
    }

}

@media (max-width: 700px) {

    /* Use almost the entire phone viewport. */
    .block-container {
        padding-left: 0.25rem !important;
        padding-right: 0.25rem !important;
        padding-top: 0.25rem !important;
        width: 100vw !important;
        max-width: 100vw !important;
    }

    /* Two cards per row on phones. */
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
    [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        flex: 0 0 calc(50% - 0.45rem) !important;
        width: calc(50% - 0.45rem) !important;
        max-width: calc(50% - 0.45rem) !important;
    }

    /* Single-column content blocks remain full width. */
    .stMarkdown,
    .stAlert {
        max-width: 100%;
    }

    .card-back-wrapper,
    .selected-wrapper {
        padding: 4px !important;
        border-radius: 12px !important;
    }

    .card-number {
        font-size: 0.65rem !important;
    }

    .reading-card-title {
        font-size: 1rem !important;
    }

    .meaning {
        font-size: 0.88rem !important;
    }

}

@media (max-width: 430px) {

    .block-container {
        padding-left: 0.15rem !important;
        padding-right: 0.15rem !important;
        width: 100vw !important;
        max-width: 100vw !important;
    }

    /* Keep the two-card layout but use the available width efficiently. */
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
    [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        flex: 0 0 calc(50% - 0.3rem) !important;
        width: calc(50% - 0.3rem) !important;
        max-width: calc(50% - 0.3rem) !important;
    }

    .hero img {
        border-radius: 8px !important;
    }

}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# TAROT FUNCTIONS
# ============================================================

def start_tarot():

    question = (
        st.session_state.question
        .strip()
    )

    name = (
        st.session_state.name
        .strip()
    )

    if not name:

        st.session_state.error = (
            "Please enter your name."
        )

        return

    if st.session_state.birthday is None:

        st.session_state.error = (
            "Please enter your birthday."
        )

        return

    if not question:

        st.session_state.error = (
            "Please enter your Tarot question."
        )

        return

    # Show exactly 8 random cards
    st.session_state.pool = random.sample(
        range(len(DECK)),
        min(
            8,
            len(DECK)
        )
    )

    st.session_state.selected = []

    st.session_state.selected_details = {}

    st.session_state.reading = []

    # Show a dedicated shuffle animation before card picking.
    st.session_state.phase = "tarot_shuffle"

    st.session_state.error = ""


def toggle_card(card_index):

    maximum_cards = len(
        SPREADS[
            st.session_state.spread
        ]
    )

    # Unpick an already selected card.
    if card_index in st.session_state.selected:

        st.session_state.selected.remove(
            card_index
        )

        st.session_state.selected_details.pop(
            card_index,
            None,
        )

        return

    # Pick a new card and immediately assign its orientation.
    if (
        len(st.session_state.selected)
        < maximum_cards
    ):

        card = DECK[card_index]

        orientation = random.choice(
            [
                "Upright",
                "Reversed",
            ]
        )

        meaning = (
            card.get("upright", "")
            if orientation == "Upright"
            else card.get("reversed", "")
        )

        st.session_state.selected.append(
            card_index
        )

        st.session_state.selected_details[
            card_index
        ] = {
            "name": card["name"],
            "orientation": orientation,
            "meaning": meaning,
        }


def reveal_tarot():

    positions = SPREADS[
        st.session_state.spread
    ]

    reading = []

    for position, index in zip(
        positions,
        st.session_state.selected,
    ):

        details = st.session_state.selected_details.get(
            index
        )

        if not details:

            card = DECK[index]

            orientation = random.choice(
                [
                    "Upright",
                    "Reversed",
                ]
            )

            details = {
                "name": card["name"],
                "orientation": orientation,
                "meaning": (
                    card.get("upright", "")
                    if orientation == "Upright"
                    else card.get("reversed", "")
                ),
            }

        reading.append(
            {
                "position": position,
                "pool_index": index,
                "name": details["name"],
                "orientation": details["orientation"],
                "meaning": details["meaning"],
            }
        )

    st.session_state.reading = reading

    st.session_state.phase = "tarot_result"


# ============================================================
# HOROSCOPE FUNCTIONS
# ============================================================

def generate_user_horoscope():

    name = (
        st.session_state.name
        .strip()
    )

    birthday = (
        st.session_state.birthday
    )

    if not name:

        st.session_state.error = (
            "Please enter your name."
        )

        return

    if birthday is None:

        st.session_state.error = (
            "Please enter your birthday."
        )

        return

    sign = get_zodiac_sign(
        birthday
    )

    horoscope = generate_horoscope(
        sign,
        birthday
    )

    st.session_state.zodiac = sign

    st.session_state.horoscope = horoscope

    st.session_state.phase = (
        "horoscope_result"
    )

    st.session_state.error = ""


# ============================================================
# RESET
# ============================================================

def reset_app():

    st.session_state.phase = "setup"

    st.session_state.pool = []

    st.session_state.selected = []

    st.session_state.selected_details = {}

    st.session_state.reading = []

    st.session_state.question = ""

    st.session_state.horoscope = {}

    st.session_state.zodiac = None

    st.session_state.error = ""


# ============================================================
# COPY BUTTON
# ============================================================

def render_copy_button(prompt, key):
    """Render a simple one-click clipboard button."""

    prompt_json = json.dumps(
        prompt,
        ensure_ascii=False,
    )

    component_html = f"""
    <div style="
        width:100%;
        font-family:Arial,sans-serif;
        text-align:center;
        padding:4px 0;
    ">
        <button id="copyBtn_{key}" style="
            width:100%;
            min-height:48px;
            border:0;
            border-radius:10px;
            background:linear-gradient(90deg,#745ca8,#9b78d0);
            color:white;
            font-size:16px;
            font-weight:700;
            cursor:pointer;
            padding:12px 18px;
        ">
            📋 Copy Reading
        </button>
        <div id="status_{key}" style="
            margin-top:7px;
            color:#bdb0ce;
            font-size:13px;
            min-height:18px;
        "></div>
    </div>

    <script>
    const promptText_{key} = {prompt_json};
    const button_{key} = document.getElementById("copyBtn_{key}");
    const status_{key} = document.getElementById("status_{key}");

    button_{key}.addEventListener("click", async () => {{
        let copied = false;

        try {{
            await navigator.clipboard.writeText(promptText_{key});
            copied = true;
        }} catch (e) {{
            try {{
                const textarea = document.createElement("textarea");
                textarea.value = promptText_{key};
                textarea.style.position = "fixed";
                textarea.style.left = "-9999px";
                document.body.appendChild(textarea);
                textarea.focus();
                textarea.select();
                copied = document.execCommand("copy");
                textarea.remove();
            }} catch (fallbackError) {{
                copied = false;
            }}
        }}

        status_{key}.textContent = copied
            ? "✓ Copied to clipboard. Paste it into ChatGPT."
            : "Copy was blocked by the browser. Please use the prompt below.";
    }});
    </script>
    """

    components.html(
        component_html,
        height=82,
        scrolling=False,
    )


# ============================================================
# CHATGPT TAROT PROMPT
# ============================================================

def create_tarot_chatgpt_prompt(language="English"):

    language_instruction = {
        "English": "Write the explanation in clear, natural English.",
        "Tagalog": "Write the explanation in natural, easy-to-understand Filipino/Tagalog. Keep Tarot card names and standard Tarot terms in English when appropriate.",
        "Cebuano": "Write the explanation in natural, easy-to-understand Cebuano/Bisaya. Keep Tarot card names and standard Tarot terms in English when appropriate.",
    }.get(language, "Write the explanation in clear, natural English.")

    prompt = f"""
Please explain this tarot reading in simple,
easy-to-understand language.

Preferred language: {language}

{language_instruction}

User name:
{st.session_state.name}

Birthday:
{st.session_state.birthday}

Reading category:
{st.session_state.category}

Spread:
{st.session_state.spread}

Question:
{st.session_state.question}

Please:

1. Explain each Tarot card.
2. Explain each card's position.
3. Explain whether each card is upright or reversed.
4. Explain how the cards relate to one another.
5. Explain the overall symbolic message.
6. Relate the interpretation to the user's question.
7. Give practical things the user can reflect on.
8. Keep the explanation simple and clear.
9. Do not present Tarot as a guaranteed prediction.

Tarot reading:
"""

    for card in st.session_state.reading:

        prompt += f"""

Position:
{card["position"]}

Card:
{card["name"]}

Orientation:
{card["orientation"]}

Meaning:
{card["meaning"]}
"""

    prompt += """

Please explain this in a warm,
clear and easy-to-understand way.

Separate symbolic interpretation from
established facts.
"""

    return prompt.strip()


# ============================================================
# CHATGPT HOROSCOPE PROMPT
# ============================================================

def create_horoscope_chatgpt_prompt(language="English"):

    language_instruction = {
        "English": "Write the explanation in clear, natural English.",
        "Tagalog": "Write the explanation in natural, easy-to-understand Filipino/Tagalog.",
        "Cebuano": "Write the explanation in natural, easy-to-understand Cebuano/Bisaya.",
    }.get(language, "Write the explanation in clear, natural English.")

    sign = (
        st.session_state.zodiac
    )

    horoscope = (
        st.session_state.horoscope
    )

    prompt = f"""
Please explain this horoscope in simple,
easy-to-understand language.

Preferred language: {language}

{language_instruction}

Name:
{st.session_state.name}

Birthday:
{st.session_state.birthday}

Zodiac sign:
{sign["name"]}

Zodiac description:
{sign["description"]}

Horoscope:

Career:
{horoscope["career"]}

Love & Relationships:
{horoscope["love"]}

Money:
{horoscope["money"]}

Personal Growth:
{horoscope["growth"]}

Please:

1. Explain each section in simple language.
2. Explain what the themes could mean in everyday life.
3. Give practical reflection points.
4. Clearly distinguish astrology as a symbolic/
   entertainment/reflection practice from factual certainty.
5. Do not present the horoscope as a guaranteed
   prediction of future events.
6. Keep the explanation warm and easy to understand.
"""

    return prompt.strip()


# ============================================================
# TOP BANNER
# ============================================================

banner = get_banner()

if banner:

    st.image(
        str(banner),
        use_container_width=True,
    )

else:

    st.warning(
        "Banner.png was not found. "
        "Place it at assets/tarot/Banner.png."
    )


def render_flip_card(
    card_back,
    card_image,
    card_name,
    orientation,
    number,
):
    """Render a responsive 3D flip card. The front is shown after selection."""

    back_bytes = card_back.read_bytes()
    back_b64 = base64.b64encode(back_bytes).decode("ascii")

    back_ext = card_back.suffix.lower()
    back_mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(back_ext, "image/png")

    front_bytes = card_image.read_bytes()
    front_b64 = base64.b64encode(front_bytes).decode("ascii")

    front_ext = card_image.suffix.lower()
    front_mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(front_ext, "image/jpeg")

    # Keep the artwork upright. "Reversed" is represented by the
    # orientation label/meaning rather than rotating the source artwork.
    rotation = "none"

    html = f"""
    <style>
        * {{ box-sizing: border-box; }}
        body {{ margin:0; background:transparent; }}
        .scene {{
            width:100%;
            height:300px;
            padding:4px;
            perspective:1100px;
            display:flex;
            justify-content:center;
            align-items:center;
            overflow:hidden;
        }}
        .card {{
            width:min(100%, 190px);
            aspect-ratio:2 / 3;
            height:auto;
            max-height:285px;
            position:relative;
            transform-style:preserve-3d;
            transform:rotateY(360deg);
            animation:flipIn .75s cubic-bezier(.2,.75,.2,1) both;
        }}
        .face {{
            position:absolute;
            inset:0;
            backface-visibility:hidden;
            -webkit-backface-visibility:hidden;
            border-radius:14px;
            overflow:hidden;
            border:2px solid rgba(201,168,106,.75);
            box-shadow:0 12px 30px rgba(0,0,0,.45);
            background:#120a20;
        }}
        .face img {{
            width:100%;
            height:100%;
            object-fit:cover;
            display:block;
        }}
        /* Back is the visible face before the flip. */
        .back {{ transform:rotateY(0deg); }}
        /* Tarot face is hidden on the back side until the card flips. */
        .front {{ transform:rotateY(180deg); }}
        .front img {{ transform:none; }}
        @keyframes flipIn {{
            from {{ transform:rotateY(0deg); }}
            to {{ transform:rotateY(180deg); }}
        }}
        @media (max-width:700px) {{
            .scene {{ height:235px; }}
            .card {{ width:min(100%,145px); aspect-ratio:2 / 3; height:auto; max-height:218px; }}
        }}
        @media (max-width:430px) {{
            .scene {{ height:215px; }}
            .card {{ width:min(100%,130px); aspect-ratio:2 / 3; height:auto; max-height:195px; }}
        }}
    </style>

    <div class="scene">
        <div class="card">
            <div class="face front">
                <img src="data:{front_mime};base64,{front_b64}" alt="{card_name}">
            </div>
            <div class="face back">
                <img src="data:{back_mime};base64,{back_b64}" alt="Berlin Tarot card back">
            </div>
        </div>
    </div>
    """

    components.html(
        html,
        height=315,
        scrolling=False,
    )


# ============================================================
# MODE SELECTOR
# ============================================================

if st.session_state.phase == "setup":

    mode = st.radio(
        "Choose your reading",
        [
            "🃏 Tarot Reading",
            "🌙 Horoscope",
        ],
        horizontal=True,
        index=(
            0
            if st.session_state.mode
            == "Tarot Reading"
            else 1
        ),
    )

    if mode == "🃏 Tarot Reading":

        st.session_state.mode = (
            "Tarot Reading"
        )

    else:

        st.session_state.mode = (
            "Horoscope"
        )


# ============================================================
# TAROT SETUP
# ============================================================

if (
    st.session_state.phase == "setup"
    and
    st.session_state.mode
    == "Tarot Reading"
):

    st.markdown("## 🃏 Tarot Reading")

    col1, col2 = st.columns(2)

    with col1:

        st.session_state.name = st.text_input(
            "Your name",
            value=(
                st.session_state.name
            ),
            placeholder="Enter your name",
        )

    with col2:

        st.session_state.birthday = st.date_input(
            "Your birthday",
            value=(
                st.session_state.birthday
                or date(1990, 1, 1)
            ),
            min_value=date(1900, 1, 1),
            max_value=date.today(),
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
                help="Choose how many cards you want and what each position means.",
            )
        )

    st.session_state.question = st.text_area(
        "Your question",
        value=(
            st.session_state.question
        ),
        placeholder=(
            "Example: What do I need to know "
            "about my career right now?"
        ),
        height=110,
    )

    if st.session_state.error:

        st.error(
            st.session_state.error
        )

    with st.container(border=True):

        st.markdown(
            "### 🔮 How it works"
        )

        st.write(
            "Enter your name and birthday, "
            "choose your reading category, "
            "and ask your question."
        )

        st.write(
            "The deck will shuffle and show "
            "**8 Berlin Tarot card backs**."
        )

        st.write(
            "Choose your cards personally."
        )

        st.write(
            "Your selected cards will then be "
            "revealed as actual Tarot card images."
        )

        st.write(
            "After your reading, you can copy "
            "the result into ChatGPT for a "
            "simpler interpretation."
        )

        st.markdown("**1 Card**")
        st.markdown(
            "- **Guidance** — Main symbolic message or energy to reflect on."
        )

        st.markdown("**3 Cards**")
        st.markdown(
            "- **Situation** — What is happening now\n"
            "- **Challenge** — Main obstacle or difficulty\n"
            "- **Guidance** — What to consider moving forward"
        )

        st.markdown("**5 Cards**")
        st.markdown(
            "- **Situation** — Current circumstances\n"
            "- **Challenge** — Main obstacle or tension\n"
            "- **Hidden Influence** — Something beneath the surface\n"
            "- **Advice** — Practical/reflection message\n"
            "- **Direction** — Symbolic direction going forward"
        )

        st.caption(
            "🔮 Tarot is a symbolic reflection tool. It does not guarantee or predict exactly what will happen in the future."
        )

    st.write("")

    if st.button(
        "✨ Start & Shuffle the Deck",
        type="primary",
        use_container_width=True,
    ):

        start_tarot()

        if (
            st.session_state.phase
            == "tarot_shuffle"
        ):

            st.rerun()


# ============================================================
# HOROSCOPE SETUP
# ============================================================

elif (
    st.session_state.phase == "setup"
    and
    st.session_state.mode
    == "Horoscope"
):

    st.markdown("## 🌙 Horoscope Reading")

    st.session_state.name = st.text_input(
        "Your name",
        value=(
            st.session_state.name
        ),
        placeholder="Enter your name",
    )

    st.session_state.birthday = st.date_input(
        "Your birthday",
        value=(
            st.session_state.birthday
            or date(1990, 1, 1)
        ),
        min_value=date(1900, 1, 1),
        max_value=date.today(),
    )

    if st.session_state.error:

        st.error(
            st.session_state.error
        )

    with st.container(border=True):

        st.markdown(
            "### 🌙 How it works"
        )

        st.write(
            "Enter your name and birthday."
        )

        st.write(
            "Berlin Tarot Reading will "
            "determine your zodiac sign."
        )

        st.write(
            "You will receive symbolic themes "
            "for career, love, money, and "
            "personal growth."
        )

        st.write(
            "You can then copy the result "
            "and ask ChatGPT to explain it "
            "in simpler language."
        )

    st.write("")

    if st.button(
        "🌙 Generate My Horoscope",
        type="primary",
        use_container_width=True,
    ):

        generate_user_horoscope()

        if (
            st.session_state.phase
            == "horoscope_result"
        ):

            st.rerun()


# ============================================================
# TAROT SHUFFLE ANIMATION — 3 TIMES
# ============================================================

elif (
    st.session_state.phase
    == "tarot_shuffle"
):

    st.markdown("## 🃏 Shuffling the Deck")

    st.caption(
        "The 8-card deck is shuffled 3 times before you pick your cards."
    )

    card_back = get_card_back()

    if card_back is None:

        st.error(
            "Berlin card-back image was not found."
        )

    else:

        status = st.empty()
        deck_area = st.empty()

        # Exactly three visible shuffle passes.
        for shuffle_number in range(1, 4):

            random.shuffle(st.session_state.pool)

            status.markdown(
                f"### 🔄 Shuffle {shuffle_number} / 3"
            )

            with deck_area.container():

                for row_start in range(0, 8, 4):

                    row = st.session_state.pool[
                        row_start:row_start + 4
                    ]

                    columns = st.columns(4, gap="small")

                    for position, (column, _card_index) in enumerate(
                        zip(columns, row),
                        start=row_start + 1,
                    ):

                        with column:

                            st.image(
                                str(card_back),
                                use_container_width=True,
                            )

                            st.caption(
                                f"Card {position}"
                            )

            # Pause so users can actually see each shuffle.
            time.sleep(0.65)

        status.markdown(
            "### ✨ Shuffle complete — choose your cards"
        )

        time.sleep(0.25)

        st.session_state.selected = []
        st.session_state.selected_details = {}
        st.session_state.reading = []
        st.session_state.phase = "tarot_select"

        st.rerun()


# ============================================================
# TAROT CARD SELECTION
# ============================================================

elif (
    st.session_state.phase
    == "tarot_select"
):

    required_cards = len(
        SPREADS[
            st.session_state.spread
        ]
    )

    selected_cards = len(
        st.session_state.selected
    )

    st.markdown("## 2. Pick your cards")

    st.write(
        f"Choose {required_cards} "
        f"{'card' if required_cards == 1 else 'cards'} "
        "from the 8 Berlin cards."
    )

    st.caption(
        f"Selected: {selected_cards} / {required_cards}"
    )

    card_back = get_card_back()

    if card_back is None:

        st.error(
            "Berlin card-back image was not found."
        )

        st.info(
            "Place it here:\n\n"
            "assets/tarot/berlin-card-back.png"
        )

    pool = (
        st.session_state.pool
    )

    columns = st.columns(
        8,
        gap="small",
    )

    for number, (
        column,
        card_index
    ) in enumerate(
        zip(
            columns,
            pool
        ),
        start=1,
    ):

        with column:

            selected = (
                card_index
                in st.session_state.selected
            )

            if selected:

                details = st.session_state.selected_details.get(
                    card_index
                )

                card_image = (
                    get_card_image(details["name"])
                    if details
                    else None
                )

                if card_back and card_image and details:

                    render_flip_card(
                        card_back,
                        card_image,
                        details["name"],
                        details["orientation"],
                        number,
                    )

                elif card_back:

                    st.image(
                        str(card_back),
                        use_container_width=True,
                    )

                st.caption(
                    f"Card {number} • {details['orientation']}"
                    if details
                    else f"Card {number}"
                )

            else:

                if card_back:

                    st.image(
                        str(card_back),
                        use_container_width=True,
                    )

                else:

                    st.warning(
                        "Berlin card-back image not found."
                    )

                st.caption(
                    f"Card {number} • Face-down"
                )

            button_text = (
                "↩ Unpick"
                if selected
                else "🃏 Pick"
            )

            if st.button(
                button_text,
                key=f"card_{card_index}",
                use_container_width=True,
            ):

                toggle_card(
                    card_index
                )

                st.rerun()

    st.write("")

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

            reveal_tarot()

            st.rerun()

    with col2:

        if st.button(
            "↻ Reshuffle 8 Cards",
            use_container_width=True,
        ):

            st.session_state.pool = (
                random.sample(
                    range(len(DECK)),
                    min(
                        8,
                        len(DECK)
                    ),
                )
            )

            st.session_state.selected = []

            st.session_state.selected_details = {}

            st.rerun()


# ============================================================
# TAROT RESULT
# ============================================================

elif (
    st.session_state.phase
    == "tarot_result"
):

    st.markdown("## 🔮 Your Tarot Reading")

    st.write(
        f"**Name:** "
        f"{st.session_state.name}"
    )

    st.write(
        f"**Birthday:** "
        f"{st.session_state.birthday}"
    )

    st.write(
        f"**Category:** "
        f"{st.session_state.category}"
    )

    st.write(
        f"**Question:** "
        f"{st.session_state.question}"
    )

    st.write("")

    cards = st.session_state.reading

    # Keep the original 8-card deck positions.
    # Selected cards are revealed in their original position;
    # unselected cards remain face-down.
    revealed_by_index = {
        card["pool_index"]: card
        for card in cards
    }

    pool = st.session_state.pool

    st.markdown("### 🃏 Your selected cards")
    st.caption("Your selected cards have been flipped in place. The other cards remain face-down.")

    # Desktop: 8 columns. Streamlit automatically wraps on smaller screens.
    columns = st.columns(8, gap="small")

    for number, (column, card_index) in enumerate(
        zip(columns, pool),
        start=1,
    ):

        with column:

            revealed = card_index in revealed_by_index

            if revealed:

                card = revealed_by_index[card_index]
                image_path = get_card_image(card["name"])

                with st.container(border=True):

                    st.caption(f"Card {number}")

                    if image_path:

                        # Always show the physical Tarot artwork upright.
                        # Reversed is indicated by the orientation label and
                        # uses the reversed meaning from the deck data.
                        st.image(
                            str(image_path),
                            use_container_width=True,
                        )

                    else:

                        st.error(
                            f"Image not found for {card['name']}"
                        )

                    st.markdown(
                        f"**{card['name']}**"
                    )

                    st.caption(
                        f"✦ {card['orientation']} ✦"
                    )

            else:

                with st.container(border=True):

                    st.caption(f"Card {number}")

                    if card_back := get_card_back():

                        st.image(
                            str(card_back),
                            use_container_width=True,
                        )

                    else:

                        st.warning(
                            "Card back not found."
                        )

                    st.caption("Face-down")

    # ========================================================
    # INTERPRETATION
    # ========================================================

    st.divider()

    st.markdown(
        "### 🔮 Interpretation"
    )

    if (
        st.session_state.category
        == "🔮 Future"
    ):

        st.info(
            "This Future reading is presented "
            "as symbolic themes and possibilities, "
            "not as a guaranteed prediction."
        )

    else:

        st.info(
            "Use the cards as symbolic prompts "
            "for reflection and decision-making."
        )

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
    # CHATGPT
    # ========================================================

    st.divider()

    st.markdown("### 💬 Explain this with ChatGPT")

    st.write(
        "Click the button to copy the complete reading, "
        "then paste it into ChatGPT. 🤖"
    )

    tarot_language = st.selectbox(
        "🌐 ChatGPT explanation language",
        ["English", "Tagalog", "Cebuano"],
        key="tarot_chatgpt_language",
    )

    tarot_prompt = create_tarot_chatgpt_prompt(
        tarot_language
    )

    render_copy_button(
        tarot_prompt,
        f"tarot_{tarot_language.lower()}",
    )

    with st.expander("👁️ View the prompt before copying"):

        st.code(
            tarot_prompt,
            language="text",
        )

    st.caption(
        "Copied to your clipboard. Paste it into ChatGPT when ready."
    )

    st.divider()

    if st.button(
        "🔄 Start a New Reading",
        type="primary",
        use_container_width=True,
    ):

        reset_app()

        st.rerun()


# ============================================================
# HOROSCOPE RESULT
# ============================================================

elif (
    st.session_state.phase
    == "horoscope_result"
):

    sign = (
        st.session_state.zodiac
    )

    horoscope = (
        st.session_state.horoscope
    )

    st.markdown("## 🌙 Your Horoscope")

    st.write(
        f"**Name:** "
        f"{st.session_state.name}"
    )

    st.write(
        f"**Birthday:** "
        f"{st.session_state.birthday}"
    )

    # ========================================================
    # ZODIAC CARD
    # ========================================================

    with st.container(border=True):

        st.markdown(
            f"## {sign['symbol']} {sign['name']}"
        )

        st.write(
            sign["description"]
        )

    # HOROSCOPE SECTIONS
    # ========================================================

    section_order = [
        "career",
        "love",
        "money",
        "growth",
    ]

    for category in section_order:

        data = (
            HOROSCOPE_THEMES[
                category
            ]
        )

        with st.container(border=True):

            st.markdown(
                f"### {data['title']}"
            )

            st.write(
                horoscope[category]
            )

    # ========================================================
    # REFLECTION
    # ========================================================

    st.info(
        "🌙 This horoscope is a symbolic "
        "reflection tool. It is not a guaranteed "
        "prediction of future events."
    )

    # ========================================================
    # CHATGPT
    # ========================================================

    st.divider()

    st.markdown("### 💬 Explain this with ChatGPT")

    st.write(
        "Click the button to copy the complete reading, "
        "then paste it into ChatGPT. 🤖"
    )

    horoscope_language = st.selectbox(
        "🌐 ChatGPT explanation language",
        ["English", "Tagalog", "Cebuano"],
        key="horoscope_chatgpt_language",
    )

    horoscope_prompt = create_horoscope_chatgpt_prompt(
        horoscope_language
    )

    render_copy_button(
        horoscope_prompt,
        f"horoscope_{horoscope_language.lower()}",
    )

    with st.expander("👁️ View the prompt before copying"):

        st.code(
            horoscope_prompt,
            language="text",
        )

    st.caption(
        "Copied to your clipboard. Paste it into ChatGPT when ready."
    )

    st.divider()

    if st.button(
        "🔄 Start a New Reading",
        type="primary",
        use_container_width=True,
    ):

        reset_app()

        st.rerun()
