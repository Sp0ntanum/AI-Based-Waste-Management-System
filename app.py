import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np
from keras.models import load_model
from PIL import Image, ImageOps
import plotly.express as px
import pandas as pd

# APP CONFIGURATION 
st.set_page_config(layout="wide", page_title="♻ Smart Waste Classifier", page_icon="🌍")

# LOAD MODEL
@st.cache_resource()
def load_waste_model():
    return load_model("keras_model.h5", compile=False), open("labels.txt", "r").readlines()

model, class_names = load_waste_model()

# WASTE CLASSIFICATION FUNCTION 
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

# RECYCLING GUIDELINES 
def get_recycling_guidelines(label):
    guidelines = {
        "cardboard": " Recycling cardboard helps reduce waste and conserve resources. Before recycling, remove any plastic, food residue, or grease stains, as contaminated cardboard is not recyclable. Flatten boxes to save space and ensure they are dry, as wet or greasy cardboard (like pizza boxes) should be composted or disposed of separately. Most clean cardboard, including shipping boxes and packaging, can be placed in curbside recycling bins or taken to local recycling centers. Proper recycling helps reduce landfill waste and supports a sustainable environment.",
        "plastic": " Recycling plastic helps reduce pollution and conserve resources. Before recycling, rinse plastic containers to remove residue and check for recycling symbols to determine if they are accepted locally. Hard plastics like bottles and food containers are commonly recyclable, while soft plastics like bags and wrappers may require special drop-off programs. Avoid recycling contaminated or mixed-material plastics, such as coated packaging. Proper sorting and disposal ensure plastics can be effectively processed and repurposed, reducing environmental impact.",
        "glass": " Recycling glass reduces waste and conserves raw materials. Before recycling, rinse glass containers to remove residue and remove any lids or caps, as they may be made of different materials. Most glass bottles and jars are recyclable, but items like mirrors, window glass, ceramics, and light bulbs require special disposal. Sorting glass by color (clear, green, brown) may be required in some areas. Glass can be recycled indefinitely without losing quality, making proper recycling essential for sustainability.",
        "metal": " Recycling metal waste conserves resources and reduces pollution. Clean and sort metals like aluminum, steel, and copper before recycling. Avoid placing hazardous items like batteries and gas cylinders in regular bins; instead, take them to specialized facilities. Many metals, including large appliances and car parts, can be recycled at scrap yards or designated centers, sometimes for monetary value. Proper recycling minimizes waste and supports sustainability."
    }

    return guidelines.get(label.lower(), "No specific recycling information available.")

# APP TITLE 
st.title("♻ Smart Waste Classifier & EXP Tracker 🌱🏆")

# NAVIGATION TABS 
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home", "📊 Waste Tracker", "📍 Recycling Centers", "📖 Education Hub"])

# WASTE CLASSIFICATION SECTION 
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
        milestones = {50: "🌱 Eco Starter", 100: "♻ Waste Warrior", 200: "🌍 Green Hero", 500: "🏆 Planet Protector"}
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

                st.subheader(f"✅ {label.upper()} detected")
                st.write(f"*Confidence:* {confidence:.2f}%")
                st.success(f"🎯 You earned *{exp_earned} EXP*!")

                if confidence < 60:
                    st.warning("⚠ The confidence score is low. The prediction may not be accurate.")
                
                check_achievements()
            
            with col2:
                st.subheader("🏆 Your EXP Progress")
                st.write(f"🎯 Your EXP Progress: {st.session_state['exp']} / 500")
                st.progress(min(st.session_state["exp"] / 500, 1.0))

                if st.session_state["achievements"]:
                    for achievement in st.session_state["achievements"]:
                        st.success(achievement)

                st.subheader("♻ Recycling Guidelines")
                st.write(get_recycling_guidelines(label))

        if st.button("🔄 Upload Another Image"):
            st.rerun()


