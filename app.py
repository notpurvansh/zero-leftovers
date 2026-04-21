import streamlit as st
import requests

# --- ⚙️ CONFIG & SECRETS ---
API_KEY = st.secrets["SPOON_KEY"]

# --- 🎨 UI CONFIGURATION ---
st.set_page_config(page_title="Zero Leftovers", page_icon="🥗", layout="wide")

# Custom CSS for a unique look
st.markdown("""
    <style>
    .main { background: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .recipe-card { border: 1px solid #e1e4e8; border-radius: 15px; padding: 20px; background: white; transition: 0.3s; }
    .recipe-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 🛠️ SIDEBAR: MORE OPTIONS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2329/2329903.png", width=100)
    st.title("Settings")
    
    st.subheader("🎯 Preferences")
    diet = st.selectbox("Dietary Plan", ["None", "Vegetarian", "Vegan", "Gluten Free", "Ketogenic"])
    
    st.subheader("⚖️ Waste Control")
    max_missing = st.slider("Max missing ingredients allowed", 0, 5, 2)
    
    st.divider()
    st.info("Zero Leftovers uses AI to scan your fridge and find the most efficient recipes.")

# --- 🏠 MAIN PAGE ---
st.title("🥗 Zero Leftovers")
st.write("### *Turn your fridge 'scraps' into a gourmet meal.*")

# Layout: Two columns for input and dashboard
top_col1, top_col2 = st.columns([2, 1])

with top_col1:
    uploaded_file = st.file_uploader("📸 Snap a photo of your ingredients", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 🧠 PROCESS IMAGE
    analyze_url = f"https://api.spoonacular.com/food/images/analyze?apiKey={API_KEY}"
    files = {"file": ("image.jpg", uploaded_file.getvalue(), "image/jpeg")}
    
    with st.spinner("✨ AI is scanning your ingredients..."):
        try:
            res = requests.post(analyze_url, files=files).json()
            
            # Extract Ingredients
            detected = [i["name"] for i in res.get("category", {}).get("ingredients", [])]
            if not detected and "category" in res: detected = [res["category"]["name"]]
            
            if detected:
                query = ",".join(detected)
                
                # 📊 Dashboard Metrics
                with top_col2:
                    st.metric(label="Ingredients Found", value=len(detected))
                    st.success(f"Recognized: {', '.join([d.capitalize() for d in detected])}")

                # 🍳 FIND RECIPES
                # Using additional filters from sidebar (diet)
                diet_query = f"&diet={diet.lower()}" if diet != "None" else ""
                recipe_url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={query}&number=6&ranking=2&ignorePantry=true{diet_query}&apiKey={API_KEY}"
                
                recipes = requests.get(recipe_url).json()
                
                if recipes:
                    st.divider()
                    st.subheader("🔥 Top Matches for You")
                    
                    # Display in a responsive grid
                    grid_cols = st.columns(3)
                    
                    for idx, r in enumerate(recipes):
                        # Filter based on "Max Missing" slider
                        if r['missedIngredientCount'] <= max_missing:
                            with grid_cols[idx % 3]:
                                with st.container():
                                    st.image(r['image'], use_container_width=True)
                                    st.markdown(f"#### {r['title']}")
                                    
                                    # Sustainability Badge
                                    if r['missedIngredientCount'] == 0:
                                        st.markdown("🏆 **PERFECT MATCH**")
                                    else:
                                        st.write(f"Needs {r['missedIngredientCount']} extra items")
                                    
                                    # Expand for Details
                                    with st.expander("View Recipe Details"):
                                        info_url = f"https://api.spoonacular.com/recipes/{r['id']}/information?apiKey={API_KEY}"
                                        info = requests.get(info_url).json()
                                        st.write(f"⏱️ **Time:** {info.get('readyInMinutes')} mins")
                                        st.write(f"🥦 **Healthy Score:** {info.get('healthScore')}/100")
                                        st.link_button("Start Cooking 👩‍🍳", info.get('sourceUrl'))
                else:
                    st.warning("No recipes found matching your dietary filters!")
            else:
                st.error("Couldn't identify any ingredients. Try a clearer photo!")
        except Exception as e:
            st.error("There was an issue connecting to the AI. Check your API key!")

else:
    # Home State: Helpful Tips
    st.divider()
    st.write("#### 💡 How to get the best results:")
    c1, c2, c3 = st.columns(3)
    c1.info("📷 **Clear Photos**\nAvoid blurry images for better AI detection.")
    c2.warning("🥑 **One by One**\nGrouping 2-3 main items works best.")
    c3.success("♻️ **Zero Waste**\nUse the slider to see recipes with zero missing items.")
