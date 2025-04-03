import streamlit as st 
import folium
from streamlit_folium import st_folium

import numpy as np
from keras.models import load_model
from PIL import Image, ImageOps
import random
import time

# user interface design 
st.set_page_config(layout="wide", page_title="♻ Smart Waste Classifier", page_icon="🌍") 

@st.cache_resource()
def load_waste_model():
    return load_model("keras_model.h5", compile=False), open("labels.txt", "r").readlines()

model, class_names = load_waste_model()

# input image for classfication
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
        "cardboard": "✅ Recycling cardboard helps reduce waste and conserve resources. Before recycling, remove any plastic, food residue, or grease stains, as contaminated cardboard is not recyclable. Flatten boxes to save space and ensure they are dry, as wet or greasy cardboard (like pizza boxes) should be composted or disposed of separately. Most clean cardboard, including shipping boxes and packaging, can be placed in curbside recycling bins or taken to local recycling centers. Proper recycling helps reduce landfill waste and supports a sustainable environment.",
        "plastic": "✅ Recycling plastic helps reduce pollution and conserve resources. Before recycling, rinse plastic containers to remove residue and check for recycling symbols to determine if they are accepted locally. Hard plastics like bottles and food containers are commonly recyclable, while soft plastics like bags and wrappers may require special drop-off programs. Avoid recycling contaminated or mixed-material plastics, such as coated packaging. Proper sorting and disposal ensure plastics can be effectively processed and repurposed, reducing environmental impact.",
        "glass": "✅ Recycling glass reduces waste and conserves raw materials. Before recycling, rinse glass containers to remove residue and remove any lids or caps, as they may be made of different materials. Most glass bottles and jars are recyclable, but items like mirrors, window glass, ceramics, and light bulbs require special disposal. Sorting glass by color (clear, green, brown) may be required in some areas. Glass can be recycled indefinitely without losing quality, making proper recycling essential for sustainability.",
        "metal": "✅ Recycling metal waste conserves resources and reduces pollution. Clean and sort metals like aluminum, steel, and copper before recycling. Avoid placing hazardous items like batteries and gas cylinders in regular bins; instead, take them to specialized facilities. Many metals, including large appliances and car parts, can be recycled at scrap yards or designated centers, sometimes for monetary value. Proper recycling minimizes waste and supports sustainability."
    }
    return guidelines.get(label.lower(), "No recycling information available.")

st.markdown("""
    <style>
        .big-font { font-size:25px !important; }
        .exp-bar .stProgress > div > div { background-color: #4CAF50; }
        .sidebar-style { background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: -20px; }
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
        
        st.subheader(f"🌍 Total Yearly Waste: {total_waste:.2f} kg")
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
            st.success(f"✅ {label.upper()} detected! You earned {exp_earned} EXP! 🎉")
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
                    
            st.success(f"♻ Recycling Tip: {get_recycling_guidelines(label)}")

st.markdown("---")
st.info("♻ Track your waste, earn EXP, and make the world greener! 🌱💚")

def show_recycling_map(): # creating map
    # code for static map location
    st.subheader("📍 Nearby Recycling Centers")

    # compile time location input
    user_location = [31.48181963943555, 76.19054117377216]

    # location of the centers
    recycling_centers = [
        {"name": "Green Earth Recycling", "lat": 31.483, "lon": 76.195},
        {"name": "EcoCycle Center", "lat": 31.479, "lon": 76.185},
        {"name": "Waste Wise Hub", "lat": 31.485, "lon": 76.192},
    ]
    
    m = folium.Map(location=user_location, zoom_start=13)
    
    folium.Marker(
        location=user_location,
        popup="Your Location",
        icon=folium.Icon(color="blue", icon="home")
    ).add_to(m)
    
    for center in recycling_centers:
        folium.Marker(
            location=[center["lat"], center["lon"]],
            popup=center["name"],
            icon=folium.Icon(color="green", icon="recycle")
        ).add_to(m)
    
    st_folium(m, width=700, height=400)

st.markdown("---")
show_recycling_map()
