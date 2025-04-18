import streamlit as st
from openai import OpenAI  # Updated import
import re
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # New client initialization

# Set up Streamlit page
st.set_page_config(page_title="Style Personality & Vision Board", layout="wide")
st.title("🧥 Discover Your Style Personality")
st.markdown("Answer these 4 sections to get your custom capsule wardrobe and visual vision board.")

# Section 1: Basic Info
st.header("Section 1: Basic Information")
with st.form("section1"):
    name = st.text_input("Full Name")
    email = st.text_input("Email ID")
    phone = st.text_input("Whatsapp Number")
    birthdate = st.date_input("Birthdate")
    weight = st.number_input("Weight (in kgs)", min_value=30, max_value=200)
    height = st.text_input("Height (in cm or ft)")
    shirt_size = st.selectbox("Shirt Size", ["S", "M", "L", "XL", "XXL"])
    pant_size = st.text_input("Pant Size (e.g., 34x32)")
    skin_tone = st.slider("Skin Complexity (1 = Fair, 10 = Dark)", 1, 10, 5)
    submitted1 = st.form_submit_button("Save Section 1")

# Section 2: Challenges & Fit
st.header("Section 2: Dressing Challenges & Style Fit")
with st.form("section2"):
    frustrations = st.multiselect("What frustrates you most when dressing up?", [
        "Nothing fits me right", "I don't know what matches", "My clothes are outdated",
        "I never have the right outfit", "Shopping is overwhelming", "I want to look better, just don't know how"
    ])
    fit_pref = st.multiselect("What kind of fit makes you feel most confident?", [
        "Slim & tailored", "Relaxed & comfy", "Structured but not tight", "I wear whatever I find"
    ])
    color_groups = st.multiselect("Which of these color groups do you naturally wear or like?", [
        "Black, Grey, Navy", "White, Beige, Brown", "Olive, Teal, Rust",
        "Brights like mustard/red", "I avoid color — unsure what suits me"
    ])
    submitted2 = st.form_submit_button("Save Section 2")

# Section 3: Personality
st.header("Section 3: Style Expression & Personality")
with st.form("section3"):
    icon = st.selectbox("Which look or style icon inspires you most?", [
        "Shah Rukh in Pathaan (Rugged cool)", "Steve Jobs (Minimal)",
        "Virat Kohli (Sharp sporty)", "Pankaj Tripathi (Earthy calm)", "Ranveer Singh (Bold expressive)"
    ])
    weekend_outfit = st.multiselect("Weekend outfit of choice?", [
        "Tee + joggers", "Kurta + pants", "Blazer + tee", "Loose tee + slides", "Shirt + jeans"
    ])
    accessories = st.multiselect("How do you feel about accessories?", [
        "Love them — they finish a look", "Stick to basics", "Avoid them — too much hassle", "Curious, open to learn"
    ])
    submitted3 = st.form_submit_button("Save Section 3")

# Section 4: Mindset
st.header("Section 4: Self Image & Mindset")
with st.form("section4"):
    wardrobe_goal = st.selectbox("What's your ideal wardrobe goal in the next 3 months?", [
        "Look more polished for work", "Rebuild with fewer, better pieces", "Be comfy but presentable",
        "Try a bold new look", "Just reduce confusion"
    ])
    wardrobe_vibe = st.selectbox("What's the overall vibe of your wardrobe right now?", [
        "Clean & functional", "Cool & laid-back", "Sharp & versatile", "Random & messy", "Doesn't reflect who I am"
    ])
    style_conf = st.slider("Style confidence level today", 1, 5, 3)
    final_submit = st.form_submit_button("✨ Generate My Style Vision Board")

# Final Processing
if final_submit:
    user_profile = f"""
    Name: {name}
    Weekend Outfit: {', '.join(weekend_outfit)}
    Accessories: {', '.join(accessories)}
    Wardrobe Goal: {wardrobe_goal}
    Current Vibe: {wardrobe_vibe}
    Style Confidence: {style_conf}/5
    Frustrations: {', '.join(frustrations)}
    Fit Preferences: {', '.join(fit_pref)}
    Color Preferences: {', '.join(color_groups)}
    Icon Inspiration: {icon}
    Skin Complexity: {skin_tone}/10
    Shirt Size: {shirt_size}, Pant Size: {pant_size}
    """

    full_prompt = f"""
    You are a fashion stylist creating a capsule wardrobe for a male client with the following preferences:

    {user_profile}

    Create a capsule wardrobe suggestion that includes:
    1. Tops (6 pieces)
    2. Bottoms (3–4 pieces)
    3. Footwear (2–3 options)
    4. Outerwear (1–2 pieces)
    5. Accessories (if relevant)
    6. A brief explanation of the style vibe
    7. A one-line image generation prompt for DALL·E that describes the vision board featuring these items
    """

    st.subheader("🎯 Style Breakdown")
    with st.spinner("Creating your wardrobe..."):
        response = client.chat.completions.create(  # Updated API call
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful fashion stylist."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        content = response.choices[0].message.content  # Updated response access
        st.markdown(content)

        image_prompt_match = re.search(r'(?i)image generation prompt.*?:\s*(.+)', content)
        image_prompt = image_prompt_match.group(1).strip() if image_prompt_match else (
            f"Flat lay editorial photo of a stylish Indian man's capsule wardrobe — 6 visible clothing items including "
            f"{', '.join(weekend_outfit)}, matching accessories, and shoes laid out on a neutral background. "
            f"Modern, clean design, everything clearly visible, top-down view."
        )

    st.subheader("🖼️ Vision Board Preview")
    with st.spinner("Generating your visual..."):
        image_response = client.images.generate(  # Updated API call
            prompt=image_prompt,
            n=1,
            size="1024x1024"
        )
        image_url = image_response.data[0].url  # Updated response access
        st.image(image_url, caption="Your Style Vision Board", use_column_width=True)
        st.markdown(f"[🔗 View Full Image]({image_url})")
