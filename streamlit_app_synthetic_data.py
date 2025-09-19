import streamlit as st
import re
import base64
from PIL import Image
from io import BytesIO
import pandas as pd
import numpy as np
import io
import os
from typing import List, Tuple, Dict, Any
import plotly.graph_objects as go
from vector_store import build_vector_store, query_vector_store, generate_answer_from_docs
from collections import OrderedDict
from typing import Optional


def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded}"


# Inject background image
def set_background(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    css_code = f"""
    <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
    </style>
    """
    st.markdown(css_code, unsafe_allow_html=True)


# Call function early in your script
set_background("artistic-blurry-colorful-wallpaper-background.jpg")

# INFO STUFF
# INFO TAB
# 🔑 Initialize session state
if "show_info_tab1" not in st.session_state:
    st.session_state["show_info_tab1"] = False

# INFO TAB 2
# 🔑 Initialize session state
if "show_info_tab2" not in st.session_state:
    st.session_state["show_info_tab2"] = False

# INFO TAB 3
# 🔑 Initialize session state
if "show_info_tab3" not in st.session_state:
    st.session_state["show_info_tab3"] = False


def toggle_info_tab1():
    st.session_state["show_info_tab1"] = not st.session_state["show_info_tab1"]


def toggle_info_tab2():
    st.session_state["show_info_tab2"] = not st.session_state["show_info_tab2"]


def toggle_info_tab3():
    st.session_state["show_info_tab3"] = not st.session_state["show_info_tab3"]


# 🔁 Optional: Handle query param toggling
if st.query_params.get("show_info_tab1") == "true":
    st.session_state["show_info_tab1"] = not st.session_state["show_info_tab1"]
    st.query_params["show_info_tab1"] = "false"  # Reset after toggle

# 🔁 Optional: Handle query param toggling
if st.query_params.get("show_info_tab2") == "true":
    st.session_state["show_info_tab2"] = not st.session_state["show_info_tab2"]
    st.query_params["show_info_tab2"] = "false"  # Reset after toggle

# 🔁 Optional: Handle query param toggling
if st.query_params.get("show_info_tab3") == "true":
    st.session_state["show_info_tab3"] = not st.session_state["show_info_tab3"]
    st.query_params["show_info_tab3"] = "false"  # Reset after toggle


# ✅ Inject Custom CSS
def inject_custom_css():
    st.markdown("""
            <style>

            /* Force the tooltip (help text) background and text color */
            [data-testid="stTooltipContent"] {
                background-color: black !important;
                color: white !important;
                border-radius: 6px !important;
                font-size: 0.85rem !important;
                padding: 6px 8px !important;
            }

            /* ---------- HEADER ---------- */
            h1, h2, h3, h4 {
                color: #e50914;
                font-weight: 700;
            }

            /* ---------- SUBTLE BOX SHADOW ON WIDGETS ---------- */
            .stButton>button, .stSelectbox, .stRadio, .stTextInput>div>div>input, .stExpander, .stDataFrame {
                box-shadow: 0px 0px 10px rgba(229, 9, 20, 0.2);
                border-radius: 8px !important;
            }

             /* ---------- TABS ---------- */
            [data-baseweb="tab"] {
                background-color: #1c1c1c;
                color: white;
                border-radius: 5px 5px 0 0;
            }
            [data-baseweb="tab"][aria-selected="true"] {
                background-color: #e50914;
                color: white;
                font-weight: bold;
            }

            /* ---------- LABEL TEXT ---------- */
            label, .css-1cpxqw2 {
                color: #f5f5f5 !important;
            }

            /* ---------- SIDEBAR ---------- */
            .css-6qob1r {
                background-color: #121212 !important;
                border-right: 1px solid #2e2e2e;
            }

            /* ---------- GLOBAL BUTTON STYLE (unchanged) ---------- */
            .stButton>button {
                background-color: #e50914;
                color: black;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            .stButton>button:hover {
                background-color: #ff3333;
            }

            /* ---------- INFO BOX ---------- */
            .stAlert {
                border: 1px solid #e50914;
                background-color: #1e1e1e;
                color: #f5f5f5;
                border-radius: 8px;
            }

            /* ---------- DATAFRAME STYLING ---------- */
            thead tr th {
                background-color: #1c1c1c;
                color: #ffffff;
                font-weight: bold;
            }
            tbody tr td {
                background-color: #101010;
                color: #f5f5f5;
            }

            /* ---------- EXPANDERS ---------- */
            .stExpanderHeader {
                background-color: #1c1c1c !important;
                color: #ffffff !important;
                font-weight: bold;
            }

            /* ---------- RADIO BUTTON TEXT COLOR ---------- */
            [data-baseweb="radio"] label {
                color: white !important;
                font-weight: 500;
            }

            /* ---------- NOTIFICATION MESSAGES ---------- */
            div[data-testid="stNotificationContent"] {
                color: white !important;
                font-weight: 500;
            }

            /* ---------- TOOLTIP STYLING ---------- */
            .tooltip {
                position: relative;
                display: inline-block;
                cursor: pointer;
                color: #ff4b4b;
                font-size: 20px;
            }
            .tooltip .tooltiptext {
                visibility: hidden;
                width: 250px;
                background-color: #222;
                color: #fff;
                text-align: left;
                border-radius: 6px;
                padding: 10px;
                position: absolute;
                z-index: 1;
                bottom: 125%;
                left: 50%;
                margin-left: -125px;
                opacity: 0;
                transition: opacity 0.3s;
            }
            .tooltip:hover .tooltiptext {
                visibility: visible;
                opacity: 1;
            }

            /* ---------- GLOBAL TEXT CONTRAST FIX (SAFE) ---------- */
            body, .stApp, section.main, header, h1, h2, h3, h4, h5, h6, p, label {
                color: #ffffff !important;
            }

            /* ---------- INPUT TEXT + BACKGROUND ---------- */
            input, textarea {
                color: #ffffff !important;
                background-color: #1a1a1a !important;
            }

            /* ---------- FOCUS STATES (inputs, select) ---------- */
            input:focus, select:focus, textarea:focus {
                border: 1px solid #ff4b4b !important;
                background-color: #262626 !important;
            }

            /* ---------- MAIN PAGE BACKGROUND ---------- */
            html, body {
                background-color: #000000 !important;
            }

            /* ---------- CENTER CONTAINER BACKGROUND ---------- */
            section.main > div {
                background-color: transparent !important;
            }

            /* ---------- SIDEBAR BACKGROUND FIX ---------- */
            [data-testid="stSidebar"], .css-1d391kg, .css-6qob1r {
                background-color: #000000 !important;
                color: white !important;
            }

            /* ========== TWEAKS FOR WHITE ELEMENTS ========== */
            [data-testid="stFileUploaderDropzone"] label {
                color: #000000 !important;
            }
            [data-testid="stFileUploaderDropzone"] button {
                color: #000000 !important;
                background-color: #ffffff !important;
                border: 1px solid #aaa !important;
            }
            [data-testid="stFileUploaderDropzone"]:hover {
                border: 1px solid #ff3333 !important;
                box-shadow: 0 0 10px rgba(229, 9, 20, 0.3);
            }

            /* ---------- SELECTBOX CLOSED STATE ---------- */
            div[data-baseweb="select"] {
                background-color: #1a1a1a !important;
                color: white !important;
            }

            /* ---------- SELECTBOX OPEN MENU ---------- */
            div[data-testid="stSelectbox"] ul {
                background-color: #1a1a1a !important;
                color: white !important;
            }
            div[data-testid="stSelectbox"] ul li {
                color: white !important;
            }

            /* ---------- SELECTBOX TEXT ---------- */
            div[data-testid="stSelectbox"] > div {
                color: white !important;
            }

            /* ---------- SELECTBOX BORDER + HOVER ---------- */
            .css-1s2u09g-control {
                background-color: #1a1a1a !important;
                border-color: #e50914 !important;
            }
            .css-1s2u09g-control:hover {
                box-shadow: 0 0 6px rgba(229, 9, 20, 0.4);
            }
            .css-1s2u09g-control:focus {
                border-color: #ff3333 !important;
            }

            /* ---------- DEFAULT BUTTONS ---------- */
            .stButton > button:not([title="Click to toggle info"]) {
              background-color: #e50914 !important;
              color: white !important;
              font-weight: bold;
              border: none;
              border-radius: 5px;
            }

            /* ---------- FIX DROPDOWN VISIBILITY ---------- */
            select, option, .stSelectbox div, .css-1s2u09g-control, .css-1wa3eu0-placeholder, .css-1uccc91-singleValue, .css-qc6sy-singleValue {
                color: #ffffff !important;
                background-color: #1a1a1a !important;
                border-color: #e50914 !important;
            }

            /* Dropdown menu options */
            div[data-testid="stSelectbox"] ul {
                background-color: #1a1a1a !important;
                color: #ffffff !important;
            }

            /* ========== FIX DROPDOWN MENU OPTIONS WHEN OPEN ========== */

            /* The container holding the dropdown options */
            div[data-testid="stSelectbox"] ul {
                background-color: #1a1a1a !important;
                color: white !important;
                border: 1px solid #e50914 !important;
                box-shadow: 0px 0px 10px rgba(229, 9, 20, 0.3);
            }

            /* Each individual option item */
            div[data-testid="stSelectbox"] ul li {
                background-color: #1a1a1a !important;
                color: #ffffff !important;
                font-weight: 500;
            }

            /* Hovered item */
            div[data-testid="stSelectbox"] ul li:hover {
                background-color: #e50914 !important;
                color: #ffffff !important;
            }


           /* Final: force only the info button to black */
            .stButton > button[title="Click to toggle info"],
            .stButton > button[title="Click to toggle info"] * {
              background-color: #000 !important;
              color: #fff !important;
              border-radius: 12px !important;
              box-shadow: 0 0 10px rgba(229, 9, 20, .4) !important;
              padding: 0 !important;
            }

            /* Make only the info button black with a large white "i" */
            .info-btn-wrapper button[title="Click to toggle info"] {
              background-color: #000000 !important; /* black background */
              color: #ffffff !important; /* white text/icon */
              font-weight: bold !important;
              font-size: 100px !important; /* size of "i" */
              width: 300px !important;
              height: 300px !important;
              border-radius: 12px !important;
              text-align: center !important;
              padding: 0 !important;
              line-height: 1 !important;
            } 

            thead, th.col_heading, th.row_heading {
              background-color: #8B0000 !important;
              color: white !important;
            }

            </style>
        """, unsafe_allow_html=True)


# ✅ Call the custom CSS injector
inject_custom_css()

# Path to your Excel file in the repo (same folder as streamlit_app.py)
EXCEL_FILE_PATH = "marketing_decision_intelligence_system_data_synthetic.xlsx"


@st.cache_data(show_spinner=False)
def load_excel_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Try current directory first (for Streamlit Cloud)
    primary_path = "marketing_decision_intelligence_system_data_synthetic.xlsx"

    # Try local path (for local testing)
    local_path = os.path.expanduser("~/Downloads/marketing_decision_intelligence_system_data_synthetic.xlsx")

    if os.path.exists(primary_path):
        path = primary_path
    elif os.path.exists(local_path):
        path = local_path
    else:
        st.error("❌ File not found in either local or cloud path.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    try:
        xls = pd.ExcelFile(path, engine="openpyxl")
    except Exception as e:
        st.error(f"❌ Failed to open Excel file: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    try:
        seg_mix = xls.parse('segment_recommendations_mix')
        pod_segs = xls.parse('pod_account_type_segments')
        pod_details = xls.parse('pod_account_type_details')
        campaign = xls.parse('campaign_effectiveness')
        campaign_accounts = xls.parse('campaign_opps_accounts')
        info_df = xls.parse('INFO')
    except Exception as e:
        st.error(f"❌ Failed to parse one or more sheets: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    return seg_mix, pod_segs, pod_details, campaign, campaign_accounts, info_df


# FILTERS ACROSS TABS
# Shared defaults
if "region_filter" not in st.session_state:
    st.session_state.region_filter = "All"
if "acct_type_filter" not in st.session_state:
    st.session_state.acct_type_filter = "All"

# Tab-specific (only used in Tab 2)
if "pod_filter" not in st.session_state:
    st.session_state.pod_filter = "All"


# Small helper to keep prior selection valid (useful when options change and saved selection not in new list)
def select_with_shared_key(label, options, key):
    # fall back to "All" if current value not in options
    cur = st.session_state.get(key, "All")
    if cur not in options:
        st.session_state[key] = "All"
        cur = "All"
    return st.selectbox(label, options, key=key)


def render_info_icon(tab_info_df: pd.DataFrame):
    for _, row in tab_info_df.iterrows():
        field = row["Field"]
        desc = row["Definition"]
        st.markdown(f"**{field}**\n\n{desc}\n")


def create_gauge(value: float, title: str, color: str) -> go.Figure:
    """
    Construct a radial gauge indicator using Plotly.

    Parameters
    ----------
    value : float
        The value to display on the gauge (0‑100).
    title : str
        Title to display on the gauge.
    color : str
        Color for the indicator bar.

    Returns
    -------
    plotly.graph_objects.Figure
        A gauge figure ready to be rendered in Streamlit.
    """
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=round(value),
            number={
                "suffix": "%",
                "font": {"color": "white", "size": 36},  # Increased size
                "valueformat": ".0f"
            },
            title={"text": title, "font": {"color": "white", "size": 18}},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickcolor": "white",
                    "showticklabels": False
                },
                "bar": {"color": color},
                "bgcolor": "#444444",
                "borderwidth": 2,
                "bordercolor": "#777777",
            },
        )
    )

    fig.update_layout(
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        margin=dict(l=20, r=20, t=40, b=20),
        height=250,
    )

    return fig


