import base64
from pathlib import Path
import streamlit as st

ASSETS = Path(__file__).parent / "assets" / "characters"

def encode_image(filename):
    path = ASSETS / filename
    if not path.exists():
        return ""
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def apply_theme():
    characters = {
        "charizard": encode_image("charizard.png"),
        "gengar": encode_image("gengar.png"),
        "pikachu": encode_image("pikachu.png"),
        "mewtwo": encode_image("mewtwo.png"),
        "lucario": encode_image("lucario.png"),
    }

    css = """
    <style>
    .stApp {
        background:
            radial-gradient(ellipse at 50% 20%, #142B4B, transparent 65%),
            linear-gradient(135deg, #080F20, #10182D);
        color: #E2E8F0;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #0D172A !important;
        border-right: 1px solid #285078;
        min-width: 260px;
    }

    [data-testid="stSidebar"] * {
        color: #E2E8F0;
    }

    [data-testid="stSidebar"] label {
        color: #E2E8F0 !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #A8BCD4;
    }

    /* Main dashboard: remove the extra width restriction */
    [data-testid="stMainBlockContainer"] {
        position: relative;
        z-index: 2;
        width: 100% !important;
        max-width: 1450px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding: 2rem !important;
        background: rgba(8, 15, 32, 0.88);
        border: 1px solid rgba(56, 189, 248, 0.22);
        border-radius: 18px;
        box-shadow: 0 0 35px rgba(0, 120, 255, 0.10);
    }

    /* Character illustrations */
    .poke-art {
        position: fixed;
        z-index: 1;
        width: 95px;
        height: 145px;
        object-fit: contain;
        pointer-events: none;
        filter: drop-shadow(0 0 12px rgba(56, 189, 248, 0.25));
    }

    .charizard { top: 3%; left: 5px; }
    .gengar { top: 34%; left: 5px; }
    .pikachu { bottom: 1%; left: 5px; }
    .mewtwo { top: 12%; right: 8px; }
    .lucario { bottom: 3%; right: 8px; }

    /* KPI cards */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #172B46, #102039);
        border: 1px solid #285078;
        padding: 15px 12px;
        border-radius: 14px;
        min-width: 0;
    }

    [data-testid="stMetricLabel"] {
        color: #A8BCD4 !important;
        font-size: 0.88rem !important;
    }

    [data-testid="stMetricValue"] {
        color: #38BDF8 !important;
        font-size: clamp(1.3rem, 2vw, 2.2rem) !important;
    }

    h1, h2, h3 {
        color: #F8FAFC !important;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #29415F;
        border-radius: 12px;
    }

    footer {
        visibility: hidden;
    }

    @media (max-width: 1100px) {
        .poke-art {
            display: none;
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 100% !important;
            padding: 1rem !important;
        }
    }
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)

    image_elements = []

    for name, encoded in characters.items():
        if encoded:
            image_elements.append(
                f'<img class="poke-art {name}" '
                f'src="data:image/png;base64,{encoded}">'
            )

    st.markdown("\n".join(image_elements), unsafe_allow_html=True)

