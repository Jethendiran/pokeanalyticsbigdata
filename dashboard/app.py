import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
from pathlib import Path

from dashboard.theme import apply_theme

API_URL = "http://127.0.0.1:8001"

st.set_page_config(
    page_title="PokéAnalytics",
    page_icon="⚡",
    layout="wide"
)

apply_theme()

@st.cache_data(ttl=30)
def fetch_api(endpoint):
    session = requests.Session()
    session.trust_env = False
    url = f"{API_URL}/{endpoint.lstrip('/')}"
    response = session.get(url, timeout=20)
    response.raise_for_status()
    return response.json()


# Load live data
try:
    analytics = fetch_api("analytics")
    cards = fetch_api("cards?limit=200")
    battles = fetch_api("battles?limit=100")

except requests.RequestException as error:
    st.error(f"Cannot connect to PokéAnalytics API: {error}")
    st.stop()

except (KeyError, ValueError, TypeError) as error:
    st.error(f"Unexpected API response: {error}")
    st.stop()


card_df = pd.DataFrame(cards)
battle_df = pd.DataFrame(battles)

# Load local card categories and artwork
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = PROJECT_ROOT / "data" / "processed" / "card_catalog.json"

with CATALOG_PATH.open("r", encoding="utf-8") as file:
    local_catalog = json.load(file)

catalog_df = pd.DataFrame(local_catalog)[["id", "category", "artwork"]]
card_df["id"] = card_df["id"].astype(str)
catalog_df["id"] = catalog_df["id"].astype(str)
card_df = card_df.merge(catalog_df, on="id", how="left")


# Sidebar navigation
with st.sidebar:
    st.title("⚡ PokéAnalytics")
    st.caption("BIG DATA ANALYTICS")

    st.divider()

    page = st.radio(
        "MAIN MENU",
        [
            "Overview",
            "Card Explorer",
            "Battle Explorer",
            "Advanced Analytics"
        ],
        index=0
    )

    st.divider()

    st.markdown("### System Status")
    st.success("API Connected")
    st.success("Firebase Connected")

    st.divider()

    st.caption("Powered by Rust · Python · FastAPI · Firebase")


