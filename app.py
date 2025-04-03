import streamlit as st 
import folium
from streamlit_folium import st_folium

import numpy as np
from keras.models import load_model
from PIL import Image, ImageOps
import random
import time

st.set_page_config(layout="wide", page_title="♻ Smart Waste Classifier", page_icon="🌍")

@st.cache_resource()
def load_waste_model():
    return load_model("keras_model.h5", compile=False), open("labels.txt", "r").readlines()

model, class_names = load_waste_model()

def classify_waste(img):
    np.set_printoptions(suppress=True)
    
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    image = img.convert("RGB")
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    data[0] = normalized_image_array
    
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index].strip().split(" ")[1].strip()
    confidence_score = prediction[0][index]
    return class_name, confidence_score

def get_recycling_guidelines(label):
    guidelines = {
        "cardboard": "✅ Remove plastic and grease before recycling. Flatten boxes to save space.",
        "plastic": "✅ Rinse plastic containers. Check recycling symbols for local rules.",
        "glass": "✅ Rinse bottles, remove lids. Do not recycle broken glass or ceramics.",
        "metal": "✅ Clean metal containers. Do not mix with hazardous waste like batteries."
    }
    return guidelines.get(label.lower(), "No recycling information available.")

st.markdown("""
    <style>
        .big-font { font-size:25px !important; }
        .exp-bar .stProgress > div > div { background-color: #4CAF50; }
        .sidebar-style { background-color: #f8f9fa; padding: 20px; border-radius: 10px; }
        .hover-button:hover { background-color: #28a745 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

st.title("♻ Waste Classifier & EXP Tracker 🌱🏆")

with st.sidebar:
    st.markdown("<div class='sidebar-style'>", unsafe_allow_html=True)
    st.header("📊 Waste Footprint Tracker")
    
    if "waste_data" not in st.session_state:
        st.session_state["waste_data"] = {"Plastic": 0, "Metal": 0, "Cardboard": 0, "Food": 0, "Glass": 0}
    
    for category in st.session_state["waste_data"]:
        st.session_state["waste_data"][category] = st.number_input(
            f"{category} Waste (grams per day)", 
            min_value=0, 
            value=st.session_state["waste_data"][category], 
            step=1,
            key=category
        )

    if "calculate_footprint" not in st.session_state:
        st.session_state["calculate_footprint"] = False

    if st.toggle("📈 Show My Waste Footprint", key="calculate_footprint"):
        yearly_waste = {k: v / 1000 * 365 for k, v in st.session_state["waste_data"].items()}
        total_waste = sum(yearly_waste.values())
        
        st.subheader(f"🌍 *Total Yearly Waste: {total_waste:.2f} kg*")
        for category, yearly_amount in yearly_waste.items():
            st.write(f"✅ {category}: {yearly_amount:.2f} kg per year")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("### 📸 Upload an Image for Waste Classification")
input_img = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if "exp" not in st.session_state:
    st.session_state["exp"] = 0
if "achievements" not in st.session_state:
    st.session_state["achievements"] = []

def earn_exp(category):
    points = {"plastic": 10, "metal": 15, "cardboard": 5, "food": 3, "glass": 8}
    earned = points.get(category.lower(), 0)
    st.session_state["exp"] += earned
    return earned

def check_achievements():
    milestones = {
        50: "🌱 Eco Starter - Earn 50 EXP",
        100: "♻ Waste Warrior - Earn 100 EXP",
        200: "🌍 Green Hero - Earn 200 EXP",
        500: "🏆 Planet Protector - Earn 500 EXP"
    }
    for exp_needed, achievement in milestones.items():
        if exp_needed <= st.session_state["exp"] and achievement not in st.session_state["achievements"]:
            st.session_state["achievements"].append(achievement)
            st.toast(f"🎉 Achievement Unlocked: {achievement}")
            st.balloons()

if input_img is not None:
    if st.button("🔍 Classify Waste", use_container_width=True, help="Click to analyze your waste item"): 
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(input_img, use_container_width=True)
            image_file = Image.open(input_img)
            label, confidence_score = classify_waste(image_file)
            exp_earned = earn_exp(label)
            st.success(f"✅ *{label.upper()} detected! You earned {exp_earned} EXP!* 🎉")
            st.success(f"♻ *Recycling Tip:* {get_recycling_guidelines(label)}")
            check_achievements()

        with col2:
            st.info("🌟 EXP Progress & Achievements")
            st.write(f"🎯 Your EXP Progress: {st.session_state['exp']} / 500")
            progress = st.session_state["exp"] / 500
            progress_bar = f"<progress value='{progress*100}' max='100' style='width:100%; height:20px;'></progress>"
            st.markdown(progress_bar, unsafe_allow_html=True)
            
            if st.session_state["achievements"]:
                for achievement in st.session_state["achievements"]:
                    st.success(achievement)

st.success(f"💡 Eco Tip: {random.choice(['🌱 Bring your own reusable bags when shopping.', '💧 Save water by turning off the tap while brushing.', '🔋 Recycle old batteries at designated collection points.', '🍃 Compost food waste to enrich soil naturally.', '🚲 Use a bike or walk instead of driving short distances.'])}")

st.markdown("---")
st.info("♻ *Track your waste, earn EXP, and make the world greener!* 🌱💚")

def show_recycling_map():
    st.subheader("📍 Nearby Recycling Centers")
    
    # User's location
    user_location = [31.48181963943555, 76.19054117377216]
    
    # List of sample recycling centers (replace with real data if needed)
    recycling_centers = [
        {"name": "Green Earth Recycling", "lat": 31.483, "lon": 76.195},
        {"name": "EcoCycle Center", "lat": 31.479, "lon": 76.185},
        {"name": "Waste Wise Hub", "lat": 31.485, "lon": 76.192},
    ]
    
    # Create map
    m = folium.Map(location=user_location, zoom_start=13)
    
    # Add user's location marker
    folium.Marker(
        location=user_location,
        popup="Your Location",
        icon=folium.Icon(color="blue", icon="home")
    ).add_to(m)
    
    # Add recycling center markers
    for center in recycling_centers:
        folium.Marker(
            location=[center["lat"], center["lon"]],
            popup=center["name"],
            icon=folium.Icon(color="green", icon="recycle")
        ).add_to(m)
    
    # Display map in Streamlit
    st_folium(m, width=700, height=400)

# Show map below classification results
st.markdown("---")
show_recycling_map()