# WASTE FOOTPRINT TRACKER SECTION 
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
        weekly_waste = {k: v / 1000 * 7 for k, v in st.session_state["waste_data"].items()}
        monthly_waste = {k: v / 1000 * 30 for k, v in st.session_state["waste_data"].items()}
        total_weekly = sum(weekly_waste.values())
        total_monthly = sum(monthly_waste.values())
        
        st.subheader("🌍 Waste Breakdown")
        st.write(f"**Total Weekly Waste:** {total_weekly:.2f} kg")
        st.write(f"**Total Monthly Waste:** {total_monthly:.2f} kg")
        
        df_waste = pd.DataFrame({
            "Category": list(st.session_state["waste_data"].keys()), 
            "Weekly (kg)": list(weekly_waste.values()), 
            "Monthly (kg)": list(monthly_waste.values())
        })
        
        fig = px.bar(df_waste, x="Category", y=["Weekly (kg)", "Monthly (kg)"],
                     title="Waste Generation (Weekly & Monthly)", barmode="group",
                     labels={"value": "Weight (kg)", "variable": "Time Frame"},
                     color_discrete_map={"Weekly (kg)": "lightcoral", "Monthly (kg)": "red"})
        
        st.plotly_chart(fig)

# RECYCLING CENTER MAP SECTION 
with tab3:
    st.subheader("📍 Nearby Recycling Centers")

    recycling_centers = [
        {"name": "Green Earth Recycling", "lat": 31.5001, "lon": 76.2003},
        {"name": "EcoWaste Solutions", "lat": 31.4956, "lon": 76.2054},
        {"name": "Sustainable Recycling Hub", "lat": 31.4823, "lon": 76.1987},
        {"name": "Zero Waste Facility", "lat": 31.4789, "lon": 76.1921},
    ]

    map_center = [31.4818, 76.1905]
    m = folium.Map(location=map_center, zoom_start=13)

    for center in recycling_centers:
        folium.Marker(
            [center["lat"], center["lon"]],
            popup=center["name"],
            icon=folium.Icon(color="green", icon="recycle", prefix='fa'),
        ).add_to(m)

    folium.Marker(
        map_center, popup="Your Location", icon=folium.Icon(color="blue", icon="home", prefix='fa')
    ).add_to(m)

    st_folium(m, width=700, height=400)

# WASTE AWARENESS & EDUCATION HUB  
with tab4:
    st.header("📖 Waste Awareness & Education Hub")

    # Interactive Quiz
    st.subheader("🎯 Test Your Recycling Knowledge!")
    quiz_question = "Which type of plastic is commonly recyclable?"
    quiz_options = ["PET (Plastic #1)", "PVC (Plastic #3)", "Polystyrene (Plastic #6)"]
    answer = st.radio(quiz_question, quiz_options)
    
    if st.button("Check Answer"):
        if answer == "PET (Plastic #1)":
            st.success("✅ Correct! PET is widely accepted for recycling.")
        else:
            st.error("❌ Incorrect. Try again!")

    # Educational Videos
    st.subheader("📺 Watch & Learn")
    st.video("https://www.youtube.com/watch?v=6jQ7y_qQYUA")  # Updated working video

    # Sustainability Articles
    st.subheader("📚 Sustainability Articles")
    st.write("[♻ How to Reduce Waste at Home](https://www.epa.gov/recycle)")
    st.write("[🌍 The Importance of Recycling](https://earth911.com/recycling/)")  # Updated valid link

    # Sustainable Shopping Suggestions
    st.subheader("🛍 Sustainable Shopping Suggestions")
    st.write("- Buy reusable bags instead of plastic bags.")
    st.write("- Choose products with minimal packaging.")
    st.write("- Support brands that use eco-friendly materials.")
    st.write("- Invest in high-quality, long-lasting items.")

    # Eco-Friendly Newsletters
    st.subheader("📩 Subscribe to Monthly Eco-News")
    email = st.text_input("Enter your email to receive sustainability tips:")
    if st.button("Subscribe"):
        st.success("✅ Subscription successful! Stay tuned for eco-friendly tips.")
