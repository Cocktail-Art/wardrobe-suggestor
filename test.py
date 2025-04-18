# style_vision.py
import streamlit as st
from openai import OpenAI
import re
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set up Streamlit page
st.set_page_config(page_title="Personal Style Architect", layout="wide")
st.title("👗🧥 Personal Style Architect")
st.markdown("Complete this style profile to receive your custom capsule wardrobe and visual collection")

# Single form for all sections
with st.form("style_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("🔑 Basic Information")
        name = st.text_input("Full Name")
        age = st.slider("Age", 18, 80, 25)
        gender = st.selectbox("Gender Identity", ["Female", "Male", "Non-binary", "Prefer not to say"])
        body_type = st.selectbox("Body Type", [
            "Hourglass", "Pear", "Apple", "Rectangle", "Inverted triangle", "No preference"
        ])
        sizes = st.columns(2)
        with sizes[0]:
            top_size = st.selectbox("Top Size", ["XS", "S", "M", "L", "XL"])
        with sizes[1]:
            bottom_size = st.text_input("Bottom Size (e.g., 28/30)")
        
    with col2:
        st.header("🎨 Style Preferences")
        color_palette = st.multiselect("Favorite Color Palette", [
            "Neutrals (black, white, beige)",
            "Earth tones (olive, rust, brown)",
            "Jewel tones (emerald, sapphire, ruby)",
            "Pastels (lavender, mint, blush)",
            "Brights (neon, primary colors)"
        ])
        style_inspiration = st.multiselect("Style Inspiration", [
            "Minimalist", "Bohemian", "Streetwear", "Business Casual",
            "Athleisure", "Romantic", "Edgy", "Vintage"
        ])
        avoids = st.text_area("What clothing items/materials do you avoid?")

    st.header("💡 Wardrobe Goals")
    lifestyle = st.multiselect("Weekly Activities (select all that apply)", [
        "Office work", "Creative work", "Parenting", "Fitness", 
        "Social events", "Outdoor activities", "Casual hangouts"
    ])
    investment = st.slider("Budget for new pieces (per month)", 50, 1000, 200)
    
    # Single submit button
    submitted = st.form_submit_button("🚀 Generate My Style Plan")

# Processing
if submitted:
    style_profile = f"""
    Gender Identity: {gender}
    Age: {age}
    Body Type: {body_type}
    Sizes: Top {top_size}, Bottom {bottom_size}
    Color Preferences: {', '.join(color_palette)}
    Style Inspiration: {', '.join(style_inspiration)}
    Avoids: {avoids}
    Lifestyle Needs: {', '.join(lifestyle)}
    Monthly Budget: ${investment}
    """

    wardrobe_prompt = f"""
    Act as a professional stylist creating a seasonless capsule wardrobe. Client profile:

    {style_profile}

    Create a wardrobe plan that includes:
    1. 8-10 tops (specify types and color/material)
    2. 5-6 bottoms (specify styles)
    3. 3-4 outerwear pieces
    4. 4-5 footwear options
    5. Accessories recommendation
    6. Key wardrobe rules for mixing pieces
    
    For DALL-E image:
    - List specific clothing items from the wardrobe
    - Create an image prompt showing these items arranged aesthetically
    - NO human figures - show only clothing
    - Specify exact colors from the palette
    """

    with st.spinner("Designing your perfect wardrobe..."):
        # Get wardrobe recommendations
        chat_response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a knowledgeable fashion stylist specializing in capsule wardrobes."},
                {"role": "user", "content": wardrobe_prompt}
            ],
            temperature=0.6,
            max_tokens=1500
        )
        wardrobe_plan = chat_response.choices[0].message.content
        st.subheader("✨ Your Capsule Wardrobe")
        st.markdown(wardrobe_plan)

        # Extract clothing items for image generation
        items_pattern = r"\d+\.\s(.*?)\s-\s(.*?)(?=\n\d+\.|$)"
        clothing_items = re.findall(items_pattern, wardrobe_plan)
        flat_items = [f"{type}: {desc}" for _, (type, desc) in enumerate(clothing_items[:10])]

        # Generate image prompt
        image_prompt = f"""
        Professional flat lay of a gender-neutral capsule wardrobe collection showing:
        {', '.join(flat_items[:8]) if flat_items else 'Various clothing items'} 
        arranged artistically on a neutral background. 
        Colors: {', '.join(color_palette) if color_palette else 'neutral palette'}.
        Editorial product photography style, clean lines, perfect lighting, 
        minimalist composition. No human figures or models.
        """

        # Generate vision board
        st.subheader("🖼️ Digital Closet Preview")
        with st.spinner("Creating your visual collection..."):
            try:
                image_response = client.images.generate(
                    model="dall-e-3",
                    prompt=image_prompt,
                    size="1024x1024",
                    quality="hd",
                    style="natural",
                    n=1
                )
                image_url = image_response.data[0].url
                st.image(image_url, use_column_width=True)
                st.markdown(f"**Image Prompt:** `{image_prompt}`")
                
            except Exception as e:
                st.error(f"Error generating image: {str(e)}")
                st.markdown(f"**Failed Image Prompt:** {image_prompt}")