def create_bubble_chart(
        df: pd.DataFrame,
        title: str = "",
        selected_campaign="All"
) -> go.Figure:
    """
    Create an interactive bubble chart using Plotly.

    The x-axis corresponds to Opportunity $, the y-axis corresponds to
    Contact Engagements, the size of each bubble corresponds to the count
    of Opportunities, and the color encodes the Region.

    Parameters
    ----------
    df : pd.DataFrame
        Campaign effectiveness data filtered by user selections.
    title : str, optional
        Title for the chart, by default "".
    bg_color : str, optional
        Optional background fill color in rgba format.

    Returns
    -------
    plotly.graph_objects.Figure
        Bubble chart ready to render in Streamlit.
    """

    # Ensure the necessary columns exist; if not, return an empty figure.
    required_cols = {"Opportunity $", "Cost $", "Opportunities", "Region", "Campaign"}
    if not required_cols.issubset(set(df.columns)):
        return go.Figure()

    # Filter out missing values AND rows where Cost $ = 0
    plot_df = df.dropna(subset=["Opportunity $", "Cost $", "Opportunities", "Region"])
    plot_df = plot_df[plot_df["Cost $"] != 0]  # 👈 FILTER OUT ZERO COST

    if plot_df.empty:
        return go.Figure()

    # --- Bubble Size Logic (Consistent across filter) ---
    # Use raw Opportunity counts as size input
    sizes = plot_df["Opportunities"].astype(float)

    # Calculate global sizeref (constant) based on full dataset's max opportunity count
    global_max_opps = df["Opportunities"].max()
    # sizeref formula: 2 * max(size) / (desired_maximum_marker_size^2)
    desired_max_size_px = 80  # You can tweak this (e.g., 40-80) to make bubbles larger/smaller overall
    global_sizeref = 2. * global_max_opps / (desired_max_size_px ** 2)

    # Define a discrete color map based on Tier Label
    tier_colors = {
        "Invest": "#14532d",  # dark green
        "Refine": "#9B870D",  # yellow/goldenrod
        "Reduce": "#7f1d1d"  # dark red
    }

    # Create a color column based on Tier Label
    plot_df["Color"] = plot_df["Tier Label"].map(tier_colors).fillna("#808080")  # default to grey if missing

    fig = go.Figure()

    # Initialize shapes
    shapes = []

    # Apply background fill
    # if bg_color:
    #     x_min = plot_df["Opportunity $"].min()
    #     x_max = plot_df["Opportunity $"].max()
    #     y_min = plot_df["Cost $"].min()
    #     y_max = plot_df["Cost $"].max()
    #     shapes.append(
    #         dict(
    #             type="rect",
    #             xref="x",
    #             yref="y",
    #             x0=x_min,
    #             x1=x_max,
    #             y0=y_min,
    #             y1=y_max,
    #             fillcolor=bg_color,
    #             line=dict(width=0),
    #             layer="below",
    #         )
    #     )

    # Assign shapes if any
    if shapes:
        fig.update_layout(shapes=shapes)

    # --- Plot bubbles ---
    customdata = np.stack(
        [plot_df["Opportunities"], plot_df["Region"]],  # 👈 Region added
        axis=-1
    )

    # Determine opacity dynamically based on whether a specific campaign is selected
    if selected_campaign != "All":
        opacities = [0.25 if c != selected_campaign else 1.0 for c in plot_df["Campaign"]]
    else:
        opacities = [0.8] * len(plot_df)  # normal look for all bubbles

    fig.add_trace(
        go.Scatter(
            x=plot_df["Opportunity $"],
            y=plot_df["Cost $"],
            mode="markers",
            marker=dict(
                size=sizes,
                color=plot_df["Color"],
                sizemode="area",
                sizeref=global_sizeref,  # 👈 fixed sizeref based on full dataset
                sizemin=4,
                line=dict(width=1, color="white"),
                opacity=opacities
            ),
            text=plot_df["Campaign"],
            customdata=customdata,
            hovertemplate=(
                "<b>%{text}</b><br><br>"
                "Region: %{customdata[1]}<br>"  # 👈 Region shown on hover
                "Opportunity $: %{x:,.0f}<br>"
                "Opportunities: %{customdata[0]:,.0f}<br>"
                "Cost $: %{y}<br>"
                "<extra></extra>"
            ),
            showlegend=False,
        )
    )

    # --- Add invisible dummy traces to show legend by Tier Label ---
    for tier, color in tier_colors.items():
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=dict(size=20, color=color),
                name=tier,
                showlegend=True
            )
        )

    # Configure axes and layout (updated API)
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor="center", font=dict(color="white", size=28)),
        xaxis=dict(
            title=dict(text="Opportunity $", font=dict(color="white", size=20)),
            gridcolor="#333333",
            zeroline=False,
            tickfont=dict(color="white", size=16),
        ),
        yaxis=dict(
            title=dict(text="Cost $", font=dict(color="white", size=20)),
            gridcolor="#333333",
            zeroline=False,
            tickfont=dict(color="white", size=16),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(color="white", size=16),
        ),
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        margin=dict(l=40, r=40, t=60, b=80),
        height=600,
    )

    return fig


###############################################################################
# Main Streamlit app
###############################################################################

# Clear cache on startup (only for debugging / after data updates)
st.cache_data.clear()

