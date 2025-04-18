import streamlit as st
from openai import OpenAI
import re
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set up Streamlit page
st.set_page_config(page_title="Style DNA Analyzer", layout="wide")
st.title("👔 Discover Your Fashion Personality in 60 Seconds")
st.markdown("### Answer these quick questions to unlock your personalized style blueprint")

with st.form("style_dna"):
    # Header
    st.markdown("## Quick Personal Info")
    
    # Personal Information
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name*", placeholder="Required")
        email = st.text_input("Email ID*")
        phone = st.text_input("Whatsapp Number*")
    with col2:
        birthdate = st.date_input("Birthdate (Optional)", value=None)
        weight = st.number_input("Weight (kg)*", min_value=30, max_value=200)
        height = st.text_input("Height* (cm or ft)")
    
    # Body Basics
    st.markdown("---")
    st.markdown("#### Your Body Basics (Essential for perfect fit)")
    body_col1, body_col2 = st.columns(2)
    with body_col1:
        shirt_size = st.selectbox("Shirt Size*", ["S", "M", "L", "XL", "XXL"])
    with body_col2:
        pant_size = st.text_input("Pant Size* (e.g., 34x32)")

    # Section 1: Dressing Challenges
    with st.expander("Section 1: Dressing Challenges", expanded=True):
        st.markdown("#### 1. What frustrates you most when dressing up? (Pick 2)")
        frustrations = st.multiselect(
            "Select up to 2:",
            options=[
                "Nothing fits me right", "I don't know what matches",
                "My clothes are outdated", "I never have the right outfit",
                "Shopping is overwhelming", "I want to look better, just don't know how"
            ],
            max_selections=2
        )

        st.markdown("#### 2. What kind of fit makes you feel most confident?")
        fit_pref = st.radio(
            "Select one:",
            options=[
                "Slim & tailored", "Relaxed & comfy",
                "Structured but not tight", "I wear whatever I find"
            ],
            horizontal=True
        )

        st.markdown("#### 3. Preferred color groups? (Pick 2)")
        color_groups = st.multiselect(
            "Select up to 2:",
            options=[
                "Black, Grey, Navy", "White, Beige, Brown",
                "Olive, Teal, Rust", "Brights like mustard/red",
                "I avoid color — unsure what suits me"
            ],
            max_selections=2
        )

    # Section 2: Style Personality
    with st.expander("Section 2: Style Expression", expanded=False):
        st.markdown("#### 4. Which style icon inspires you most? (Pick 1-2)")
        icons = st.multiselect(
            "Select 1-2:",
            options=[
                "Shah Rukh in Pathaan (Rugged cool)",
                "Steve Jobs (Minimal)",
                "Virat Kohli (Sharp sporty)",
                "Pankaj Tripathi (Earthy calm)",
                "Ranveer Singh (Bold expressive)"
            ],
            max_selections=2
        )

        st.markdown("#### 5. Weekend outfit of choice?")
        weekend_outfit = st.radio(
            "Select one:",
            options=[
                "Tee + joggers", "Shirt + jeans",
                "Kurta + pants", "Blazer + tee",
                "Loose tee + slides"
            ],
            horizontal=True
        )

        st.markdown("#### 6. How do you feel about accessories?")
        accessories = st.radio(
            "Select one:",
            options=[
                "Love them — they finish a look",
                "Stick to basics",
                "Avoid them — too much hassle",
                "Curious, open to learn"
            ],
            horizontal=True
        )

    # Section 3: Mindset
    with st.expander("Section 3: Self Image & Mindset", expanded=False):
        st.markdown("#### 7. 3-month wardrobe goal?")
        wardrobe_goal = st.radio(
            "Select one:",
            options=[
                "Look more polished for work",
                "Rebuild with fewer, better pieces",
                "Be comfy but presentable",
                "Try a bold new look",
                "Just reduce confusion"
            ],
            horizontal=True
        )

        st.markdown("#### 8. Current wardrobe vibe?")
        wardrobe_vibe = st.radio(
            "Select one:",
            options=[
                "Clean & functional", "Cool & laid-back",
                "Sharp & versatile", "Random & messy",
                "Doesn't reflect who I am"
            ],
            horizontal=True
        )

        st.markdown("#### 9. Style confidence level today?")
        style_conf = st.slider(
            "1 = Not confident, 5 = I own it",
            1, 5, 3,
            label_visibility="collapsed"
        )

    # Final submission
    submitted = st.form_submit_button("🚀 Generate My Style DNA Report")

if submitted:
    # Calculate zodiac sign if birthdate provided
    zodiac = ""
    if birthdate:
        month = birthdate.month
        day = birthdate.day
        # Add zodiac calculation logic here

    # Build analysis prompt
    analysis_prompt = f"""Analyze this style profile:
    Name: {name}
    Body: {weight}kg, {height}, {shirt_size} top, {pant_size} bottom
    Frustrations: {', '.join(frustrations)}
    Fit Preference: {fit_pref}
    Colors: {', '.join(color_groups)}
    Style Icons: {', '.join(icons)}
    Weekend Style: {weekend_outfit}
    Accessory Approach: {accessories}
    Wardrobe Goal: {wardrobe_goal}
    Current Vibe: {wardrobe_vibe}
    Confidence: {style_conf}/5
    Zodiac: {zodiac if zodiac else 'Not provided'}

    Create:
    1. Style persona name
    2. 3 key style strengths
    3. 3 improvement areas
    4. 8-item capsule wardrobe (specific colors/materials)
    5. DALL-E 3 prompt for flat lay image (no humans, labeled items)
    """

    # Generate analysis
    with st.spinner("🔍 Decoding your style DNA..."):
        try:
            # GPT-4 Analysis
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a fashion analyst specializing in personalized style profiles."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            analysis = response.choices[0].message.content

            # Extract DALL-E prompt
            dalle_prompt = re.search(r"DALL-E 3 prompt:(.*?)(?=\n\d+\.|$)", analysis, re.DOTALL)
            if dalle_prompt:
                dalle_prompt = dalle_prompt.group(1).strip()
            else:
                dalle_prompt = f"Professional flat lay of {name}'s capsule wardrobe containing 8 items: {color_groups[0]} and {color_groups[1]} colors. Include labels, textile textures, no humans. Minimalist white background."

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
