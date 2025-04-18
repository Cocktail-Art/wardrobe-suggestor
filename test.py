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
st.set_page_config(page_title="Style Personality & Vision Board", layout="wide")
st.title("👗 Discover Your Style Personality")
st.markdown("Complete this style questionnaire to receive your personalized capsule wardrobe and vision board")

# Consolidated form with all sections
with st.form("style_form"):
    st.header("🛍️ Personal Style Profile")
    
    # Section 1: Basic Info
    st.subheader("Basic Information")
    name = st.text_input("Full Name")
    weight = st.number_input("Weight (kg)", min_value=30, max_value=200)
    height = st.text_input("Height")
    top_size = st.selectbox("Top Size", ["XS", "S", "M", "L", "XL", "XXL"])
    bottom_size = st.text_input("Bottom Size (e.g., 28x32, M, 38)")
    skin_tone = st.slider("Skin Tone (1 = Fair, 10 = Dark)", 1, 10, 5)

    # Section 2: Style Preferences
    st.subheader("Style Preferences")
    style_icons = st.multiselect("Which style icons inspire you?", [
        "Classic Elegance", "Streetwear Vibes", "Boho Chic", 
        "Minimalist", "Sporty", "Professional", "Artsy"
    ])
    color_palette = st.multiselect("Favorite color groups:", [
        "Neutrals (black, white, beige)", "Earth tones", "Pastels",
        "Jewel tones", "Bright colors", "Monochromatic"
    ])
    frustrations = st.multiselect("Biggest style challenges:", [
        "Finding proper fits", "Mixing patterns/textures",
        "Accessorizing", "Seasonal transitions",
        "Budget-friendly options", "Body confidence"
    ])

    # Section 3: Lifestyle Needs
    st.subheader("Lifestyle Needs")
    weekly_breakdown = st.multiselect("Weekly activities:", [
        "Office work", "Gym/fitness", "Casual outings",
        "Special events", "Creative work", "Parenting"
    ])
    comfort_level = st.slider("Comfort vs Style balance", 1, 5, 3, 
                            help="1 = All comfort, 5 = All style")

    # Single submit button
    submitted = st.form_submit_button("✨ Generate My Style Plan")

if submitted:
    # Build the style profile
    style_profile = f"""
    Style Profile for {name}:
    - Body: {weight}kg, {height}, Top: {top_size}, Bottom: {bottom_size}
    - Skin Tone: {skin_tone}/10
    - Style Inspirations: {', '.join(style_icons)}
    - Color Preferences: {', '.join(color_palette)}
    - Challenges: {', '.join(frustrations)}
    - Weekly Activities: {', '.join(weekly_breakdown)}
    - Comfort/Style Balance: {comfort_level}/5
    """

    # Enhanced GPT prompt
    gpt_prompt = f"""Act as a professional fashion stylist. Create a capsule wardrobe based on these requirements:
    
    {style_profile}
    
    Your response MUST include:
    1. 8-10 specific clothing items (include colors/materials)
    2. 4-5 footwear options 
    3. 3-5 accessory recommendations
    4. Style guidelines for mixing items
    5. A DALL-E 3 prompt for a flat lay image of these items
    
    Image requirements:
    - No human models or body parts
    - Show individual clothing items arranged artistically
    - Neutral background
    - Consistent lighting
    - Include text labels for key pieces
    """

    # Generate wardrobe suggestions
    with st.spinner("Creating your perfect wardrobe..."):
        try:
            # Get text response
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a fashion expert specializing in capsule wardrobes."},
                    {"role": "user", "content": gpt_prompt}
                ],
                temperature=0.6,
                max_tokens=1500
            )
            response_text = completion.choices[0].message.content
            
            # Extract DALL-E prompt
            dalle_prompt = re.search(r"DALL-E 3 prompt:(.*?)(?=\n\d+\.|$)", response_text, re.DOTALL)
            if dalle_prompt:
                dalle_prompt = dalle_prompt.group(1).strip()
            else:  # Fallback prompt
                dalle_prompt = f"Professional flat lay photography of a gender-neutral capsule wardrobe containing {len(style_icons)*2} items, "\
                            f"including {', '.join(color_palette[:2])} colors. Items neatly arranged on neutral background, "\
                            "soft lighting, minimalist composition, high detail, textile textures visible, no human models."

            # Generate wardrobe image
            image_response = client.images.generate(
                model="dall-e-3",
                prompt=dalle_prompt,
                size="1024x1024",
                quality="hd",
                n=1
            )

            # Display results
            st.subheader("🧳 Your Capsule Wardrobe")
            st.markdown(response_text.split("DALL-E 3 prompt:")[0])

            st.subheader("🎨 Visual Wardrobe Guide")
            st.image(image_response.data[0].url, caption="Your Personalized Capsule Wardrobe", use_column_width=True)
            
        except Exception as e:
            st.error(f"Error generating wardrobe: {str(e)}")
