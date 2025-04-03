import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np
from keras.models import load_model
from PIL import Image, ImageOps

st.set_page_config(layout="wide", page_title="♻ Smart Waste Classifier", page_icon="🌍")

st.markdown("""
    <style>
    /* Light Mode */
    .stApp {
        background-color: #f5f7fa;
        font-family: 'Arial', sans-serif;
        color: #333;
    }
    
    .info-card {
        background-color: #ffffff;
        color: #333;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        text-align: center;
    }

    /* Dark Mode */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background-color: #121212;
            color: #e0e0e0;
        }
        .info-card {
            background-color: #1e1e1e !important;
            color: #e0e0e0 !important;
            box-shadow: 0px 4px 10px rgba(255, 255, 255, 0.1);
        }
        .stButton>button {
            background-color: #555;
            color: white;
        }
        .stButton>button:hover {
            background-color: #777;
        }
        .stProgress>div>div {
            background-color: #4CAF50 !important;
        }
    }

    /* Title Styling */
    h1 {
        color: #1f6f8b;
        text-align: center;
        font-size: 36px;
        font-weight: bold;
    }

    /* Buttons */
    .stButton>button {
        background-color: #1f6f8b;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
        transition: 0.3s;
    }

    .stButton>button:hover {
        background-color: #99a8b2;
    }

    /* Progress Bar */
    .stProgress>div>div {
        background-color: #1f6f8b !important;
    }
    </style>
""", unsafe_allow_html=True)


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
    confidence_score = prediction[0][index] * 100
    
    return class_name, confidence_score

def get_recycling_guidelines(label):
    guidelines = {
        "cardboard": "Flatten boxes and remove any plastic or grease.",
        "plastic": "Rinse and check for recycling symbols.",
        "glass": "Remove lids and sort by color if required.",
        "metal": "Clean and separate from hazardous waste."
    }
    return guidelines.get(label.lower(), "No recycling information available.")

st.title("♻ Smart Waste Classifier & EXP Tracker 🌱🏆")

tab1, tab2, tab3 = st.tabs(["🏠 Home", "📊 Waste Tracker", "📍 Recycling Centers"])

with tab1:
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
            50: "🌱 Eco Starter",
            100: "♻ Waste Warrior",
            200: "🌍 Green Hero",
            500: "🏆 Planet Protector"
        }
        for exp_needed, achievement in milestones.items():
            if exp_needed <= st.session_state["exp"] and achievement not in st.session_state["achievements"]:
                st.session_state["achievements"].append(achievement)
                st.toast(f"🎉 Achievement Unlocked: {achievement}")
                st.balloons()
    
    if input_img is not None:
        if st.button("🔍 Classify Waste"): 
            col1, col2 = st.columns([1, 1])
            with col1:
                st.image(input_img, use_container_width=True)
                image_file = Image.open(input_img)
                with st.spinner("🔄 Classifying... Please wait"):
                    label, confidence = classify_waste(image_file)
                exp_earned = earn_exp(label)

                st.markdown(f"""
                <div class='info-card'>
                    <h3>✅ {label.upper()} detected</h3>
                    <p><strong>Confidence: {confidence:.2f}%</strong></p>
                    <p>🎯 You earned <strong>{exp_earned} EXP</strong>!</p>
                </div>
                """, unsafe_allow_html=True)

                if confidence < 60:
                    st.warning("⚠ The confidence score is low. The prediction may not be accurate.")
                
                check_achievements()
            
            with col2:
                st.markdown("<h3 style='text-align: center;'>🏆 Your EXP Progress</h3>", unsafe_allow_html=True)
                st.write(f"🎯 Your EXP Progress: {st.session_state['exp']} / 500")
                st.progress(min(st.session_state["exp"] / 500, 1.0))

                if st.session_state["achievements"]:
                    for achievement in st.session_state["achievements"]:
                        st.success(achievement)

                st.subheader("♻ Recycling Guidelines")
                st.write(get_recycling_guidelines(label))

        if st.button("🔄 Upload Another Image"):
            st.experimental_rerun()

with tab2:
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
    
    if st.toggle("📈 Show My Waste Footprint"):
        yearly_waste = {k: v / 1000 * 365 for k, v in st.session_state["waste_data"].items()}
        total_waste = sum(yearly_waste.values())
        st.subheader(f"🌍 Total Yearly Waste: {total_waste:.2f} kg")
        for category, yearly_amount in yearly_waste.items():
            st.markdown(f"✅ **{category}:** {yearly_amount:.2f} kg per year")

with tab3:
    st.subheader("📍 Nearby Recycling Centers")
    user_location = [31.4818, 76.1905]
    m = folium.Map(location=user_location, zoom_start=13)
    folium.Marker(user_location, popup="Your Location", icon=folium.Icon(color="blue", icon="home")).add_to(m)
    st_folium(m, width=700, height=400)
