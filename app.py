import streamlit as st
from dungeon.engine import init_game_state, reset_game, advance_challenge, use_hint
from dungeon.levels import DUNGEON_LEVELS
from dungeon.dm import list_models, preferred_model, query_dungeon_master

st.set_page_config(
    page_title="DeadLock",
    page_icon="🦇",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Crimson+Pro:ital,wght@0,400;0,600;1,400&display=swap');

    .stApp {
        color: #f0e4d4;
        background:
            radial-gradient(ellipse at 50% -10%, rgba(90, 18, 28, 0.45), transparent 46%),
            radial-gradient(ellipse at 50% 120%, rgba(20, 8, 12, 0.9), transparent 50%),
            #0a090b;
    }
    .stApp::before {
        content: "";
        pointer-events: none;
        position: fixed;
        inset: 0;
        box-shadow: inset 0 0 140px 30px rgba(0, 0, 0, 0.72);
        z-index: 0;
    }
    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 3rem;
        max-width: 720px;
        font-family: "Crimson Pro", Georgia, serif;
    }
    header[data-testid="stHeader"], footer, [data-testid="stToolbar"] { display: none; }
    .crypt-title {
        font-family: Cinzel, Georgia, serif;
        font-size: 2rem;
        letter-spacing: 0.08em;
        color: #f3e2c4;
        text-shadow: 0 0 18px rgba(180, 40, 40, 0.45);
        margin: 0;
        animation: candle 4.5s ease-in-out infinite;
    }
    .gate {
        text-align: center;
        padding-top: 16vh;
    }
    .gate .crypt-title {
        font-size: 4rem;
        letter-spacing: 0.16em;
    }
    .gate .crypt-sub {
        margin-top: 0.6rem;
        font-size: 1.15rem;
    }
    @keyframes candle {
        0%, 100% { opacity: 1; }
        48% { opacity: 0.88; }
        52% { opacity: 1; }
        70% { opacity: 0.82; }
    }
    h3, [data-testid="stHeading"] h3 {
        font-family: Cinzel, Georgia, serif;
        color: #f4ead8;
        font-weight: 600;
    }
    .outcome {
        margin-top: 1rem;
        padding: 0.85rem 1rem;
        border: 1px solid #5c3b34;
        background: #16110f;
        font-family: Cinzel, Georgia, serif;
        letter-spacing: 0.04em;
    }
    .outcome span {
        display: block;
        font-size: 1.6rem;
        margin-bottom: 0.2rem;
    }
    .outcome.treat span { color: #e7c27a; }
    .outcome.trick span { color: #e07070; }
    .outcome p { margin: 0; font-family: "Crimson Pro", Georgia, serif; letter-spacing: 0; }
    p, li, label, .stMarkdown { color: #eadfce; }
    [data-testid="stCaptionContainer"] { color: #a89888; }
    textarea, [data-testid="stTextArea"] textarea {
        background: #120e0e !important;
        color: #d7f5c4 !important;
        border: 1px solid #4a2c2c !important;
        border-radius: 6px !important;
        font-family: Consolas, "Courier New", monospace !important;
        box-shadow: inset 0 0 28px rgba(80, 12, 18, 0.45);
    }
    .stButton > button {
        font-family: Cinzel, Georgia, serif;
        letter-spacing: 0.04em;
        border-radius: 4px;
        background: transparent;
        color: #f0e4d4;
        border: 1px solid #6d5348;
    }
    .stButton > button[kind="primary"] {
        background: #6e1824;
        border-color: #c45a5a;
        color: #fff4ec;
    }
    .stButton > button:hover {
        border-color: #e7b2a4;
        color: #fff;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #5a1018, #c4373f);
    }
    [data-testid="stAlert"] {
        background: #16110f;
        color: #f3e6d6;
        border: 1px solid #5c3b34;
    }
    [data-testid="stPopover"] button, [data-testid="stDialog"] {
        background: #120e0e;
        color: #f0e4d4;
    }
    </style>
""", unsafe_allow_html=True)

@st.dialog("How to play")
def show_how_to_play():
    st.markdown(
        """
There are 5 levels, and each level has 2 challenges. You fix small AI-engineering tasks: prompts, sampling, context windows, retrieval, and evals.

**How scoring works**
- Each level is worth 10 points. You get those points when you clear both challenges.
- A correct fix is a **treat**. A wrong fix is a **trick**: you stay on the same challenge.
- A perfect run, with no hints, is 50. Your score stays at the top.

**Hints**
You get 2 hints for the whole game. Using one costs 5 points. When they are gone, the button stops.
        """
    )

if not st.session_state.get("started"):
    st.markdown(
        '<div class="gate">'
        '<h1 class="crypt-title">DeadLock</h1>'
        '<p class="crypt-sub">Five rooms. The lights do not come back on.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    _, start_col, _ = st.columns([1, 1, 1])
    with start_col:
        if st.button("Start", type="primary", use_container_width=True):
            st.session_state.started = True
            st.rerun()
    st.stop()

init_game_state()
state = st.session_state.game_state
level_count = len(DUNGEON_LEVELS)

title_col, help_col = st.columns([5, 1.4], vertical_alignment="center")
with title_col:
    st.markdown(
        '<h1 class="crypt-title">DeadLock</h1>'
        '<p class="crypt-sub">The server room keeps the lights low.</p>',
        unsafe_allow_html=True,
    )
with help_col:
    if st.button("How to play", use_container_width=True):
        show_how_to_play()

model_choices = list_models()
model_name = model_choices[preferred_model(model_choices)]

st.caption(f"Score  {state['score']}    ·    Hints  {state['hints_left']} left")

if state["current_level"] >= level_count:
    banner = st.session_state.pop("dm_banner", None)
    if banner and banner["kind"] == "treat":
        st.markdown(
            f'<div class="outcome treat"><span>Treat 🍫</span><p>{banner["text"]}</p></div>',
            unsafe_allow_html=True,
        )
    st.success(f"You cleared all {level_count} levels. Final score: {state['score']}.")
    if st.button("Play again"):
        reset_game()
        st.rerun()
    st.stop()

level = DUNGEON_LEVELS[state["current_level"]]
challenge = level["challenges"][state["current_challenge"]]

st.subheader(level["name"])
st.write(level["description"])

user_code = st.text_area(
    "Patch",
    value=challenge["starter_code"],
    height=220,
    key=f"ai_code_{state['current_level']}_{state['current_challenge']}",
    label_visibility="collapsed",
)

attack_col, hint_col = st.columns(2)
with attack_col:
    compile_btn = st.button("Compile and attack", type="primary", use_container_width=True)
with hint_col:
    hints_left = state["hints_left"]
    hint_label = "No hints left" if hints_left == 0 else f"Hint ({hints_left} left)"
    hint_btn = st.button(hint_label, use_container_width=True, disabled=hints_left == 0)

if compile_btn:
    with st.spinner("Testing the patch..."):
        if challenge["validate"](user_code):
            finished_level = advance_challenge()
            st.session_state.dm_banner = {
                "kind": "treat",
                "text": "+10 points." if finished_level else "Clear the other challenge to earn 10 points.",
            }
            st.rerun()
        else:
            st.session_state.dm_banner = {
                "kind": "trick",
                "text": "No points. The door stays shut.",
            }
            st.rerun()

if hint_btn and state["hints_left"] > 0:
    with st.spinner("Listening..."):
        hint = query_dungeon_master(
            f"Give a subtle, spooky hint for this coding puzzle against the {level['monster']}:\n{challenge['task']}\n```python\n{challenge['starter_code']}\n```",
            model_name,
        )
        use_hint()
        st.session_state.dm_banner = {"kind": "hint", "text": f"{hint}\n\nHint used. −5 points."}
        st.rerun()

banner = st.session_state.pop("dm_banner", None)
if banner and banner["kind"] == "treat":
    st.markdown(f'<div class="outcome treat"><span>Treat 🍫</span><p>{banner["text"]}</p></div>', unsafe_allow_html=True)
elif banner and banner["kind"] == "trick":
    st.markdown(f'<div class="outcome trick"><span>Trick</span><p>{banner["text"]}</p></div>', unsafe_allow_html=True)
elif banner:
    st.info(banner["text"])
