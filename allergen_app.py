import streamlit as st
import pandas as pd
import re

# --- 1. Page Setup & MenuSync Design Language ---
st.set_page_config(page_title="Jamix Allergen Review", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* MenuSync Background & Typography */
    .stApp { background-color: #fdfaf6; }
    h1, h2, h3, h4 { color: #c25e44 !important; font-family: 'Inter', sans-serif; }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] { background-color: #f4f1ea !important; width: 380px !important; }
    
    /* Replit Tag Styles with MenuSync Terracotta */
    .keyword-tag {
        display: inline-block;
        background-color: #c25e44;
        color: white;
        padding: 4px 8px;
        margin: 3px;
        border-radius: 4px;
        font-size: 0.9em;
        font-weight: 500;
    }
    
    /* Table & Card styling */
    .stTable { background-color: white; border-radius: 8px; }
    .nutritive-small { font-size: 1.05em; color: #2d2d2d; font-weight: 600; line-height: 1.4; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Core Logic (Preserved from Replit) ---
def clean_ingredients(text):
    if pd.isna(text): return []
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
            if t == "nut" and ("nutrition" in joined or "chestnut" in joined): continue
            if t == "natto" and "annatto" in joined: continue
            if t in joined: hits.append(t)
        if hits: found[allergen] = hits
    return found

# --- 3. UI Implementation ---
st.markdown("### 🥗 Allergen Review Tool")

with st.sidebar:
    st.markdown("### 📂 Data Import")
    uploaded = st.file_uploader("Upload Excel file", type=["xlsx"], label_visibility="collapsed")
    
    if uploaded:
        try:
            # Load data from Replit's expected sheets
            search_df = pd.read_excel(uploaded, sheet_name='Search')
            review_df = pd.read_excel(uploaded, sheet_name='Review')
            allergen_map = load_search_terms(search_df)
            
            st.success(f"Loaded {len(review_df)} products")
            
            # Search & Filter Sidebar UI
            search_query = st.text_input("🔍 Search Products", "")
            sort_order = st.selectbox("Sort Order", ["A-Z", "Z-A"])
        except Exception as e:
            st.error(f"Error loading sheets: {e}")
            uploaded = None

if not uploaded:
    st.info("Welcome, Jeremy. Please upload your Jamix export in the sidebar.")
else:
    # Filter Logic
    df_display = review_df.copy()
    if search_query:
        df_display = df_display[df_display['nutritive value name'].str.contains(search_query, case=False, na=False)]
    
    df_display = df_display.sort_values('nutritive value name', ascending=(sort_order == "A-Z"))

    # Display Results as "Cards"
    for _, row in df_display.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown(f"<span class='nutritive-small'>{row['nutritive value name']}</span>", unsafe_allow_html=True)
                st.caption(f"Stock Card: {row.get('stock card', 'N/A')}")
            
            with col2:
                ingredients = clean_ingredients(row.get('ingredients', ''))
                found_allergens = detect_allergens(ingredients, allergen_map)
                
                if found_allergens:
                    for alg, terms in found_allergens.items():
                        st.markdown(f"**{alg}:** " + " ".join([f"<span class='keyword-tag'>{t}</span>" for t in terms]), unsafe_allow_html=True)
                else:
                    st.write("✅ No allergens detected")
            st.divider()