# Page 1: Overview
if page == "Overview":

    st.title("⚡ PokéAnalytics")
    st.caption("Pokémon TCG — Big Data Analytics Platform")

    st.success("Connected to PokéAnalytics API and Firebase Firestore")

    st.header("Battle Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Battles",
        f"{analytics['total_battles']:,}"
    )

    col2.metric(
        "Unique Cards",
        f"{len(card_df):,}"
    )

    col3.metric(
        "Agent 0 Win Rate",
        f"{analytics['agent_0_win_rate']:.2f}%"
    )

    col4.metric(
        "Agent 1 Win Rate",
        f"{analytics['agent_1_win_rate']:.2f}%"
    )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Battle Outcomes")

        outcome_data = pd.DataFrame({
            "Outcome": [
                "Agent 0 Wins",
                "Agent 1 Wins",
                "Draws",
                "Incomplete"
            ],
            "Battles": [
                analytics["agent_0_wins"],
                analytics["agent_1_wins"],
                analytics["draws"],
                analytics["incomplete_battles"]
            ]
        })

        fig = px.pie(
            outcome_data,
            names="Outcome",
            values="Battles",
            hole=0.48
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(fig, width="stretch")

    with right:
        st.subheader("Battle Performance")

        performance_data = pd.DataFrame({
            "Metric": ["Average Steps", "Average Events"],
            "Value": [
                analytics["average_steps_per_battle"],
                analytics["average_events_per_battle"]
            ]
        })

        fig = px.bar(
            performance_data,
            x="Metric",
            y="Value",
            text_auto=".2f"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(fig, width="stretch")


# Page 2: Card Explorer
elif page == "Card Explorer":

    st.title("?? Pok?mon TCG Card Explorer")
    st.caption("Explore your card collection with real TCG artwork")

    col1, col2 = st.columns(2)
    col1.metric("Total Card Records", len(card_df))
    col2.metric("Cards With Artwork", int(card_df["artwork"].notna().sum()))

    st.divider()

    filter_col, search_col = st.columns([1, 2])

    with filter_col:
        category_filter = st.selectbox(
            "Filter by category",
            ["All", "Pokemon", "Energy", "Trainer", "Stadium"]
        )

    with search_col:
        search = st.text_input(
            "Search cards",
            placeholder="Example: Pikachu, Charizard, Energy..."
        )

    filtered_cards = card_df.copy()

    if category_filter != "All":
        filtered_cards = filtered_cards[
            filtered_cards["category"] == category_filter
        ]

    if search:
        filtered_cards = filtered_cards[
            filtered_cards["name"].fillna("").astype(str).str.contains(
                search, case=False, na=False, regex=False
            )
        ]

    st.write(f"Showing {len(filtered_cards)} matching cards")
    st.divider()

    if filtered_cards.empty:
        st.warning("No matching cards found.")
    else:
        cards_per_row = 3

        for row_start in range(0, len(filtered_cards), cards_per_row):
            columns = st.columns(cards_per_row)

            for index, (_, card) in enumerate(
                filtered_cards.iloc[row_start:row_start + cards_per_row].iterrows()
            ):
                with columns[index]:
                    with st.container(border=True):
                        artwork = card.get("artwork")

                        image_path = (
                            PROJECT_ROOT / artwork
                            if isinstance(artwork, str) and artwork
                            else None
                        )

                        if image_path and image_path.is_file():
                            st.image(str(image_path), width=220)
                        else:
                            st.markdown(
                                "<div style='font-size:75px;text-align:center;padding:35px 0;'>??</div>",
                                unsafe_allow_html=True
                            )

                        st.subheader(str(card.get("name", "Unknown Card")))
                        st.caption(f"Category: {card.get('category', 'Unknown')}")
                        st.caption(f"Card ID: {card.get('id', 'N/A')}")
                        st.caption(f"Document ID: {card.get('document_id', 'N/A')}")

    st.divider()
    st.caption("Pok?Analytics ? Card collection powered by TCGdex artwork")


# Page 3: Battle Explorer
elif page == "Battle Explorer":

    st.title("⚔️ Battle Explorer")
    st.caption("Inspect individual battle records")

    st.metric("Battle Records Loaded", len(battle_df))

    if not battle_df.empty:

        if "battle_outcome" in battle_df.columns:

            outcomes = ["All"] + sorted(
                battle_df["battle_outcome"].dropna().unique().tolist()
            )

            selected = st.selectbox(
                "Filter by battle outcome",
                outcomes
            )

            filtered_battles = battle_df.copy()

            if selected != "All":
                filtered_battles = filtered_battles[
                    filtered_battles["battle_outcome"] == selected
                ]

        else:
            filtered_battles = battle_df

        st.write(f"Showing {len(filtered_battles)} battle records")

        st.dataframe(
            filtered_battles,
            width="stretch",
            hide_index=True
        )

    else:
        st.info("No battle records are available.")


# Page 4: Advanced Analytics
elif page == "Advanced Analytics":

    st.title("📊 Advanced Analytics")
    st.caption("Detailed performance indicators from the analytics collection")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Total Events",
            f"{analytics['total_events']:,}"
        )

        st.metric(
            "Average Steps per Battle",
            f"{analytics['average_steps_per_battle']:.2f}"
        )

    with col2:
        st.metric(
            "Average Events per Battle",
            f"{analytics['average_events_per_battle']:.2f}"
        )

        st.metric(
            "Decisive Battles",
            f"{analytics['decisive_battles']:,}"
        )

    st.divider()

    st.subheader("Agent Win Rate Comparison")

    win_rate_data = pd.DataFrame({
        "Agent": ["Agent 0", "Agent 1"],
        "Win Rate": [
            analytics["agent_0_win_rate"],
            analytics["agent_1_win_rate"]
        ]
    })

    fig = px.bar(
        win_rate_data,
        x="Agent",
        y="Win Rate",
        text_auto=".2f"
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Win Rate (%)"
    )

    st.plotly_chart(fig, width="stretch")

    st.divider()

    st.subheader("Analytics Summary")

    summary = pd.DataFrame({
        "Metric": [
            "Total Battles",
            "Agent 0 Wins",
            "Agent 1 Wins",
            "Draws",
            "Incomplete Battles",
            "Total Events"
        ],
        "Value": [
            analytics["total_battles"],
            analytics["agent_0_wins"],
            analytics["agent_1_wins"],
            analytics["draws"],
            analytics["incomplete_battles"],
            analytics["total_events"]
        ]
    })

    st.dataframe(summary, width="stretch", hide_index=True)


st.divider()

st.caption(
    "PokéAnalytics | Rust Processing | Python Analytics | "
    "FastAPI Backend | Firebase Firestore"
)

