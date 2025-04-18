import streamlit as st
from openai import OpenAI
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

    # Build comprehensive analysis prompt
    analysis_prompt = f"""Create a personalized {gender.lower()} wardrobe considering ALL these factors:
    
    ### User Profile ###
    Name: {name}
    Gender: {gender}
    Body: {weight}kg, {height}, {shirt_size} top, {pant_size} bottom
    
    ### Style Challenges ###
    Frustrations: {', '.join(frustrations) if frustrations else 'None'}
    
    ### Preferences ###
    Fit: {fit_pref}
    Colors: {', '.join(color_groups) if color_groups else 'Open to all colors'}
    Style Icons: {', '.join(icons) if icons else 'No specific icons'}
    Weekend Style: {weekend_outfit}
    Accessories: {accessories}
    
    ### Wardrobe Context ###
    Current Vibe: {wardrobe_vibe}
    3-Month Goal: {wardrobe_goal}
    Confidence Level: {style_conf}/5
    
    ### Required Output ###
    1. 8 specific clothing items (include colors, materials, and how they address the user's preferences)
    2. 3 footwear options (match the style and colors)
    3. 3 accessory suggestions (consider the user's accessory preference)
    4. Style summary connecting all choices to the user's inputs
    5. EXACT DALL-E prompt to visualize these items together (12 items total, no humans)
    
    Format response with these exact section headers:
    ### Wardrobe Recommendations ###
    ### Footwear Options ### 
    ### Accessory Suggestions ###
    ### Style Explanation ###
    ### Image Generation Prompt ###
    """

    with st.spinner("🔍 Creating your perfect wardrobe..."):
        try:
            # Get comprehensive wardrobe recommendations
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are a {gender.lower()} fashion expert creating fully personalized wardrobes."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.7,
                max_tokens=1800
            )
            analysis = response.choices[0].message.content
            
            # Parse the response
            wardrobe = analysis.split("### Wardrobe Recommendations ###")[1].split("### Footwear Options ###")[0].strip()
            footwear = analysis.split("### Footwear Options ###")[1].split("### Accessory Suggestions ###")[0].strip()
            accessories = analysis.split("### Accessory Suggestions ###")[1].split("### Style Explanation ###")[0].strip()
            explanation = analysis.split("### Style Explanation ###")[1].split("### Image Generation Prompt ###")[0].strip()
            image_prompt = analysis.split("### Image Generation Prompt ###")[1].strip()

            # Generate the wardrobe image
            image_response = client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size="1024x1024",
                quality="hd",
                style="natural"
            )

            # Display results
            st.success(f"🎉 {name}'s Complete Style Profile")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("## 👕 Wardrobe Recommendations")
                st.markdown(wardrobe)
                
                st.markdown("## 👟 Footwear Options")
                st.markdown(footwear)
                
                st.markdown("## 💍 Accessory Suggestions")
                st.markdown(accessories)
                
                st.markdown("## 💡 Style Explanation")
                st.markdown(explanation)
            
            with col2:
                st.markdown("## 🖼️ Your Personalized Wardrobe")
                st.image(image_response.data[0].url, use_column_width=True)
                st.caption("AI-generated visualization of your recommended items")

        except Exception as e:
            st.error(f"Error generating wardrobe: {str(e)}")

# Add footer
st.markdown("---")
st.caption("Style DNA Analyzer v1.0 | Your personal fashion assistant")
