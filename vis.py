import google.generativeai as genai
from pathlib import Path
import streamlit as st

# Configure GenAI API key
genai.configure(api_key="AIzaSyCy4ZTxt1DiSBeySNHw-pYJey70Nc_uQ3I")

# Function to initialize the model
def initialize_model():
    generation_config = {"temperature": 0.9}
    return genai.GenerativeModel("gemini-1.5-flash", generation_config=generation_config)

# Function to process the image and generate content based on prompts
def generate_content(model, image_path, prompts):
    image_part = {
        "mime_type": "image/jpeg",
        "data": image_path.read_bytes()
    }
    
    results = []
    for prompt_text in prompts:
        prompt_parts = [prompt_text, image_part]
        response = model.generate_content(prompt_parts)
        
        # Extract and return the text content from the response
        if response.candidates:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                text_part = candidate.content.parts[0]
                if text_part.text:
                    results.append(f"Prompt: {prompt_text}\nDescription: {text_part.text}\n")
                else:
                    results.append(f"Prompt: {prompt_text}\nDescription: No valid content generated.\n")
            else:
                results.append(f"Prompt: {prompt_text}\nDescription: No content parts found.\n")
        else:
            results.append(f"Prompt: {prompt_text}\nDescription: No candidates found.\n")
    
    return results

# Streamlit app
def main():
    # Initialize session state for prompts and results
    if "prompts" not in st.session_state:
        st.session_state.prompts = ""
    if "results" not in st.session_state:
        st.session_state.results = []

    st.title("Image Description with GenAI Model")

    # Upload an image file
    uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Save the uploaded file
        with open("temp_image.jpg", "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Initialize the model
        model = initialize_model()
        
        # Input for multiple prompts
        st.write("Enter prompts (one per line):")
        st.session_state.prompts = st.text_area("Prompts", value=st.session_state.prompts)
        
        # Button to generate content
        if st.button("Generate Description"):
            # Split prompts into a list
            prompts = [prompt.strip() for prompt in st.session_state.prompts.split('\n') if prompt.strip()]
            
            if prompts:
                # Generate content based on the uploaded image and user prompts
                image_path = Path("temp_image.jpg")
                st.session_state.results = generate_content(model, image_path, prompts)
                
                # Display the image and the generated content
                st.image(uploaded_file, caption='Uploaded Image.', use_column_width=True)
                st.write("Generated Descriptions:")
                for description in st.session_state.results:
                    st.write(description)
            else:
                st.write("Please enter at least one prompt.")
        
        # Optionally remove the temporary file
        Path("temp_image.jpg").unlink()
    
    # Display the previously generated results
    if st.session_state.results:
        st.write("Previously Generated Descriptions:")
        for description in st.session_state.results:
            st.write(description)

if __name__ == "__main__":
    main()
