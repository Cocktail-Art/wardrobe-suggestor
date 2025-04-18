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
        gender = st.selectbox("Gender*", ["Male", "Female"], 
                            help="For gender-specific styling recommendations")
    
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
    
    # [Keep all the style questions exactly as before...]

if submitted:
    # Validate required fields
    if not name or not gender or not email or not phone or not weight or not height or not shirt_size or not pant_size:
        st.error("Please fill all required fields marked with *")
        st.stop()

    # Handle color groups safely
    color_description = "No color preference" if not color_groups else ", ".join(color_groups)
    if len(color_groups) == 1:
        color_description += " focus"

    # Build gender-specific analysis prompt
    analysis_prompt = f"""Analyze this {gender.lower()} style profile:
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
    1. {gender}-specific style persona name
    2. 3 key style strengths
    3. 3 improvement areas
    4. 8-item {gender.lower()} capsule wardrobe (specific colors/materials)
    5. DALL-E 3 prompt for {gender.lower()} fashion flat lay (12 items, no humans, labeled items)
    """

    # Generate analysis
    with st.spinner("🔍 Decoding your style DNA..."):
        try:
            # GPT-4 Analysis
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are a {gender.lower()} fashion expert creating detailed style reports."},
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
                if gender == "Male":
                    dalle_prompt = f"Professional flat lay of 12 {gender.lower()} fashion items: shirts, trousers, jackets, shoes. {color_description} colors. Clean white background, items neatly arranged with labels, no humans, masculine style."
                else:
                    dalle_prompt = f"Professional flat lay of 12 {gender.lower()} fashion items: blouses, skirts, dresses, shoes. {color_description} colors. Clean white background, items neatly arranged with labels, no humans, feminine style."

            # Generate wardrobe image
            image_response = client.images.generate(
                model="dall-e-3",
                prompt=dalle_prompt,
                size="1024x1024",
                quality="hd",
                style="natural"
            )

            # Display results
            st.success(f"🎉 Success! Here's {name}'s {gender} Style DNA Report")
            
            col1, col2 = st.columns([2, 3])
            with col1:
                st.markdown("## 📝 Style Breakdown")
                # st.markdown(analysis.split("DALL-E 3 prompt:")[0])
            
            with col2:
                st.markdown(f"## 🖼️ {gender} Wardrobe Preview")
                st.image(image_response.data[0].url, use_column_width=True)
                st.caption(f"✨ AI-Generated {gender} Capsule Wardrobe")

        except Exception as e:
            st.error(f"Error generating report: {str(e)}")

# Add footer
st.markdown("---")
st.caption("Style DNA Analyzer v1.0 | Your personal fashion assistant")
