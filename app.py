import streamlit as st
import requests

# --- ⚙️ CONFIG ---
# Get your key at: https://spoonacular.com/food-api/console
API_KEY = st.secrets["SPOON_KEY"]

st.set_page_config(page_title="Zero Leftovers", page_icon="🥗")

# --- 🎨 UI STYLING ---
st.title("🥗 Zero Leftovers")
st.markdown("### *Your photo, our recipes. No food wasted.*")
st.divider()

# --- 📸 STEP 1: UPLOAD ---
uploaded_file = st.file_uploader("Upload a photo of your ingredients", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Display the image nicely
    st.image(uploaded_file, caption="Scanning your fridge...", width=400)
    
    # --- 🧠 STEP 2: SPOONACULAR IMAGE ANALYSIS ---
    # We send the image to find the names of the food items
    analyze_url = f"https://api.spoonacular.com/food/images/analyze?apiKey={API_KEY}"
    files = {"file": ("image.jpg", uploaded_file.getvalue(), "image/jpeg")}
    
    with st.spinner("AI is thinking..."):
        try:
            # 1. Image Recognition Call
            response = requests.post(analyze_url, files=files)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract detected ingredients (handling different response formats)
                found_ingredients = []
                if "category" in data and "ingredients" in data["category"]:
                    found_ingredients = [i["name"] for i in data["category"]["ingredients"]]
                
                # If list is empty, try the general category name
                if not found_ingredients and "category" in data:
                    found_ingredients = [data["category"]["name"]]

                if found_ingredients:
                    query = ",".join(found_ingredients)
                    st.success(f"Detected: **{query.replace(',', ', ')}**")
                    
                    # --- 🍳 STEP 3: FIND RECIPES (The Heart of Zero Leftovers) ---
                    # ranking=2 minimizes missing ingredients
                    recipe_url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={query}&number=5&ranking=2&apiKey={API_KEY}"
                    recipes = requests.get(recipe_url).json()
                    
                    if recipes:
                        st.subheader("We found these matches:")
                        for r in recipes:
                            with st.expander(f"📖 {r['title']}"):
                                st.image(r['image'], use_container_width=True)
                                
                                # Show efficiency stats
                                st.write(f"✅ **You have:** {r['usedIngredientCount']} ingredients")
                                st.write(f"🛒 **You still need:** {r['missedIngredientCount']} ingredients")
                                
                                # 2. Get the actual recipe URL (required separate call)
                                info_url = f"https://api.spoonacular.com/recipes/{r['id']}/information?apiKey={API_KEY}"
                                info = requests.get(info_url).json()
                                st.link_button("View Full Recipe", info.get('sourceUrl', '#'))
                    else:
                        st.warning("No recipes found for these specific items. Try a different angle!")
                else:
                    st.error("AI couldn't identify the food. Try a clearer photo with good lighting.")
            
            elif response.status_code == 402:
                st.error("API Limit Reached! Spoonacular free tier only allows a few image scans per day.")
            else:
                st.error(f"Error: {response.status_code}. Make sure your API key is correct.")

        except Exception as e:
            st.error(f"Connection error: {e}")

# --- 💡 FOOTER ---
st.sidebar.info("Tip: Try uploading photos of raw ingredients like 'Potato', 'Chicken', or 'Apple' for best results.")