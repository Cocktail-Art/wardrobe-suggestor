import streamlit as st
from openai import OpenAI
import re
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set up Streamlit page
st.set_page_config(page_title="Style DNA Analyzer", layout="wide")
st.title("👔 Discover Your Fashion Personality in 60 Seconds")
st.markdown("### Answer these quick questions to unlock your personalized style blueprint")

with st.form("style_dna"):
    # Personal Information
    st.markdown("**Basic Information**")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name*", placeholder="Required")
    with col2:
        gender = st.selectbox("Gender*", ["Male", "Female", "Non-Binary", "Prefer not to say"], 
                            index=3, help="For personalized styling recommendations")
    
    email = st.text_input("Email ID*")
    phone = st.text_input("Whatsapp Number*")
    birthdate = st.date_input("Birthdate (Optional)", value=None)
    
    # Body Basics
    st.markdown("---")
    st.markdown("**Body Measurements**")
    col1, col2, col3 = st.columns(3)
    with col1:
        weight = st.number_input("Weight (kg)*", min_value=30, max_value=200)
    with col2:
        height = st.text_input("Height*")
    with col3:
        shirt_size = st.selectbox("Shirt Size*", ["S", "M", "L", "XL", "XXL"])
    pant_size = st.text_input("Pant Size* (e.g., 34x32)")

    # Style Questions
    st.markdown("---")
    st.markdown("**Style Preferences**")
    
    # Question 1
    frustrations = st.multiselect(
        "1. What frustrates you most when dressing up? (Pick 2)",
        options=[
            "Nothing fits me right", "I don't know what matches",
            "My clothes are outdated", "I never have the right outfit",
            "Shopping is overwhelming", "I want to look better, just don't know how"
        ],
        max_selections=2
    )

    # Question 2
    fit_pref = st.radio(
        "2. What kind of fit makes you feel most confident?",
        options=[
            "Slim & tailored", "Relaxed & comfy",
            "Structured but not tight", "I wear whatever I find"
        ],
        horizontal=True
    )

    # Question 3
    color_groups = st.multiselect(
        "3. Preferred color groups? (Pick 2)",
        options=[
            "Black, Grey, Navy", "White, Beige, Brown",
            "Olive, Teal, Rust", "Brights like mustard/red",
            "I avoid color — unsure what suits me"
        ],
        max_selections=2
    )

    # Question 4
    icons = st.multiselect(
        "4. Which style icon inspires you most? (Pick 1-2)",
        options=[
            "Shah Rukh (Rugged cool)",
            "Steve Jobs (Minimal)",
            "Virat Kohli (Sharp sporty)",
            "Pankaj Tripathi (Earthy calm)",
            "Ranveer Singh (Bold expressive)"
        ],
        max_selections=2
    )

    # Question 5
    weekend_outfit = st.radio(
        "5. Weekend outfit of choice?",
        options=[
            "Tee + joggers", "Shirt + jeans",
            "Kurta + pants", "Blazer + tee",
            "Loose tee + slides"
        ],
        horizontal=True
    )

    # Question 6
    accessories = st.radio(
        "6. How do you feel about accessories?",
        options=[
            "Love them — they finish a look",
            "Stick to basics",
            "Avoid them — too much hassle",
            "Curious, open to learn"
        ],
        horizontal=True
    )

    # Question 7
    wardrobe_goal = st.radio(
        "7. 3-month wardrobe goal?",
        options=[
            "Look more polished for work",
            "Rebuild with fewer, better pieces",
            "Be comfy but presentable",
            "Try a bold new look",
            "Just reduce confusion"
        ],
        horizontal=True
    )

    # Question 8
    wardrobe_vibe = st.radio(
        "8. Current wardrobe vibe?",
        options=[
            "Clean & functional", "Cool & laid-back",
            "Sharp & versatile", "Random & messy",
            "Doesn't reflect who I am"
        ],
        horizontal=True
    )

    # Question 9
    style_conf = st.slider(
        "9. Style confidence level today? (1 = Not confident, 5 = I own it)",
        1, 5, 3
    )

    # Submit button
    submitted = st.form_submit_button("🚀 Generate My Style DNA Report")

if submitted:
    # Validate required fields
    if not name or not gender or not email or not phone or not weight or not height or not shirt_size or not pant_size:
        st.error("Please fill all required fields marked with *")
        st.stop()

    # Handle color groups safely
    color_description = "No color preference" if not color_groups else ", ".join(color_groups)
    if len(color_groups) == 1:
        color_description += " focus"

    # Build analysis prompt
    analysis_prompt = f"""Analyze this style profile:
    Name: {name}
    Gender: {gender}
    Body: {weight}kg, {height}, {shirt_size} top, {pant_size} bottom
    Frustrations: {', '.join(frustrations) if frustrations else 'None specified'}
    Fit Preference: {fit_pref}
    Colors: {color_description}
    Style Icons: {', '.join(icons) if icons else 'None'}
    Weekend Style: {weekend_outfit}
    Accessory Approach: {accessories}
    Wardrobe Goal: {wardrobe_goal}
    Current Vibe: {wardrobe_vibe}
    Confidence: {style_conf}/5

    Create:
    1. Gender-appropriate style persona name
    2. 3 key style strengths
    3. 3 improvement areas
    4. 8-item capsule wardrobe (specific colors/materials)
    5. DALL-E 3 prompt for flat lay image (12 items, no humans, labeled items, white background)
    """

    # Generate analysis
    with st.spinner("🔍 Decoding your style DNA..."):
        try:
            # GPT-4 Analysis
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a fashion analyst creating detailed style reports."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            analysis = response.choices[0].message.content

            # Extract DALL-E prompt safely
            dalle_match = re.search(r"DALL-E 3 prompt:(.*?)(?=\n\d+\.|$)", analysis, re.DOTALL)
            if dalle_match:
                dalle_prompt = dalle_match.group(1).strip()
            else:
                dalle_prompt = f"Professional flat lay photography of 12 fashion items (3x4 grid) in {color_description} colors. Minimalist white background, items neatly arranged with small labels, no humans, high detail, commercial product photography style."

            # Generate wardrobe image
            image_response = client.images.generate(
                model="dall-e-3",
                prompt=dalle_prompt,
                size="1024x1024",
                quality="hd",
                style="natural"
            )

            # Display results
            st.success(f"🎉 Success! Here's {name}'s Style DNA Report")
            
            col1, col2 = st.columns([2, 3])
            with col1:
                st.markdown("## 📝 Style Breakdown")
                # Display analysis without the DALL-E prompt part
                st.markdown(analysis.split("DALL-E 3 prompt:")[0])
            
            with col2:
                st.markdown("## 🖼️ Vision Board Preview")
                st.image(image_response.data[0].url, use_column_width=True)
                st.caption("✨ AI-Generated Capsule Wardrobe Visualization")

        except Exception as e:
            st.error(f"Error generating report: {str(e)}")

# Add footer
st.markdown("---")
st.caption("Style DNA Analyzer v1.0 | Your personal fashion assistant")