def main():
    st.set_page_config(page_title="Marketing Decision Intelligence System", layout="wide", page_icon="📊")

    st.markdown(
        """
        <style>
            body {
                background-color: #0b0b0b;
                color: #f0f0f0;
            }
            .stChatInput textarea {
                color: #f0f0f0 !important;
            }
            .stChatInput textarea::placeholder {
                color: #f0f0f0 !important;
                opacity: 1 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # image_data = get_base64_image("Trend_T-Symbol_Extracted-removebg-preview.png")

    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 0;">
            <div style="flex: 1;">
                <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">Marketing Decision Intelligence System</h1>
                <p style="font-size: 1.1rem; color: #f0f0f0;">
                    Make smarter marketing decisions by uncovering winning strategies, increasing conversion rates, and maximizing campaign ROI.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # === Get Started Button Logic ===
    if "show_dashboard" not in st.session_state:
        st.session_state.show_dashboard = False

    if not st.session_state.show_dashboard:
        if st.button("🚀 Get Started"):
            st.session_state.show_dashboard = True
            st.rerun()
        return

    # === Load Excel File from Local Repo ===
    seg_mix, pod_segs, pod_details, campaign, campaign_accounts, info_df = load_excel_data()

    # === Sidebar Assistant ===
    #   with st.sidebar:
    #       st.header("💬 Assistant")
    #       st.write(
    #           "Ask a question about the data in any of the tabs. "
    #           "The assistant will retrieve relevant information and summarize it."
    #       )

    #       if not any(df.empty for df in [seg_mix, pod_segs, pod_details, campaign]):
    #           docs, vectorizer, store = build_vector_store({
    #               "Segment Recommendations": seg_mix,
    #               "Win Rate Recommendations": pod_segs,
    #               "Account Details": pod_details,
    #               "Campaign Effectiveness": campaign
    #           })
    #       else:
    #           docs, vectorizer, store = [], None, {}

    #       if "chat_messages" not in st.session_state:
    #           st.session_state.chat_messages = []

    #       for message in st.session_state.chat_messages:
    #           with st.chat_message(message["role"]):
    #               st.markdown(message["content"])

    #       if docs:
    #           user_input = st.chat_input("Type your question and press Enter...")
    #           if user_input:
    #               st.session_state.chat_messages.append({"role": "user", "content": user_input})
    #               results = query_vector_store(user_input, docs, vectorizer, store)
    #               answer = generate_answer_from_docs(results)
    #               st.session_state.chat_messages.append({"role": "assistant", "content": answer})
    #               with st.chat_message("assistant"):
    #                   st.markdown(answer)
    #       else:
    #           st.info("Upload your Excel data to start chatting with the assistant.")

    # === Shared Filters
    region_values_tab1 = sorted(seg_mix["Region"].dropna().unique())
    region_values_tab2a = sorted(pod_segs["Region"].dropna().unique())
    region_values_tab2b = sorted(pod_details["Region"].dropna().unique())
    region_values_tab3a = sorted(campaign["Region"].dropna().unique())
    region_values_tab3b = sorted(campaign_accounts["Region"].dropna().unique())
    all_region_options = sorted(
        set(region_values_tab1 + region_values_tab2a + region_values_tab2b + region_values_tab3a + region_values_tab3b))
    region_options = ["All"] + all_region_options

    acct_types_tab1 = sorted(seg_mix["Account Type"].dropna().unique())
    acct_types_tab2a = sorted(pod_segs["Account Type"].dropna().unique())
    acct_types_tab2b = sorted(pod_details["Account Type"].dropna().unique())
    all_acct_type_options = sorted(set(acct_types_tab1 + acct_types_tab2a + acct_types_tab2b))
    account_type_options = ["All"] + all_acct_type_options

    # === Tabs
    tabs = st.tabs([
        "📈 Open More High Value Opportunities",
        "🎯 Win More Active Opportunities",
        "🏆 Uncover Top Performing Campaigns",
    ])

    tab1_info = info_df[info_df["Tab"] == "segment_recommendations_mix"]
    tab2_info = info_df[info_df["Tab"] == "pod_account_type_segments"]
    tab3_info = info_df[info_df["Tab"] == "campaign_effectiveness"]

    def render_segment_recommendations(seg_mix_df: pd.DataFrame):
        st.subheader("Recommended Mix & Engagement Thresholds")
        st.dataframe(seg_mix_df, use_container_width=True)

    #############################################################################
    # Tab 1 – Open More High Value Opportunities
    #############################################################################
    with tabs[0]:
        col1, col2 = st.columns([10, 1])

        with col1:
            st.header("📈 Open More High Value Opportunities")
            st.write("Identify the optimal marketing mix and engagement thresholds for generating high-value opps.")

            # 💡 Add expander directly underneath the description
            with st.expander("ℹ️ What does this mean?"):
                st.markdown("""
                **Open Opportunities** are deals currently in flight (not yet closed). High value = above average $.

                This dashboard helps you identify:
                - Which channel combinations most often lead to high value opps
                - How much engagement is likely to create high value opps
                - Patterns that signal a high-value opportunity
                """)

        with col2:
            # Render the red "i" icon and include the hidden Streamlit button
            with col2:
                st.markdown('<div class="info-btn-wrapper">', unsafe_allow_html=True)
                if st.button("ℹ️ Data Guide", key="info-icon", help="Click to toggle info", type="primary"):
                    toggle_info_tab1()
                st.markdown('</div>', unsafe_allow_html=True)

        # Show the info panel content when toggled
        if st.session_state.get("show_info_tab1", False):
            st.subheader("ℹ️ Definitions for Tab 1 Fields")
            st.markdown("""<style>div[data-testid='column'] {width: 100% !important;}</style>""",
                        unsafe_allow_html=True)

            for _, row in tab1_info.iterrows():
                field = row["Field"]
                desc = row["Definition"]
                st.markdown(f"**{field}**\n\n{desc}\n")

            # Back to dashboard button closes the info panel and reruns
            if st.button("⬅ Back to Dashboard", key="back_to_dashboard_tab1"):
                st.session_state.show_info_tab1 = False
                st.rerun()
        else:
            # Regular dashboard content when info panel is not shown
            seg_regions = sorted(seg_mix["Region"].dropna().unique())
            seg_account_types = sorted(seg_mix["Account Type"].dropna().unique())
            persona_col = [c for c in seg_mix.columns if "persona" in c.lower()][0]

            col1, col2, col3 = st.columns([1, 1, 2])

            # 🌍 Tab 1 or Tab 2 region filter dropdown

            # Filter out "All Regions" from the dropdown values
            visible_regions = [r for r in seg_regions if r != "All Regions"]

            # Safely get region_filter from session state, fallback to "All"
            stored_region = st.session_state.get("region_filter", "All")

            with col1:
                selected_region = st.selectbox(
                    "Select Region 🌍",
                    ["All"] + visible_regions,
                    index=(["All"] + visible_regions).index(
                        stored_region if stored_region in visible_regions else "All"),
                    key="region_filter_ui"
                )
                st.session_state.region_filter = selected_region

            # Shortcut: Treat "All Regions" like "All" internally
            region_filter = selected_region if selected_region != "All Regions" else "All"

            with col2:
                selected_account_type = st.selectbox(
                    "Select Account Type 🏢",
                    ["All"] + seg_account_types,
                    index=(["All"] + seg_account_types).index(st.session_state.get("acct_type_filter", "All")),
                    key="acct_type_filter_ui"
                )
                st.session_state.acct_type_filter = selected_account_type

            with col3:
                selected_persona = st.radio(
                    "Select Targeted Persona 👤",
                    ["Technical (e.g. Engineers, Analysts, etc.)", "Exec Decision Makers (e.g. CIO, CISO, etc.)"],
                    horizontal=True,
                    key="persona_selector"
                )

            # Apply Region and Account Type filters from session state
            seg_filtered = seg_mix.copy()

            # 🟢 Handle Region Filter (Tab 1 uses account-level "Region")
            if region_filter not in ["All", "All Regions"]:
                seg_filtered = seg_filtered[seg_filtered["Region"] == region_filter]
            elif region_filter == "All Regions":
                # "All Regions" is a Tab 3 value; treat it as equivalent to "All" here by doing nothing
                pass

            # 🟢 Handle Account Type Filter
            if st.session_state.acct_type_filter != "All":
                seg_filtered = seg_filtered[seg_filtered["Account Type"] == st.session_state.acct_type_filter]

            # 🟢 Handle Persona Filter (if you still use a separate selectbox for this)
            if "Technical" in selected_persona:
                seg_filtered = seg_filtered[seg_filtered[persona_col] == "Technical"]
            else:
                seg_filtered = seg_filtered[seg_filtered[persona_col] == "Exec Decision Makers"]

            # Only show results if both filters are narrowed (optional)
            if region_filter != "All" and st.session_state.acct_type_filter != "All":
                st.subheader("Recommended Mix & Engagement Thresholds")
                table_fields = [
                    "Recommended Mix",
                    "Recommended Tactic Types",
                    "Touchpoints Goal",
                    "Contacts Attended Goal",
                    "Confidence Score"
                ]
                table_data = seg_filtered[table_fields].reset_index(drop=True)

                # Apply styling for dark background and white text
                styled_table = (
                    table_data
                    .style
                    .set_properties(
                        **{
                            "background-color": "#2c2c2c",  # Black background
                            "color": "#39FF14",  # Neon green text
                            "border-color": "white",  # Optional: white border
                        }
                    )
                    .set_table_styles(
                        [
                            {"selector": "thead", "props": [("background-color", "#8B0000"), ("color", "white")]},
                            # header row
                            {"selector": "th.row_heading",
                             "props": [("background-color", "#8B0000"), ("color", "white")]},  # row labels
                            {"selector": "th.col_heading",
                             "props": [("background-color", "#8B0000"), ("color", "white")]}  # column headers
                        ]
                    )
                )

                st.dataframe(styled_table, use_container_width=True)

                # Confidence Score Explanation
                with st.expander("ℹ️ Show Confidence Score Explanation"):
                    st.markdown("""
                                                **5 = Very High Confidence** – Backed by a large amount of data and strong results.  
                                                **4 = High Confidence** – Supported by a good amount of data and consistent results.  
                                                **3 = Medium Confidence** – Based on a moderate amount of data with solid results.  
                                                **2 = Low-Medium Confidence** – Limited or inconsistent data with early signals of effectiveness; interpret with caution.  
                                                **1 = Low Confidence** – Limited data or mixed results; interpret with caution.
                                            """)

                # Recommendations Disclaimer
                with st.expander("ℹ️ What are these recommendations based on?"):
                    st.markdown("""
                    These recommendations are powered by AI models trained on 2+ years of our engagement and opportunity data to maximize predictive accuracy.
                            """)

                # Full Recommended Mix with Digital Channels
                if "Full Recommended Mix with Digital Channels" in seg_filtered.columns:
                    unique_mix_values = seg_filtered[
                        "Full Recommended Mix with Digital Channels"].dropna().unique().tolist()
                    if unique_mix_values:
                        if st.button("Show Full Recommended Mix with Digital Channels"):
                            for mix in unique_mix_values:
                                st.markdown(f"- {mix}")

                # Top Performing Verticals
                if "Top Verticals" in seg_filtered.columns:
                    vertical_vals = seg_filtered["Top Verticals"].dropna().unique().tolist()
                    if vertical_vals:
                        st.selectbox("Top Performing Verticals", options=vertical_vals, key="top_verticals")

            else:
                # Custom info message styled for dark mode when no filters selected
                st.markdown(
                    "<div style='background-color:#1c1c1c; padding:10px; border-radius:8px; border:1px solid #e50914; color:white;'>"
                    "Select a Region and Account Type to see recommendations."
                    "</div>",
                    unsafe_allow_html=True
                )

    #############################################################################
    # Tab 2 – Win More Active Opportunities
    #############################################################################
    with tabs[1]:
        # Top bar: title + info button
        col1, col2 = st.columns([10, 1])
        with col1:
            st.header("🎯 Win More Active Opportunities")
            st.write(
                "Leverage persona and tactic recommendations to improve your close rates and address gaps in active opportunities."
            )
            # "What does this mean?" expander for Tab 2
            with st.expander("ℹ️ What does this mean?"):
                st.markdown("""
                **Win More Active Opps** focuses on converting more open opportunities into revenue using historical win rates.

                This dashboard helps you:
                - Identify the most effective persona–tactic combinations to secure closed won opps
                - Pinpoint high-priority accounts with open opps but no recent engagement — untapped wins waiting to happen
                - Prioritize accounts based on their likelihood to close when applying the right tactics
                """)

        with col2:
            st.markdown('<div class="info-btn-wrapper">', unsafe_allow_html=True)
            if st.button("ℹ️ Data Guide", key="info-icon-tab2", help="Click to toggle info", type="primary"):
                toggle_info_tab2()
            st.markdown('</div>', unsafe_allow_html=True)

        # Info panel
        if st.session_state.get("show_info_tab2", False):
            st.subheader("ℹ️ Definitions for Tab 2 Fields")
            st.markdown(
                """<style>div[data-testid='column'] {width: 100% !important;}</style>""",
                unsafe_allow_html=True
            )
            for _, row in tab2_info.iterrows():
                field = row["Field"]
                desc = row["Definition"]
                st.markdown(f"**{field}**\n\n{desc}\n")

            if st.button("⬅ Back to Dashboard", key="back_to_dashboard_tab2"):
                st.session_state.show_info_tab2 = False
                st.rerun()

        # Regular dashboard content
        else:
            # Prepare dropdown values
            pods = sorted(pod_segs["Pod"].dropna().unique())
            regions = sorted(pod_segs["Region"].dropna().unique())
            acct_types = sorted(pod_segs["Account Type"].dropna().unique())

            col1, col2, col3 = st.columns([1, 1, 1])

            # 🌍 Region Selector (Tab 2)
            region_filter = st.session_state.get("region_filter", "All")

            # Remove "All Regions" from visible dropdown list
            visible_regions = [r for r in regions if r != "All Regions"]

            with col1:
                selected_region = st.selectbox(
                    "🌍 Region",
                    ["All"] + visible_regions,
                    index=(["All"] + visible_regions).index(
                        region_filter if region_filter in visible_regions else "All"),
                    key="tab2_region"
                )
                # Store user selection in session state
                st.session_state.region_filter = selected_region
                # Optional: remap "All Regions" to "All" (safeguard)
                region_filter = selected_region if selected_region != "All Regions" else "All"

            with col2:
                selected_account_type = st.selectbox(
                    "🏢 Account Type",
                    ["All"] + acct_types,
                    index=(["All"] + acct_types).index(st.session_state.get("acct_type_filter", "All")),
                    key="tab2_account_type"
                )
                st.session_state.acct_type_filter = selected_account_type

            with col3:
                selected_pod = st.selectbox("🧩 Pod", ["All"] + pods, key="pod_filter")

            # 🧠 Optional display note for user
            st.markdown(
                f"Select your 🧩 Pod to unlock deeper insights and more detailed recommendations."
            )

            # === Filtered dataframe for win rate (top section)
            win_filtered = pod_segs.copy()
            if region_filter != "All":
                win_filtered = win_filtered[win_filtered["Region"] == region_filter]
            if st.session_state.acct_type_filter != "All":
                win_filtered = win_filtered[win_filtered["Account Type"] == st.session_state.acct_type_filter]
            if selected_pod != "All":
                win_filtered = win_filtered[win_filtered["Pod"] == selected_pod]

            # Aggregated win rates
            win_without = (
                win_filtered["Win Rate Without Recommended Tactic"].dropna().mean()
                if "Win Rate Without Recommended Tactic" in win_filtered.columns
                else np.nan
            )
            win_with = (
                win_filtered["Win Rate With Recommended Tactic"].dropna().mean()
                if "Win Rate With Recommended Tactic" in win_filtered.columns
                else np.nan
            )
            win_without = float(win_without) if not np.isnan(win_without) else 0.0
            win_with = float(win_with) if not np.isnan(win_with) else 0.0
            diff = max(0.0, win_with - win_without)

            # Recommendations (mode)
            tactic_rec = (
                win_filtered["Recommended Tactic"].mode().iloc[0]
                if "Recommended Tactic" in win_filtered.columns and not win_filtered.empty
                else "N/A"
            )

            tactic_type_rec = (
                win_filtered["Recommended Tactic Type"].mode().iloc[0]
                if "Recommended Tactic Type" in win_filtered.columns and not win_filtered.empty
                else "N/A"
            )

            persona_rec = (
                win_filtered["Recommended Persona"].mode().iloc[0]
                if "Recommended Persona" in win_filtered.columns and not win_filtered.empty
                else "N/A"
            )

            # Summary card
            title_text = f"{region_filter if region_filter != 'All' else 'All Regions'}" + \
                         (
                             f"  •  {st.session_state.acct_type_filter}" if st.session_state.acct_type_filter != "All" else "") + \
                         (f"  •  {selected_pod}" if selected_pod != "All" else "")

            st.markdown(
                f"""
                <style>
                  .rec-card {{
                    background: linear-gradient(145deg, rgba(60,5,5,.95) 0%, rgba(35,0,0,.95) 100%);
                    border: 1px solid rgba(229, 9, 20, 0.5);
                    border-radius: 28px;
                    padding: 24px 28px;
                    box-shadow: 0 8px 30px rgba(229, 9, 20, 0.18), inset 0 1px 0 rgba(255,255,255,0.04);
                  }}
                  .rec-title {{
                    text-align: center;
                    font-size: 30px;
                    font-weight: 800;
                    letter-spacing: .4px;
                    color: #ff6b6b;  /* highlight red */
                    margin: 0 0 10px 0;
                    text-shadow: 0 2px 14px rgba(229,9,20,.35);
                  }}
                  .rec-sub {{
                    text-align: center;
                    font-size: 18px;
                    color: #e5e5e5;
                    margin: 0 0 18px 0;
                    opacity: .9;
                  }}
                  .rec-row {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 14px;
                    align-items: stretch;
                    text-align: center;
                  }}
                  .rec-pill {{
                    background: #1b1b1b;
                    border: 1px solid rgba(229, 9, 20, 0.35);
                    border-radius: 18px;
                    padding: 16px 14px;
                  }}
                  .rec-label {{
                    display:block;
                    font-size: 14px;
                    letter-spacing: .5px;
                    color: #ff8a8a;
                    text-transform: uppercase;
                    margin-bottom: 6px;
                  }}
                  .rec-value {{
                    font-size: 22px;
                    font-weight: 700;
                    color: #ffffff;
                  }}
                  .delta-big {{
                    text-align:center;
                    font-size:56px;
                    line-height:1.05;
                    color:#ffffff;
                    margin-top: 10px;
                    text-shadow: 0 2px 14px rgba(229,9,20,.35);
                  }}
                  .delta-label {{
                    text-align:center;
                    color:#cfcfcf;
                    margin-top:-6px;
                    font-size:15px;
                  }}
                  .industries-wrap {{
                    margin-top: 26px;
                    text-align: center;
                  }}
                  .industries-title {{
                    font-size: 40px;
                    font-weight: 800;
                    color: #ffffff;  /* white text */
                    letter-spacing: .5px;
                    margin: 8px 0 6px 0;
                    text-shadow: none;
                  }}
                  .industries-line {{
                    font-size: 22px;
                    color: #f3f3f3;
                    margin-bottom: 8px;
                  }}
                  .industries-note {{
                    font-size: 16px;
                    color: #dddddd;
                    font-style: italic;
                    opacity: .95;
                  }}
                  @media (max-width: 900px) {{
                    .rec-row {{ grid-template-columns: 1fr; }}
                  }}
                </style>

                <div class="rec-card">
                  <div class="rec-title">{title_text}</div>
                  <div class="rec-sub">
                    Recommendations for this selection
                    <span title="Tactics are chosen based on win rate. The Tactic Type is the best-performing subtype within that tactic.&#10;&#10;The Persona reflects who’s driven the most wins across all campaigns within that tactic — not just the specific type.">
                      ℹ️
                    </span>
                  </div>
                </div>
                  <div class="rec-row">
                    <div class="rec-pill">
                      <span class="rec-label">Recommended Persona</span>
                      <span class="rec-value">{persona_rec}</span>
                    </div>
                    <div class="rec-pill">
                      <span class="rec-label">Recommended Tactic</span>
                      <span class="rec-value">{tactic_rec}</span>
                    </div>
                    <div class="rec-pill">
                      <span class="rec-label">Tactic Type</span>
                      <span class="rec-value">{tactic_type_rec}</span>
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # ===== GAUGES =====
            g_col1, g_col2, g_col3 = st.columns([1, 1, 1])
            with g_col1:
                fig1 = create_gauge(win_without * 100, "Win Rate Without Recommended Tactic", "#FF0000")
                st.plotly_chart(fig1, use_container_width=True)
            with g_col2:
                st.markdown(
                    f"""
                    <style>
                      /* Center container the same height as the gauges so it sits vertically centered */
                      .delta-shell {{
                        min-height: 240px;              /* tweak if your gauges are taller/shorter */
                        display: grid;
                        place-items: center;            /* perfect centering */
                      }}
                      /* Arrow/chevron card */
                      .delta-chev {{
                        --bg: #1b1b1b;
                        background: linear-gradient(145deg, #1b1b1b 0%, #141414 100%);
                        border: 1px solid rgba(229, 9, 20, .55);
                        border-radius: 14px;
                        padding: 18px 28px;
                        width: clamp(320px, 32vw, 460px);
                        clip-path: polygon(0 0, 85% 0, 100% 50%, 85% 100%, 0 100%);  /* chevron */
                        box-shadow: 0 8px 30px rgba(229, 9, 20, 0.18), inset 0 1px 0 rgba(255,255,255,0.04);
                        text-align: center;
                      }}
                      .delta-num {{
                        font-size: clamp(40px, 6vw, 64px);
                        line-height: 1.05;
                        font-weight: 800;
                        color: #fff;
                        text-shadow: 0 2px 14px rgba(229, 9, 20, .35);
                        margin-bottom: 6px;
                      }}
                      .delta-label {{
                        font-size: 16px;
                        color: #d8d8d8;
                        letter-spacing: .3px;
                        margin-top: -2px;
                      }}
                      @media (max-width: 900px) {{
                        .delta-shell {{ min-height: 180px; }}
                      }}
                    </style>
                    <div class="delta-shell">
                      <div class="delta-chev">
                        <div class="delta-num">{diff * 100:.0f}%</div>
                        <div class="delta-label">Win Rate Improvement</div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with g_col3:
                fig2 = create_gauge(win_with * 100, "Win Rate With Recommended Tactic", "#43A047")
                st.plotly_chart(fig2, use_container_width=True)

            # ===== TOP 3 INDUSTRIES =====
            top3_industries = (
                win_filtered["Top 3 Industries"].dropna().iloc[0]
                if "Top 3 Industries" in win_filtered.columns and not win_filtered.empty
                else "—"
            )
            top3_note = (
                win_filtered["Top 3 Industry Note"].dropna().iloc[0]
                if "Top 3 Industry Note" in win_filtered.columns and not win_filtered.empty
                else ""
            )
            st.markdown(
                f"""
                <style>
                    .industries-title {{
                        font-size: 34px;
                        font-weight: bold;
                        margin-bottom: 5px;
                    }}
                    .industries-line {{
                        font-size: 24px;
                    }}
                    .industries-note {{
                        font-size: 18px;
                        color: #ccc;
                    }}
                </style>

                <div class="industries-wrap">
                    <div class="industries-title">Top 3 Industries</div>
                    <div class="industries-line">{top3_industries}</div>
                    <div class="industries-note">{top3_note}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Sections divider
            st.markdown("<hr style='margin-top: 40px; margin-bottom: 30px; border: 1px solid #777;'>",
                        unsafe_allow_html=True)

            st.markdown("### Account Details")

            st.markdown("The below table contains accounts with currently open opportunities.")

            # === Account details section (bottom table)
            detail_filtered = pod_details.copy()
            if region_filter != "All":
                detail_filtered = detail_filtered[detail_filtered["Region"] == region_filter]
            if st.session_state.acct_type_filter != "All":
                detail_filtered = detail_filtered[detail_filtered["Account Type"] == st.session_state.acct_type_filter]
            if selected_pod != "All":
                detail_filtered = detail_filtered[detail_filtered["Pod"] == selected_pod]

            # Filter only current opps
            if "Current Opps? (< 12 mo)" in detail_filtered.columns:
                detail_filtered = detail_filtered[
                    detail_filtered["Current Opps? (< 12 mo)"].str.lower() == "yes"
                    ]

            # Additional user filters
            account_owners = sorted(detail_filtered["Account Owner"].dropna().unique().tolist())
            c_levels = sorted(detail_filtered["C-Level Engaged? (< 3 mo)"].dropna().unique().tolist())
            engagement_counts = detail_filtered["Recent Engagements (< 3 mo)"].dropna().astype(float)
            if not engagement_counts.empty:
                min_eng, max_eng = int(engagement_counts.min()), int(engagement_counts.max())
            else:
                min_eng, max_eng = 0, 0

            # Expand to 4 columns
            f_col1, f_col2, f_col3 = st.columns(3)

            with f_col1:
                selected_owner = st.selectbox("Account Owner", ["All"] + account_owners, key="owner_filter")

            with f_col2:
                min_val = int(min_eng)
                max_val = int(max_eng)

                if min_val == max_val:
                    # Only one possible value, so use number input instead of slider
                    selected_engagement_range = (min_val, max_val)
                    only_val = st.number_input(
                        "Recent Marketing Engagements (< 3 months)",
                        min_value=min_val,
                        max_value=max_val,
                        value=min_val,
                        step=1,
                        key="engagement_filter_num",
                    )
                    # Normalize to tuple for consistency
                    selected_engagement_range = (only_val, only_val)
                else:
                    selected_engagement_range = st.slider(
                        "Recent Marketing Engagements (< 3 months)",
                        min_value=min_val,
                        max_value=max_val,
                        value=(min_val, max_val),
                        step=1,
                        key="engagement_filter",
                    )

            with f_col3:
                selected_clevel = st.multiselect(
                    "C-Level Engaged? (< 3 months)",
                    c_levels,
                    default=c_levels,
                    key="clevel_filter"
                )

            # Apply filters
            if selected_owner != "All":
                detail_filtered = detail_filtered[detail_filtered["Account Owner"] == selected_owner]
            if min_eng != max_eng:
                detail_filtered = detail_filtered[
                    detail_filtered["Recent Engagements (< 3 mo)"].astype(float).between(
                        selected_engagement_range[0], selected_engagement_range[1]
                    )
                ]
            if selected_clevel:
                detail_filtered = detail_filtered[
                    detail_filtered["C-Level Engaged? (< 3 mo)"].isin(selected_clevel)
                ]

            # Display details table with dark styling
            detail_cols = [
                "Account Name",
                "Account Owner",
                "Account Type",
                "Industry",
                "Region",
                "Pod",
                "Recent Engagements (< 3 mo)",
                "C-Level Engaged? (< 3 mo)",
            ]
            existing_cols = [c for c in detail_cols if c in detail_filtered.columns]

            # Apply dark theme styling
            styled_detail_table = detail_filtered[existing_cols].reset_index(drop=True).style.set_table_styles([
                {"selector": "thead", "props": [("background-color", "#8B0000"), ("color", "white")]},  # header
                {"selector": "th.col_heading", "props": [("background-color", "#8B0000"), ("color", "white")]},
                # column headers
                {"selector": "th.row_heading", "props": [("background-color", "#8B0000"), ("color", "white")]}
                # row index
            ]).set_properties(
                **{
                    "background-color": "#2c2c2c",  # Dark grey cell background
                    "color": "white",  # White text
                    "border-color": "white",  # Optional: white borders
                }
            )

            st.dataframe(styled_detail_table, use_container_width=True)

    #############################################################################
    # Tab 3 – Uncover Top Performing Campaigns
    #############################################################################
    with tabs[2]:
        col1, col2 = st.columns([10, 1])
        with col1:
            st.header("🏆 Top Performing Campaigns")
            st.write(
                "Compare the ROI of historical campaigns by viewing their costs and opportunities.")

            # 💡 Add expander directly underneath the description
            with st.expander("ℹ️ What does this mean?"):
                st.markdown("""
                    **Top Performing Campaigns** are marketing activities that generate high ROI: strong opps and opp $ with low cost.

                    This dashboard helps you:
                    - Identify campaigns that deliver the highest ROI across regions and influence windows
                    - Compare performance by attendance, opportunity counts, opportunity $, and costs
                    - Spot which campaigns to 🟩 **Invest**, 🟨 **Refine**, or 🟥 **Reduce** for maximum impact
                """)
        with col2:
            st.markdown('<div class="info-btn-wrapper">', unsafe_allow_html=True)
            if st.button("ℹ️ Data Guide", key="info-icon-tab3", help="Click to toggle info", type="primary"):
                toggle_info_tab3()
            st.markdown('</div>', unsafe_allow_html=True)

        # Info panel
        if st.session_state.get("show_info_tab3", False):
            st.subheader("ℹ️ Definitions for Tab 3 Fields")
            st.markdown(
                """<style>div[data-testid='column'] {width: 100% !important;}</style>""",
                unsafe_allow_html=True
            )
            for _, row in tab3_info.iterrows():
                field = row["Field"]
                desc = row["Definition"]
                st.markdown(f"**{field}**\n\n{desc}\n")

            if st.button("⬅ Back to Dashboard", key="back_to_dashboard_tab3"):
                st.session_state.show_info_tab3 = False
                st.rerun()

        # Regular dashboard content
        else:
            # === Base filters: Always shown ===
            col1, col2, col3 = st.columns([1, 2, 2])

            with col1:
                # Custom Markdown label with tighter spacing (reduced bottom margin)
                st.markdown(
                    """
                    <div style="margin-bottom: -5px; font-size:15px">
                        <b>Campaign Region</b>
                        <span title='🌍 Campaign Region shows campaign-level data (e.g. "-STH-" in name = South campaign). “All” shows every campaign regardless of region. “All Regions” only includes campaigns explicitly marked as cross-regional (e.g. containing “-ALL-”).'>
                            ℹ️
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                region_options = ["All"] + sorted(campaign["Region"].dropna().unique().tolist())
                default_region = st.session_state.get("region_filter", "All")

                # Fallback if default not in options
                if default_region not in region_options:
                    default_region = "All"

                selected_c_region = st.selectbox(
                    "",  # No label
                    region_options,
                    index=region_options.index(default_region),
                    key="campaign_region_ui"
                )

                st.session_state.region_filter = selected_c_region

            with col2:
                if "Influence Window" in campaign.columns:
                    vals = (
                        campaign["Influence Window"]
                        .dropna()
                        .astype(str)
                        .str.strip()
                    )

                    pref_order = ["Pre-Open Influence", "Post-Open Influence", "Won"]
                    unique_no_all = [v for v in vals.unique().tolist() if v != "All"]
                    unique_no_all = sorted(
                        unique_no_all,
                        key=lambda x: pref_order.index(x) if x in pref_order else 99,
                    )
                    stage_options = ["All"] + unique_no_all
                else:
                    stage_options = ["All", "Pre-Open Influence", "Post-Open Influence", "Won"]

                # Label + tooltip icon
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; margin-bottom: 4px;">
                        <span style="font-size: 15px;"><b>Influence Window</b></span>
                        <span title="The timeframe in which marketing influenced an opportunity—before it opened (MGO), after it opened (MIO), or before it was closed-won."
                              style="margin-left: 6px; font-size: 14px; cursor: help;">
                            ℹ️
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                selected_stage = st.radio(
                    "",  # Empty label since it's defined in the markdown above
                    stage_options,
                    horizontal=True,
                    key="campaign_stage",
                )

            with col3:
                # Inline label + tooltip icon using HTML
                st.markdown(
                    """
                    <style>
                        /* Reduce top margin above the radio buttons */
                        div[data-testid="stRadio"] > label {
                            margin-bottom: -4px;
                        }

                        /* Pull radio group closer to the header */
                        div[role='radiogroup'] {
                            margin-top: -8px;
                            gap: 4px !important;  /* Reduce spacing between buttons */
                        }

                        /* Optional: tighter vertical alignment in Streamlit columns */
                        div[data-testid="column"] {
                            align-items: center;
                        }
                    </style>

                    <div style="display: flex; align-items: center; margin-bottom: 4px;">
                        <span style="font-size: 15px;"><strong>Tier Label</strong></span>
                        <span title="Tier is based on a composite ROI score considering return efficiency and opportunity volume across ALL influence windows. ROI Ratio shown below reflects raw Opp $ divided by Cost."
                              style="margin-left: 6px; font-size: 14px; cursor: help;">
                            ℹ️
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Emoji-enhanced radio options
                tier_labels = {
                    "All": "All",
                    "Invest": "🟩 **Invest**",
                    "Refine": "🟨 **Refine**",
                    "Reduce": "🟥 **Reduce**"
                }

                tier_options = list(tier_labels.values())
                selected_tier_label = st.radio(
                    label="",
                    options=tier_options,
                    horizontal=True,
                    key="tier_filter"
                )

            # Map back to original label for filtering
            selected_tier = [k for k, v in tier_labels.items() if v == selected_tier_label][0]

            # === Optional filters toggle ===
            show_filters = st.toggle("🔎 Show More Filter Options", value=False)

            # === Prepare campaign data ===
            campaigns_filtered = campaign.copy()
            if not campaigns_filtered.empty and "Campaign" in campaigns_filtered.columns:
                campaigns_filtered = campaigns_filtered[
                    ~campaigns_filtered["Campaign"].str.contains(
                        "Sales Contact Me|Customer Training|Customer Newsletter",
                        case=False, na=False
                    )
                ]

            # === Optional filters ===
            if show_filters:
                # === Campaign full width ===
                selected_campaign = st.selectbox(
                    "Campaign",
                    options=["All"] + sorted(campaigns_filtered["Campaign"].dropna().unique().tolist()),
                    index=0,
                    key="highlight_campaign"
                )

                # === Filters in a single row ===
                f1, f2, f3, f4 = st.columns([1, 2, 2, 2])  # Adjust widths as needed

                with f1:
                    selected_year = st.selectbox(
                        "Campaign Year",
                        ["All"] + sorted(campaigns_filtered["Campaign Year"].dropna().unique().tolist()),
                        key="year_filter"
                    )

                with f2:
                    selected_channel = st.selectbox(
                        "Tactic",
                        ["All"] + sorted(campaigns_filtered["Tactic"].dropna().unique().tolist()),
                        key="channel_filter"
                    )

                with f3:
                    selected_tactic_type = st.selectbox(
                        "Tactic Type",
                        ["All"] + sorted(campaigns_filtered["Tactic Type"].dropna().unique().tolist()),
                        key="tactic_type_filter"
                    )

                with f4:
                    selected_coop = st.selectbox(
                        "Cooperative Marketing",
                        ["All"] + sorted(campaigns_filtered["Cooperative Marketing"].dropna().unique().tolist()),
                        key="coop_filter"
                    )
            else:
                selected_campaign = selected_year = selected_channel = selected_tactic_type = selected_coop = "All"

            # === Apply filters ===
            campaigns_view = campaigns_filtered.copy()

            if st.session_state.region_filter != "All":
                campaigns_view = campaigns_view[campaigns_view["Region"] == st.session_state.region_filter]

            if selected_stage == "All":
                campaigns_view = campaigns_view[campaigns_view["Influence Window"] == "All"]
            else:
                campaigns_view = campaigns_view[campaigns_view["Influence Window"] == selected_stage]

            # Flag for highlight
            campaigns_view["is_highlighted"] = campaigns_view["Campaign"] == selected_campaign

            # If "All" is selected, don't filter ROI table, and turn off highlight flags
            if selected_campaign == "All":
                campaigns_view["is_highlighted"] = False

            if selected_year != "All":
                campaigns_view = campaigns_view[campaigns_view["Campaign Year"] == selected_year]

            if selected_channel != "All":
                campaigns_view = campaigns_view[campaigns_view["Tactic"] == selected_channel]

            if selected_tactic_type != "All":
                campaigns_view = campaigns_view[campaigns_view["Tactic Type"] == selected_tactic_type]

            if selected_coop != "All":
                campaigns_view = campaigns_view[campaigns_view["Cooperative Marketing"] == selected_coop]

            # ===== Prepare filtered table for ROI display =====
            roi_table_df = campaigns_view.copy()
            # 🟢 Filter ROI table based on selected tier (early!)
            if selected_tier != "All":
                roi_table_df = roi_table_df[roi_table_df["Tier Label"] == selected_tier]

            if selected_campaign != "All":
                roi_table_df = roi_table_df[roi_table_df["Campaign"] == selected_campaign]

            # Campaign table sorted by Tier Label
            table_cols = [
                "Campaign",
                "Tactic",
                "Attendees",
                "Account Engagements",
                "Opportunities",
                "Opportunity $",
                "Cost $",
                "ROI Ratio",
                "Tier Label",
            ]
            table_exists = [c for c in table_cols if c in roi_table_df.columns]

            # ---- Safe numeric sort key for Opportunity $ ----
            if "Opportunity $" in roi_table_df.columns:
                # Create a numeric copy for sorting; leaves original untouched for final formatting
                opp_numeric = pd.to_numeric(roi_table_df["Opportunity $"], errors="coerce")
            else:
                opp_numeric = None

            # Tier ordering then sort (use numeric opportunity for sorting if available)
            if "Tier Label" in roi_table_df.columns:
                tier_order = {"Invest": 0, "Refine": 1, "Reduce": 2, "ROI Unclear": 3}
                roi_table_df["TierRank"] = roi_table_df["Tier Label"].map(tier_order)

                if opp_numeric is not None:
                    roi_table_df = roi_table_df.assign(_opp_sort=opp_numeric).sort_values(
                        ["TierRank", "_opp_sort"], ascending=[True, False]
                    )
                else:
                    roi_table_df = roi_table_df.sort_values(["TierRank"])
            else:
                if opp_numeric is not None:
                    roi_table_df = roi_table_df.assign(_opp_sort=opp_numeric).sort_values(
                        "_opp_sort", ascending=False
                    )

            # Optional: drop helper column if it exists
            if "_opp_sort" in roi_table_df.columns:
                roi_table_df = roi_table_df.drop(columns="_opp_sort")

            st.markdown("#### ROI Summary Table")

            # Row coloring function by Tier Label
            def highlight_tier(row):
                if row["Tier Label"] == "Invest":
                    return ["background-color: #14532d; color: white;"] * len(row)  # Dark green
                elif row["Tier Label"] == "Refine":
                    return ["background-color: #9B870D; color: white;"] * len(row)  # Dark yellow/brown
                elif row["Tier Label"] == "Reduce":
                    return ["background-color: #7f1d1d; color: white;"] * len(row)  # Dark red
                else:
                    return ["background-color: #2c2c2c; color: white;"] * len(row)  # Default dark grey

            # Styled table with row colors
            styled_table = (
                roi_table_df[table_exists]
                .reset_index(drop=True)
                .style
                .apply(highlight_tier, axis=1)
                .format({
                    "ROI Ratio": "{:,.0f}",
                    "Opportunity $": "${:,.0f}",
                    "Cost $": "${:,.0f}"
                })
                .set_properties(**{"border-color": "black"})
            )

            st.dataframe(styled_table, use_container_width=True)

            # 💡 Add Markdown and Legend expander under Campaign ROI Table
            st.markdown(
                """
                *The bubble chart below shows the costs, opportunity $, and opportunity counts for different campaigns. Bubble Size = Opp Counts.*
                 """,
                unsafe_allow_html=True
            )
            with st.expander("ℹ️ See bubble chart details"):
                st.markdown(
                    """
                    - **Bubbles** represent campaigns.
                    - **Bubble Colors** represent Tier Labels. 
                    - **Tier Labels** are used to guide budget allocation. 
                        - 🟩 **Invest** = High ROI (high opp count and opp $, low cost)
                        - 🟨 **Refine** = Moderate ROI (medium opp count and opp $, medium cost) 
                        - 🟥 **Reduce** = Low ROI (low opp count and opp $, medium-high cost)
                    - *Note: Tier Label is based on performance across All Influence Windows (MGO + MIO + Won).*
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("#### ROI Bubble Chart")

            # 🟢 Filter ROI table based on selected tier
            if selected_tier != "All":
                roi_table_df = roi_table_df[roi_table_df["Tier Label"] == selected_tier]

            # Set default
            tier_title = None

            # --- Tier Filter ---
            if selected_tier != "All":
                # For chart title
                title_map = {
                    "Invest": "Invest Tier",
                    "Refine": "Refine Tier",
                    "Reduce": "Reduce Tier"
                }
                tier_title = title_map.get(selected_tier)

                selected_label = selected_tier
                campaigns_view = campaigns_view[campaigns_view["Tier Label"] == selected_label]

                # Background color
            #               if selected_label == "Invest":
            #                  bg_color = "rgba(0,128,0,0.5)"
            #               elif selected_label == "Refine":
            #                   bg_color = "rgba(255,215,0,0.5)"
            #               elif selected_label == "Reduce":
            #                   bg_color = "rgba(139,0,0,0.5)"

            # --- Influence Window Title ---
            if selected_stage == "All":
                influence_title = "All Influence Windows (MGO + MIO + Won)"
            else:
                influence_title = f"{selected_stage} Campaigns"

            # --- Final Bubble Title ---
            # Format region title
            region_title = "All Regions" if selected_region == "All" else selected_region

            # Construct title (exclude tier from title)
            bubble_title = f"{influence_title} – {region_title}"

            campaigns_view["Opportunity $"] = (
                campaigns_view["Opportunity $"]
                .replace('[\$,]', '', regex=True)
                .astype(float)
            )

            # --- Render Chart ---
            if campaigns_view.empty:
                st.warning("No data available for the selected filters.")
            else:
                bubble_fig = create_bubble_chart(campaigns_view, title=bubble_title,
                                                 selected_campaign=selected_campaign)
                st.plotly_chart(bubble_fig, use_container_width=True)

            # Section spacing without a line
            st.markdown(
                "<div style='margin-top: 40px; margin-bottom: 30px;'></div>",
                unsafe_allow_html=True
            )

            # ===================== Text-Based Recommendations for Tab 3 =====================

            # CSS for aligned lists
            st.markdown("""
                        <style>
                        ul.recs-open, ul.recs-close {
                          margin: 0.25rem 0 1rem 1.25rem;
                          padding-left: 1.25rem;
                          list-style-position: outside;
                        }
                        ul.recs-open li, ul.recs-close li {
                          margin: 0.35rem 0;
                        }
                        </style>
                        """, unsafe_allow_html=True)

            # ---------- Aliases to your sheets ----------
            df1_mix = seg_mix  # Tab 1: segment_recommendations_mix
            df2_pods = pod_details  # Tab 2: pod_account_type_details
            df3_src = campaign  # Tab 3: campaign_effectiveness (has Tier Label)
            df4_src = campaign_accounts  # Tab 4: campaign_opps_accounts

            # ---------- Current selections from state ----------
            selected_region = st.session_state.get("region_filter", "All")
            selected_acct = st.session_state.get("acct_type_filter", "All")  # NOTE: acct_type_filter
            selected_pod = st.session_state.get("pod_filter")  # e.g., "Pod 1" or "Enterprise East - Pod 2"
            selected_persona = st.session_state.get("selected_persona", "All")  # "Executive"/"Technical"/"All"

            # ---------- Build df_use with a robust Tier merge ----------
            def _canon_cols(df: pd.DataFrame) -> pd.DataFrame:
                out = df.copy()
                out.columns = [c.strip() for c in out.columns]
                return out

            df4 = _canon_cols(df4_src)
            df3 = _canon_cols(df3_src)

            # Extract Tier Label from Tab 3, coalescing if needed
            tier_col = next((c for c in df3.columns if c.strip().lower() == "tier label"), None)
            if tier_col is None:
                st.error("Tier Label column not found in Tab 3 (campaign_effectiveness).")
                tier_col = "Tier Label"

            df3_tier = df3[["Campaign", tier_col]].rename(columns={tier_col: "Tier Label"})
            df = df4.merge(df3_tier, on="Campaign", how="left", suffixes=("_tab4", "_tab3"))
            if "Tier Label" not in df.columns:
                cands = [c for c in df.columns if c.strip().lower() == "tier label"]
                if cands:
                    df.rename(columns={cands[0]: "Tier Label"}, inplace=True)
            df["Tier Label"] = df["Tier Label"].fillna("Refine")

            # Apply Region/Acct filters once
            df_use = df.copy()
            if selected_region != "All":
                df_use = df_use[df_use["Region"] == selected_region]
            if selected_acct != "All":
                df_use = df_use[df_use["Account Type"] == selected_acct]

            # ===================== Scoring & selection helpers =====================
            TIER_WEIGHT = {"Invest": 1.0, "Refine": 0.5, "Reduce": 0.0}

            def _any_ttype_match(val: str, targets: list[str]) -> int:
                """Case-insensitive exact-or-substring match; falls back to family (Event/Webinar/Tradeshow)."""
                if not targets:
                    return 0
                v = str(val or "").lower()
                for t in targets:
                    t_ = str(t or "").lower().strip()
                    if not t_:
                        continue
                    if v == t_ or (t_ in v) or (v in t_):
                        return 1
                fam_v = v.split(" - ", 1)[0].strip()
                for t in targets:
                    fam_t = str(t or "").lower().split(" - ", 1)[0].strip()
                    if fam_v and fam_t and fam_v == fam_t:
                        return 1
                return 0

            def compute_match_score(
                    rows: pd.DataFrame,
                    selected_region: str,
                    selected_acct: str,
                    intent: str,
                    preferred_ttypes: Optional[list] = None,
            ) -> pd.DataFrame:
                """Intent='MGO' (open) or 'CLOSE' (MIO/Won). Includes Tactic Type alignment."""
                dfm = rows.copy()
                dfm["region_match"] = (selected_region == "All") | (dfm["Region"] == selected_region)
                dfm["acct_match"] = (selected_acct == "All") | (dfm["Account Type"] == selected_acct)
                dfm["intent_match"] = (dfm["Influence Window"] == "Pre-Open Influence") if intent == "Pre-Open Influence" else dfm[
                    "Influence Window"].isin(["Post-Open Influence", "Won"])
                if preferred_ttypes is None:
                    preferred_ttypes = []
                dfm["tactic_match"] = dfm["Tactic Type"].apply(lambda x: _any_ttype_match(x, preferred_ttypes))

                # cast to numeric
                dfm["region_match"] = dfm["region_match"].astype(int)
                dfm["acct_match"] = dfm["acct_match"].astype(int)
                dfm["intent_match"] = dfm["intent_match"].astype(int)
                dfm["tactic_match"] = dfm["tactic_match"].astype(int)
                dfm["tier_weight"] = dfm["Tier Label"].map(TIER_WEIGHT).fillna(0.0)

                opp_max = dfm["Total Opps"].max() or 1
                dfm["opp_norm"] = dfm["Total Opps"] / opp_max

                # Rebalanced weights to include tactic alignment
                dfm["Match Score"] = (
                        1.00 * dfm["region_match"] +
                        0.90 * dfm["acct_match"] +
                        0.80 * dfm["intent_match"] +
                        0.70 * dfm["tactic_match"] +
                        0.60 * dfm["tier_weight"] +
                        0.30 * dfm["opp_norm"]
                )
                return dfm

            def parse_commalist(text) -> list[str]:
                if pd.isna(text) or not str(text).strip():
                    return []
                return [t.strip() for t in str(text).split(",") if t.strip()]

            # UNIQUE by Campaign while honoring family counts (Event/Webinar/Tradeshow)
            def take_top_by_mix_unique(df_scored: pd.DataFrame, mix_dict: dict) -> pd.DataFrame:
                picks, used_campaigns = [], set()
                need_total = sum(mix_dict.values())
                for family, n in mix_dict.items():
                    if n <= 0:
                        continue
                    sub = df_scored[
                        (~df_scored["Campaign"].isin(used_campaigns)) &
                        (df_scored["Tactic"].str.contains(family, case=False, na=False))
                        ].sort_values(["Match Score", "Total Opps"], ascending=False)
                    chosen = sub.drop_duplicates(subset=["Campaign"], keep="first").head(n)
                    if not chosen.empty:
                        picks.append(chosen)
                        used_campaigns.update(chosen["Campaign"].tolist())
                have = sum(len(p) for p in picks)
                if have < need_total:
                    backfill = (
                        df_scored[~df_scored["Campaign"].isin(used_campaigns)]
                        .sort_values(["Match Score", "Total Opps"], ascending=False)
                        .drop_duplicates(subset=["Campaign"], keep="first")
                        .head(need_total - have)
                    )
                    if not backfill.empty:
                        picks.append(backfill)
                return (
                    pd.concat(picks, ignore_index=True)
                    if picks else
                    df_scored.sort_values(["Match Score", "Total Opps"], ascending=False)
                    .drop_duplicates(subset=["Campaign"], keep="first")
                    .head(need_total)
                )

            def rec_types_by_pod(df2_pods: pd.DataFrame, region: str) -> OrderedDict:
                """OrderedDict[pod -> [tactic types]] for the region."""
                cols = [c.strip() for c in df2_pods.columns]
                dfp = df2_pods.copy()
                dfp.columns = cols
                # infer columns
                col_region = next((c for c in dfp.columns if c.lower() == "region"), None)
                col_pod = next((c for c in dfp.columns if c.lower() in ("pod", "pod id", "pod_name", "pod segment")),
                               None)
                col_types = next(
                    (c for c in dfp.columns if c.lower() in ("recommended tactic type", "recommended tactic types")),
                    None)
                if not (col_region and col_pod and col_types):
                    return OrderedDict()
                dfp = dfp if region == "All" else dfp[dfp[col_region] == region]
                if dfp.empty:
                    return OrderedDict()
                dfp = dfp[[col_pod, col_types]].copy()
                dfp[col_types] = dfp[col_types].astype(str).str.split(",")
                dfp = dfp.explode(col_types)
                dfp[col_types] = dfp[col_types].str.strip()
                out = OrderedDict()
                for pod, grp in dfp.groupby(col_pod):
                    # 🚫 Skip placeholder pods
                    if str(pod).strip().lower() in ("no pod selected", "none", "all"):
                        continue
                    types = [t for t in grp[col_types].dropna().tolist() if t]
                    out[str(pod)] = list(dict.fromkeys(types))  # unique while preserving order
                return out

            def pick_top_for_type(df_scored: pd.DataFrame, tactic_type: str, used_campaigns: set) -> Optional[
                pd.Series]:
                """Pick top row for a specific tactic type with family fallback."""
                cand = df_scored[~df_scored["Campaign"].isin(used_campaigns)]
                if cand.empty:
                    return None
                req = str(tactic_type).strip()
                exact = cand[cand["Tactic Type"].str.lower() == req.lower()]
                pool = exact if not exact.empty else cand[cand["Tactic Type"].str.contains(req, case=False, na=False)]
                if pool.empty:
                    fam = req.split(" - ", 1)[0].strip()
                    pool = cand[cand["Tactic"].str.contains(fam, case=False, na=False)]
                if pool.empty:
                    return None
                return pool.sort_values(["Match Score", "Total Opps"], ascending=False).iloc[0]

            # ===================== Renderer (uses persona-aware Tab 1 lookup + tactic scoring) =====================
            def render_tab3_recommendations():
                # Re-read state in case user changed filters
                selected_region = st.session_state.get("region_filter", "All")
                selected_acct = st.session_state.get("acct_type_filter", "All")
                selected_pod = st.session_state.get("pod_filter")
                selected_persona = st.session_state.get("selected_persona", "All")

                # --- Robust Tab 1 row lookup (Region + Account Type, optionally Persona) ---
                df1 = df1_mix.copy()
                df1.columns = [c.strip() for c in df1.columns]
                col_region = next((c for c in df1.columns if c.lower() == "region"), None)
                col_acct = next((c for c in df1.columns if c.lower() == "account type"), None)
                col_persona = next((c for c in df1.columns if c.lower() in ("persona", "persona type")), None)

                row_tab1 = pd.DataFrame()
                if col_region and col_acct and selected_region != "All" and selected_acct != "All":
                    mask = (df1[col_region] == selected_region) & (df1[col_acct] == selected_acct)
                    if col_persona and selected_persona != "All":
                        mask = mask & (df1[col_persona] == selected_persona)
                    row_tab1 = df1.loc[mask].head(1)

                def _safe_int(x):
                    try:
                        return int(x)
                    except:
                        return 0

                if not row_tab1.empty:
                    r = row_tab1.iloc[0]
                    mix_dict = {
                        "Event": _safe_int(r.get("Rec TM Events", 0)),
                        "Webinar": _safe_int(r.get("Rec Webinars", 0)),
                        "Tradeshow": _safe_int(r.get("Rec Tradeshows", 0)),
                    }
                    # Persona-specific tactic types if present; else generic
                    persona_col_map = {
                        "Executive": "Recommended Tactic Types (Executive)",
                        "Technical": "Recommended Tactic Types (Technical)",
                    }
                    persona_col = persona_col_map.get(selected_persona)
                    if persona_col and persona_col in df1.columns:
                        open_types = parse_commalist(r.get(persona_col))
                    else:
                        open_types = parse_commalist(r.get("Recommended Tactic Types"))
                else:
                    mix_dict = {"Event": 3, "Webinar": 2, "Tradeshow": 1}
                    open_types = []
                    st.caption(
                        "⚠️ Using default Recommended Mix because no exact Tab 1 row matched the current Region/Account Type/Persona.")

                # --- OPEN (MGO) with tactic-type scoring ---
                open_base = df_use[df_use["Influence Window"] == "Pre-Open Influence"]
                open_scored = compute_match_score(
                    open_base, selected_region, selected_acct, intent="Pre-Open Influence", preferred_ttypes=open_types
                )
                open_picks = take_top_by_mix_unique(open_scored, mix_dict) \
                    .sort_values(["Match Score", "Total Opps"], ascending=False)

                # --- CLOSE (MIO + Won) with tactic-type scoring ---
                close_base = df_use[df_use["Influence Window"].isin(["Post-Open Influence", "Won"])]
                # Preferred types come from Tab 2: selected pod if available, else union across region pods
                by_pod = rec_types_by_pod(df2_pods, selected_region)  # OrderedDict[pod -> [types]]
                if selected_pod and str(selected_pod) in by_pod:
                    close_pref = by_pod[str(selected_pod)]
                else:
                    # union across pods (preserve order)
                    seen, close_pref = set(), []
                    for types in by_pod.values():
                        for t in types:
                            if t not in seen:
                                seen.add(t)
                                close_pref.append(t)

                close_scored = compute_match_score(
                    close_base, selected_region, selected_acct, intent="CLOSE", preferred_ttypes=close_pref
                )

                # Exactly one campaign per pod in region (selected pod first), then others
                pod_order = list(by_pod.keys())
                if selected_pod and str(selected_pod) in pod_order:
                    pod_order = [str(selected_pod)] + [p for p in pod_order if str(p) != str(selected_pod)]
                target_close_count = len(pod_order) if pod_order else 4  # fallback 4 if no pods found

                used = set()
                close_items_li = []  # already formatted <li> strings

                def fmt_close_li(row, suffix=""):
                    return f"<li><span style='color:#FF2400'><b>{row['Campaign']}</b></span> — {row['Tactic Type']}{(' ' + suffix) if suffix else ''}</li>"

                # 1) Try to pick one per pod by that pod's recommended types
                for pod in pod_order:
                    types_for_pod = by_pod.get(str(pod), [])
                    pick = None
                    for ttype in types_for_pod:
                        cand = pick_top_for_type(close_scored, ttype, used)
                        if cand is not None:
                            pick = cand
                            break
                    # If no match for that pod's types, take best remaining overall
                    if pick is None:
                        remaining = close_scored[~close_scored["Campaign"].isin(used)]
                        if not remaining.empty:
                            pick = remaining.sort_values(["Match Score", "Total Opps"], ascending=False).iloc[0]
                    if pick is not None:
                        used.add(pick["Campaign"])
                        suffix = f"(best for {pod})"
                        close_items_li.append(fmt_close_li(pick, suffix))
                    if len(close_items_li) >= target_close_count:
                        break

                # 2) Backfill if still short (in case some pods had no options)
                if len(close_items_li) < target_close_count:
                    remaining = close_scored[~close_scored["Campaign"].isin(used)] \
                        .sort_values(["Match Score", "Total Opps"], ascending=False)
                    for _, r in remaining.iterrows():
                        close_items_li.append(fmt_close_li(r))
                        used.add(r["Campaign"])
                        if len(close_items_li) >= target_close_count:
                            break

                # --- Render text output ---
                # --- OPEN Opps header with tooltip ---
                st.markdown(
                    "<h3><span style='color:#39FF14'>◆</span> Recommended Campaigns to Open Opps "
                    "<span title='You may see differences in tactic types here compared to Tab 1. "
                    "That’s because Tab 1 shows tactic types predicted by the AI model as most likely to open opps, "
                    "while this list is based on actual historical opp counts for your chosen segment.'>ℹ️</span></h3>",
                    unsafe_allow_html=True
                )
                open_mix_value = ", ".join(f"{v} {k}" for k, v in mix_dict.items() if v > 0)
                st.caption(
                    f"We’ve highlighted the top campaigns for {selected_acct} within {selected_region}. "
                    f"We select exactly the number of campaigns specified by Tab 1’s Recommended Mix ({open_mix_value})."
                )
                if open_picks.empty:
                    st.info("No Pre-Open Influence-aligned campaigns found for the current filters.")
                else:
                    open_items = [
                        f"<li><span style='color:#39FF14'><b>{r['Campaign']}</b></span> — {r['Tactic Type']}</li>"
                        for _, r in open_picks.iterrows()
                    ]
                    st.markdown("<ul class='recs-open'>" + "".join(open_items) + "</ul>", unsafe_allow_html=True)

                # Close header + caption (show actual selected_pod if set; else 'All')
                pod_label = selected_pod if (selected_pod is not None and str(selected_pod).strip()) else "All"
                st.markdown(
                    "<h3><span style='color:#FF2400'>◆</span> Recommended Campaigns to Close Opps "
                    "<span title='You may see differences in tactic types here compared to Tab 2. "
                    "That’s because Tab 2 shows tactic types with the highest win rates overall, "
                    "while this list is based on actual historical opp counts for Post-Open Influence and Won opportunities.'>ℹ️</span></h3>",
                    unsafe_allow_html=True
                )
                st.caption(
                    f"We’ve highlighted the top campaign for {selected_acct} within your selected Pod ({pod_label}), "
                    f"and top-performing campaigns across other Pods in {selected_region} for full coverage."
                )
                st.markdown("<ul class='recs-close'>" + "".join(close_items_li) + "</ul>", unsafe_allow_html=True)

            # ===================== Button under the bubble chart (inside Tab 3 `else:`) =====================
            st.divider()
            col_btn, _ = st.columns([2, 3])  # make button a bit wider without full width
            with col_btn:
                if st.button("Select to View Recommended Campaigns", key="view_recs_btn_tab3"):
                    st.session_state["show_recs_tab3"] = True

            if st.session_state.get("show_recs_tab3"):
                render_tab3_recommendations()


if __name__ == "__main__":
    main()


