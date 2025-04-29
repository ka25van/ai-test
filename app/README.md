## Overview
This project is to show how to use the openfabric effectively and generate images also 3d images using effective prompts

1. **Enter the Prompt**  
   Uses a local ollama LLM llama 3.2 to interpret and creatively expand the prompt.

2. **Generate Image from Text**  
   Calls the Openfabric Text-to-Image app to generate an image from the prompt.

3. **Generate 3D Model from Image**  
   Calls the Openfabric Image-to-3D app to generate a 3D model from the previously generated image.

4. **Memory Management**  
   - Short-term session memory during interaction that is session storage.
   - Long-term memory persistence using SQLite database

## Project Structure

- `app/main.py` - Core pipeline logic including prompt expansion, Openfabric app chaining, and memory management.
- `app/ignite.py` - Entry point to start the Openfabric SDK server.
- `app/datastore/db.json` - SQLite database file for long-term memory.
- `app/visual.py` - Streamlit code to run from UI perspective.

## Setup Instructions

1. **Prerequisites**
- Python 3.8+
- Ollama CLI installed and configured with Llama 3.2 model
- Openfabric SDK installed (`openfabric_pysdk`)
- SQLite3 (usually included with Python)

2. **Run the application**
    python app/ignite.py
    The server will start
    or
    streamlit run visual.py
    The UI will be shown

## How it works?
- Enter a text/prompt to the application that you are thinking of.
- The local LLM will expand the prompt.
- The expanded prompt is sent to the Text-to-Image Openfabric app.
- The generated image URL is sent to the Image-to-3D Openfabric app.
- The final 3D model URL is returned.
- Session and long-term memory are saved.

## Memory
- **Short-Term Memory:** Stored in a Python dictionary during the session.
- **Long-Term Memory:** Persisted in SQLite database at `app/datastore/db.json`.
- Memory includes original prompt, expanded prompt, image URL, and 3D model URL.


# To note:- The package openfabric_pysdk is not getting installed, tried it many ways. If incase you consider or not consider my project completion, please drop the solution for it. It would be very helpful. ThankYou