import streamlit as st
import subprocess
from core.stub import Stub

# Session state to store data during the app's runtime.
if 'session_memory' not in st.session_state:
    st.session_state.session_memory = {}

# Function to call local LLM (Ollama)
def call_ollama_llama(prompt: str) -> str:
    try:
        result = subprocess.run(
            ['ollama', 'run', 'llama3.2:latest', '--prompt', prompt],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error calling Ollama Llama 3.2: {e}"

# Function to run the pipeline
def run_pipeline(user_prompt: str):
    # Expand prompt
    expanded_prompt = call_ollama_llama(user_prompt)

    # Initialize Stub with app IDs (hardcoded or configurable)
    app_ids = [
        "f0997a01-d6d3-a5fe-53d8-561300318557",  # Text-to-Image
        "69543f29-4d41-4afc-7f29-3d51591f11eb"   # Image-to-3D
    ]
    stub = Stub(app_ids)

    # Call Text-to-Image app
    text_image_stub = stub([app_ids[0]])
    text_image_response = text_image_stub.execute({
        "prompt": expanded_prompt,
    })
    image_url = text_image_response.get("image_url", "Image generation failed")

    # Call Image-to-3D app
    image_3d_stub = stub([app_ids[1]])
    image_3d_response = image_3d_stub.execute({
        "image_url": image_url
    })
    model_3d_url = image_3d_response.get("model_3d_url", "3D image generation failed")

    # Save session memory
    st.session_state.session_memory['last_prompt'] = user_prompt
    st.session_state.session_memory['expanded_prompt'] = expanded_prompt
    st.session_state.session_memory['image_url'] = image_url
    st.session_state.session_memory['model_3d_url'] = model_3d_url

    return expanded_prompt, image_url, model_3d_url

# Streamlit UI
st.title("Openfabric - Visual GUI")

user_prompt = st.text_area("Enter your prompt:", height=100)

if st.button("Generate"):
    if not user_prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        with st.spinner("Processing..."):
            expanded_prompt, image_url, model_3d_url = run_pipeline(user_prompt)

        st.subheader("Results")
        st.markdown(f"**Original Prompt:** {user_prompt}")
        st.markdown(f"**Expanded Prompt:** {expanded_prompt}")
        st.markdown(f"**Image URL:** {image_url}")
        if image_url and image_url != "Image generation failed":
            st.image(image_url, caption="Generated Image", use_column_width=True)
        st.markdown(f"**3D Model URL:** {model_3d_url}")
        if model_3d_url and model_3d_url != "3D image generation failed":
            st.markdown(f"[View 3D Model]({model_3d_url})")

st.markdown("---")
st.markdown("Session memory is stored during this interaction.")