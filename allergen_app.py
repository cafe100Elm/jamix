import streamlit as st
import pandas as pd
import re

# Page setup
st.set_page_config(page_title="Allergen Review App", layout="wide", initial_sidebar_state="expanded")

# --- Helper functions ---
def clean_ingredients(text):
    if pd.isna(text):
        return []
    text = re.sub(r'[\(\)\[\]]', '', str(text))
    parts = re.split(r'[,;/]+', text)
    return [p.strip().title() for p in parts if p.strip()]

def load_search_terms(df):
    allergen_dict = {}
    for col in df.columns:
        all_terms = []
        for val in df[col].dropna():
            terms = re.split(r'[,;/\n]+', str(val))
            all_terms += [t.strip().lower() for t in terms if t.strip()]
        allergen_dict[col] = list(set(all_terms))
    return allergen_dict

def detect_allergens(ingredients, allergen_dict):
    found = {}
    joined = " ".join(ingredients).lower()
    for allergen, terms in allergen_dict.items():
        hits = []
        for t in terms:
            if t == "nut" and ("nutrition" in joined or "chestnut" in joined):
                continue
            if t == "natto" and "annatto" in joined:
                continue
            if t in joined:
                hits.append(t)
        found[allergen] = hits
    return found

# --- UI ---
st.markdown(
    "<h3 style='font-weight:400; margin-bottom:5px;'>🥗 Allergen Review Tool</h3>",
    unsafe_allow_html=True
)

with st.sidebar:
    st.markdown("### 📂 Upload & Navigate")
    uploaded = st.file_uploader("Upload Excel file", type=["xlsx"], label_visibility="collapsed")
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] { width: 380px !important; }
            section[data-testid="stFileUploadDropzone"] > div:first-child > div:first-child > div { display: none; }
            section[data-testid="stFileUploadDropzone"] [data-testid="stMarkdownContainer"] { display: none; }
            section[data-testid="stFileUploadDropzone"] small { display: none; }
            section[data-testid="stFileUploadDropzone"] button[kind="secondary"] { display: none; }
            .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
            .stTextInput { margin-bottom: -10px !important; }
            .stSelectbox { margin-bottom: 5px !important; }
            .nutritive-small {
                font-size: 1.0375em; color: #2d2d2d; font-weight: 600;
                white-space: normal; line-height: 1.4; max-width: 96vw; display: block;
                overflow-wrap: break-word;
            }
            .nutritive-dropdown {
                font-size: 0.975em !important; max-width: 23vw !important; letter-spacing: -.01em;
            }
            .stockcard-tiny {
                font-size: 0.94em; color: #666; font-style: italic;
                white-space: normal; max-width: 97vw; display: block; margin-bottom: 3px;
            }
            .ingredient-tag {
                background-color:#e8f5e9; padding:2px 6px; margin:1px; border-radius:8px;
                display:inline-block; font-size:0.8em;
            }
            .orig-ingr-box {
                background-color:#f0f0f0; border-radius:6px; padding:7px 9px;
                font-family:monospace; font-size:0.82em; margin-top:12px; margin-bottom:8px;
                word-break:break-word; line-height: 1.4;
            }
            .allergen-count-pad {
                margin-bottom: 8px;
            }
            .stMarkdown {
                margin-bottom: 0.3rem !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    if uploaded:
        search_df = pd.read_excel(uploaded, sheet_name="Search")
        review_df = pd.read_excel(uploaded, sheet_name="Review")
        review_df.columns = review_df.columns.str.strip().str.lower()
        allergen_dict = load_search_terms(search_df)
        review_df = review_df[
            (review_df.get("nutritive value name", "").astype(str).str.strip() != "") |
            (review_df.get("stock card", "").astype(str).str.strip() != "") |
            (review_df.get("id", "").astype(str).str.strip() != "")
        ]
        products = review_df.to_dict(orient="records")
        if not products:
            st.error("No valid products found.")
            st.stop()
        all_names = [str(p.get("nutritive value name", "")) for p in products]
        sort_cols = st.columns(2)
        with sort_cols[0]:
            if st.button("A-Z", key="sort_az", use_container_width=True): st.session_state["sort_method"] = "A-Z"
        with sort_cols[1]:
            if st.button("Z-A", key="sort_za", use_container_width=True): st.session_state["sort_method"] = "Z-A"
        method = st.session_state.get("sort_method", "A-Z")
        if method == "Z-A":
            sorted_names = sorted(all_names, key=lambda x: x.lower(), reverse=True)
        else:
            sorted_names = sorted(all_names, key=lambda x: x.lower())
        st.markdown("### 🔎 Select Item")
        search_query = st.text_input("search_box", "", placeholder="Search by Nutritive Value Name", label_visibility="collapsed").lower().strip()
        filtered_names = [
            name for name in sorted_names if search_query in name.lower()
        ] if search_query else sorted_names
        if not filtered_names:
            st.warning("No matches found.")
            st.stop()
        search_name = st.selectbox(
            "",
            options=filtered_names,
            format_func=lambda x: f"{x[:90]}..." if len(x) > 90 else x,
            key="select_product"
        )
        current_index = filtered_names.index(search_name)
    else:
        st.info("Upload an Excel file to begin.")
        products = None

if uploaded and products:
    product = next((p for p in products if str(p.get("nutritive value name", "")) == str(search_name)), None)
    nutritive = product.get("nutritive value name", "")
    stock_card = product.get("stock card", product.get("stock_card", ""))
    ingredients_raw = str(product.get("ingredients", "")).strip()
    ingredients = clean_ingredients(ingredients_raw)
    ingredient_count = len(ingredients)
    found = detect_allergens(ingredients, allergen_dict)
    allergen_count = sum(1 for hits in found.values() if hits)
    status_icon = "⚠️" if allergen_count > 0 else "✓"

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; background: #f7f7f7; padding: 10px 15px; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.07);">
            <div style="flex:1;">
                <div class="nutritive-small">{nutritive}</div>
                <div class="stockcard-tiny"><b>Stock Card.</b> {stock_card}</div>
                <div class="orig-ingr-box">{ingredients_raw}</div>
            </div>
            <div style="text-align: right; min-width: 82px;">
                <div style="font-size: 1.8em;">{status_icon}</div>
                <div class="allergen-count-pad" style="font-size: 0.8em; color: #666;">{allergen_count} allergen(s)</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        " ".join(
            [f"<span class='ingredient-tag'>{ing}</span>" for ing in ingredients]
        ),
        unsafe_allow_html=True,
    )

    st.markdown("<hr style='margin:10px 0 8px 0; border:0; border-top:1px solid #ddd;'>", unsafe_allow_html=True)
    num_cols = 3
    cols = st.columns(num_cols)
    for i, (allergen, hits) in enumerate(found.items()):
        with cols[i % num_cols]:
            if hits:
                st.markdown(f"<div style='margin-bottom:4px;'>✅ <b>{allergen}</b><br><span style='font-size:0.75em; color:green;'>{', '.join(hits)}</span></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='margin-bottom:4px;'>❌ <b>{allergen}</b></div>", unsafe_allow_html=True)
    st.caption(f"Item {current_index + 1} of {len(filtered_names)}")
else:
    if not uploaded:
        st.stop()
