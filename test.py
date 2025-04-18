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
    
    # [All your style questions remain exactly the same...]

    # Submit button
    submitted = st.form_submit_button("🚀 Generate My Style DNA Report")

if submitted:
    # Validate required fields
    if not name or not gender or not email or not phone or not weight or not height or not shirt_size or not pant_size:
        st.error("Please fill all required fields marked with *")
        st.stop()

    # Build analysis prompt with strict formatting requirements
    analysis_prompt = f"""Create a detailed {gender.lower()} capsule wardrobe based on these preferences:
    
    Gender: {gender}
    Body: {weight}kg, {height}, {shirt_size} top, {pant_size} bottom
    Colors: {', '.join(color_groups) if color_groups else 'No preference'}
    Fit: {fit_pref}
    Style Icons: {', '.join(icons) if icons else 'None'}
    
    Provide the following EXACTLY in this format:
    
    ### Wardrobe Items ###
    1. [Item 1 with color/details]
    2. [Item 2 with color/details]
    3. [Item 3 with color/details]
    4. [Item 4 with color/details]
    5. [Item 5 with color/details]
    6. [Item 6 with color/details]
    7. [Item 7 with color/details]
    8. [Item 8 with color/details]
    
    ### Footwear ###
    - [Shoe 1 with details]
    - [Shoe 2 with details]
    
    ### Accessories ###
    - [Accessory 1]
    - [Accessory 2]
    
    ### Style Summary ###
    [3-4 sentence summary of the style]
    
    ### Image Prompt ###
    [Detailed DALL-E prompt describing EXACTLY how to visualize these items together]
    """

    with st.spinner("🔍 Creating your perfect wardrobe..."):
        try:
            # Get wardrobe recommendations
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are a {gender.lower()} fashion stylist creating detailed wardrobe plans."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            analysis = response.choices[0].message.content
            
            # Extract the image prompt
            image_prompt = analysis.split("### Image Prompt ###")[1].strip()
            
            # Extract the wardrobe items for display
            wardrobe_items = analysis.split("### Wardrobe Items ###")[1].split("### Footwear ###")[0].strip()
            footwear = analysis.split("### Footwear ###")[1].split("### Accessories ###")[0].strip()
            accessories = analysis.split("### Accessories ###")[1].split("### Style Summary ###")[0].strip()
            style_summary = analysis.split("### Style Summary ###")[1].split("### Image Prompt ###")[0].strip()

            # Generate the wardrobe image
            image_response = client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size="1024x1024",
                quality="hd",
                style="natural"
            )

            # Display results
            st.success(f"🎉 {name}'s Personalized {gender} Wardrobe")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("## 👕 Wardrobe Items")
                st.markdown(wardrobe_items)
                
                st.markdown("## 👟 Footwear")
                st.markdown(footwear)
                
                st.markdown("## 💍 Accessories")
                st.markdown(accessories)
                
                st.markdown("## 💡 Style Summary")
                st.markdown(style_summary)
            
            with col2:
                st.markdown("## 🖼️ Your Wardrobe Visualized")
                st.image(image_response.data[0].url, use_column_width=True)
                st.caption("AI-generated based on your style preferences")

        except Exception as e:
            st.error(f"Error generating wardrobe: {str(e)}")

# Add footer
st.markdown("---")
st.caption("Style DNA Analyzer v1.0 | Your personal fashion assistant")
