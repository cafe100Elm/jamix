import streamlit as st
import pandas as pd
import re

# --- 1. MenuSync Design Language ---
st.set_page_config(page_title="Jamix Allergen Review", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #fdfaf6; }
    h1, h2, h3 { color: #c25e44 !important; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #f4f1ea !important; }
    
    /* The 'MenuSync' Terracotta Tag */
    .keyword-tag {
        display: inline-block;
        background-color: #c25e44;
        color: white;
        padding: 4px 10px;
        margin: 4px;
        border-radius: 6px;
        font-size: 0.85em;
        font-weight: 500;
    }
    .product-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #c25e44;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Logic (Directly from Jeremy's Replit) ---
def clean_ingredients(text):
    if pd.isna(text): return []
    text = re.sub(r'[\(\)\[\]]', '', str(text))
    parts = re.split(r'[,;/]+', text)
    return [p.strip().title() for p in parts if p.strip()]

def load_search_terms(df):
    allergen_dict = {}
    for col in df.columns:
        terms = []
        for val in df[col].dropna():
            terms += [t.strip().lower() for t in re.split(r'[,;/\n]+', str(val)) if t.strip()]
        allergen_dict[col] = list(set(terms))
    return allergen_dict

def detect_allergens(ingredients, allergen_dict):
    found = {}
    joined = " ".join(ingredients).lower()
    for allergen, terms in allergen_dict.items():
        hits = []
        for t in terms:
            # Jeremy's exclusion logic for Natto/Nuts
            if t == "nut" and ("nutrition" in joined or "chestnut" in joined): continue
            if t == "natto" and "annatto" in joined: continue
            if t in joined: hits.append(t)
        if hits: found[allergen] = hits
    return found

# --- 3. UI Implementation ---
st.title("🥗 Jamix Allergen Review")

with st.sidebar:
    st.header("📂 Data Import")
    uploaded = st.file_uploader("Upload Jamix Excel", type=["xlsx"])
    if uploaded:
        search_df = pd.read_excel(uploaded, sheet_name='Search')
        review_df = pd.read_excel(uploaded, sheet_name='Review')
        allergen_map = load_search_terms(search_df)
        st.success(f"Processed {len(review_df)} items")
        
        search_query = st.text_input("🔍 Search Products")
        sort_order = st.radio("Sort", ["A-Z", "Z-A"])

if not uploaded:
    st.info("Please upload your Excel file to begin.")
else:
    # Filter and Sort
    df_display = review_df.copy()
    if search_query:
        df_display = df_display[df_display['nutritive value name'].str.contains(search_query, case=False, na=False)]
    df_display = df_display.sort_values('nutritive value name', ascending=(sort_order == "A-Z"))

    # Display results in the MenuSync Card Style
    for _, row in df_display.iterrows():
        ingredients = clean_ingredients(row.get('ingredients', ''))
        found_allergens = detect_allergens(ingredients, allergen_map)
        
        with st.container():
            st.markdown(f"""
            <div class="product-card">
                <div style="font-size: 1.1em; font-weight: bold; color: #2d2d2d;">{row['nutritive value name']}</div>
                <div style="font-size: 0.8em; color: #666; margin-bottom: 8px;">Stock Card: {row.get('stock card', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if found_allergens:
                for alg, hits in found_allergens.items():
                    tags = "".join([f'<span class="keyword-tag">{h}</span>' for h in hits])
                    st.markdown(f"**{alg}**: {tags}", unsafe_allow_html=True)
            else:
                st.write("✅ No allergens flagged.")
            st.divider()
