import base64
import json
import random
import re
from datetime import date, datetime
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

    padding-top: 1.5rem;
    padding-bottom: 3rem;
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

@media (max-width: 900px) {

    .hero h1 {

        font-size:
            2.2rem;
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

    st.session_state.reading = []

    st.session_state.phase = "tarot_select"

    st.session_state.error = ""


def toggle_card(card_index):

    maximum_cards = len(
        SPREADS[
            st.session_state.spread
        ]
    )

    if card_index in st.session_state.selected:

        st.session_state.selected.remove(
            card_index
        )

        return

    if (
        len(st.session_state.selected)
        < maximum_cards
    ):

        st.session_state.selected.append(
            card_index
        )


def reveal_tarot():

    positions = SPREADS[
        st.session_state.spread
    ]

    reading = []

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

        reading.append(
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

    st.session_state.reading = []

    st.session_state.question = ""

    st.session_state.horoscope = {}

    st.session_state.zodiac = None

    st.session_state.error = ""


# ============================================================
# CHATGPT TAROT PROMPT
# ============================================================

def create_tarot_chatgpt_prompt():

    prompt = f"""
Please explain this tarot reading in simple,
easy-to-understand language.

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

def create_horoscope_chatgpt_prompt():

    sign = (
        st.session_state.zodiac
    )

    horoscope = (
        st.session_state.horoscope
    )

    prompt = f"""
Please explain this horoscope in simple,
easy-to-understand language.

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
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">

        <h1>🔮 Berlin Tarot Reading</h1>

        <div class="hero-subtitle">
            Tarot • Horoscope • Reflection • Guidance
        </div>

    </div>
    """,
    unsafe_allow_html=True,
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

    st.markdown(
        '<div class="section-title">'
        '🃏 Tarot Reading'
        '</div>',
        unsafe_allow_html=True,
    )

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

    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )

    if st.button(
        "✨ Start & Shuffle the Deck",
        type="primary",
        use_container_width=True,
    ):

        start_tarot()

        if (
            st.session_state.phase
            == "tarot_select"
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

    st.markdown(
        '<div class="section-title">'
        '🌙 Horoscope Reading'
        '</div>',
        unsafe_allow_html=True,
    )

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

    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )

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

    st.markdown(
        '<div class="section-title">'
        '2. Pick your cards'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="selection-title">

            Choose {required_cards}
            {"card" if required_cards == 1 else "cards"}
            from the 8 Berlin cards

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="selection-subtitle">

            Selected:
            <strong>
                {selected_cards} / {required_cards}
            </strong>

        </div>
        """,
        unsafe_allow_html=True,
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

            wrapper_class = (
                "selected-wrapper"
                if selected
                else "card-back-wrapper"
            )

            st.markdown(
                f'<div class="{wrapper_class}">',
                unsafe_allow_html=True,
            )

            if card_back:

                st.image(
                    str(card_back),
                    use_container_width=True,
                )

            else:

                st.markdown(
                    """
                    <div style="
                        height:220px;
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
                    CARD {number}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

            button_text = (
                "✓ Selected"
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

    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )

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

            st.rerun()


# ============================================================
# TAROT RESULT
# ============================================================

elif (
    st.session_state.phase
    == "tarot_result"
):

    st.markdown(
        '<div class="section-title">'
        '🔮 Your Tarot Reading'
        '</div>',
        unsafe_allow_html=True,
    )

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

    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )

    cards = (
        st.session_state.reading
    )

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

                </div>
                """,
                unsafe_allow_html=True,
            )

            if image_path:

                if (
                    card["orientation"]
                    == "Reversed"
                ):

                    image_bytes = (
                        image_path.read_bytes()
                    )

                    encoded_image = (
                        base64.b64encode(
                            image_bytes
                        ).decode(
                            "utf-8"
                        )
                    )

                    extension = (
                        image_path.suffix.lower()
                    )

                    if extension == ".png":

                        mime_type = "image/png"

                    elif extension in (
                        ".jpg",
                        ".jpeg",
                    ):

                        mime_type = "image/jpeg"

                    else:

                        mime_type = "image/webp"

                    st.markdown(
                        f"""
                        <div style="
                            display:flex;
                            justify-content:center;
                            margin:10px auto;
                        ">

                            <img
                                src="data:{mime_type};base64,{encoded_image}"
                                style="
                                    width:100%;
                                    max-width:280px;
                                    border-radius:12px;
                                    border:3px solid #c9a86a;
                                    box-shadow:
                                        0 15px 40px
                                        rgba(0,0,0,.55);
                                    transform:
                                        rotate(180deg);
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
                    f"{card['name']}"
                )

            st.markdown(
                f"""
                <div style="
                    text-align:center;
                ">

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

            st.markdown(
                f"""
                <div class="meaning">
                    {card["meaning"]}
                </div>
                """,
                unsafe_allow_html=True,
            )

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

    st.markdown(
        "### 💬 How to interpret this with ChatGPT"
    )

    st.write(
        "Copy the text below, open ChatGPT, "
        "paste it, and send it."
    )

    with st.container(border=True):

        st.markdown(
            "#### 🤖 Steps"
        )

        st.write(
            "1️⃣ Click inside the box below."
        )

        st.write(
            "2️⃣ Press **Ctrl+A**."
        )

        st.write(
            "3️⃣ Press **Ctrl+C**."
        )

        st.write(
            "4️⃣ Open ChatGPT."
        )

        st.write(
            "5️⃣ Press **Ctrl+V**."
        )

        st.write(
            "6️⃣ Send the message."
        )

    tarot_prompt = (
        create_tarot_chatgpt_prompt()
    )

    st.text_area(
        "📋 Copy-ready ChatGPT prompt",
        value=tarot_prompt,
        height=400,
    )

    st.info(
        "ChatGPT can simplify the symbolic "
        "interpretation, but Tarot should not "
        "be treated as a guaranteed prediction."
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

    st.markdown(
        '<div class="section-title">'
        '🌙 Your Horoscope'
        '</div>',
        unsafe_allow_html=True,
    )

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

    st.markdown(
        f"""
        <div class="zodiac-card">

            <div class="zodiac-symbol">
                {sign["symbol"]}
            </div>

            <div class="zodiac-name">
                {sign["name"]}
            </div>

            <div class="zodiac-description">
                {sign["description"]}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # ========================================================
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

        st.markdown(
            f"""
            <div class="horoscope-section">

                <h3>
                    {data["title"]}
                </h3>

                <p>
                    {horoscope[category]}
                </p>

            </div>
            """,
            unsafe_allow_html=True,
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

    st.markdown(
        "### 💬 How to interpret this with ChatGPT"
    )

    st.write(
        "Copy the horoscope below, open ChatGPT, "
        "paste it, and ask ChatGPT to explain "
        "it in simple language."
    )

    with st.container(border=True):

        st.markdown(
            "#### 🤖 Steps"
        )

        st.write(
            "1️⃣ Click inside the box."
        )

        st.write(
            "2️⃣ Press **Ctrl+A**."
        )

        st.write(
            "3️⃣ Press **Ctrl+C**."
        )

        st.write(
            "4️⃣ Open ChatGPT."
        )

        st.write(
            "5️⃣ Press **Ctrl+V**."
        )

        st.write(
            "6️⃣ Send the message."
        )

    horoscope_prompt = (
        create_horoscope_chatgpt_prompt()
    )

    st.text_area(
        "📋 Copy-ready ChatGPT prompt",
        value=horoscope_prompt,
        height=400,
    )

    st.info(
        "ChatGPT can explain the symbolic "
        "themes in simpler language."
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
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div class="footer">

        🔮 Berlin Tarot Reading

        <br><br>

        Tarot and horoscope content are presented
        as symbolic reflection and entertainment,
        not as guaranteed predictions.

    </div>
    """,
    unsafe_allow_html=True,
)