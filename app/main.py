import logging
import subprocess
from typing import Dict

from ontology_dc8f06af066e4a7880a5938933236037.config import ConfigClass
from ontology_dc8f06af066e4a7880a5938933236037.input import InputClass
from ontology_dc8f06af066e4a7880a5938933236037.output import OutputClass
from openfabric_pysdk.context import AppModel, State  
from core.stub import Stub

from typing import Dict
import sqlite3
import os

from ontology_dc8f06af066e4a7880a5938933236037.config import ConfigClass
from ontology_dc8f06af066e4a7880a5938933236037.input import InputClass
from ontology_dc8f06af066e4a7880a5938933236037.output import OutputClass
from openfabric_pysdk.context import AppModel, State
from core.stub import Stub

session_memory = {}
# Configurations for the app
configurations: Dict[str, ConfigClass] = dict()

# Setup SQLite for long-term memory persistence
DB_PATH = "app/datastore/db.json"


# Database connection and schema design
def init_db():
    if not os.path.exists("app/datastore"):
        os.makedirs("app/datastore")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            prompt TEXT,
            expanded_prompt TEXT,
            image_url TEXT,
            model_3d_url TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

#Save the data that we get into the database that we had created for long term
def save_memory(user_id: str, prompt: str, expanded_prompt: str, image_url: str, model_3d_url: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO memory (user_id, prompt, expanded_prompt, image_url, model_3d_url)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, prompt, expanded_prompt, image_url, model_3d_url))
    conn.commit()
    conn.close()

############################################################
# Config callback function
############################################################
def config(configuration: Dict[str, ConfigClass], state: State) -> None:
    """
    Stores user-specific configuration data.

    Args:
        configuration (Dict[str, ConfigClass]): A mapping of user IDs to configuration objects.
        state (State): The current state of the application (not used in this implementation).
    """
    for uid, conf in configuration.items():
        logging.info(f"Saving new config for user with id:'{uid}'")
        configurations[uid] = conf


############################################################
# Execution callback function
############################################################

# I personally use llama 3.2 as it is light weight compared to llama 3 suitable for my system. Responses may vary as per the embeddings and tokens that it takes
def call_ollama_llama(prompt: str) -> str:
    """
    Calls the local Ollama Llama 3.2 model via CLI to process the prompt.
    Returns the model's response as a string.
    """
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


def execute(model: AppModel) -> None:
    """
    Main execution entry point for handling a model pass.

    Args:
        model (AppModel): The model object containing request and response structures.
    """

    # Initialize DB if not exists
    init_db()

    #to handle requests
    request: InputClass = model.request

    user_config: ConfigClass = configurations.get('super-user', None)
    logging.info(f"{configurations}")

    # To access the appid's we need to have the stub class from stub.py as mentioned in the readme
    app_ids = user_config.app_ids if user_config else []
    stub = Stub(app_ids)

    # ------------------------------

    prompt = call_ollama_llama(request.prompt)

    #Text-to-Image from Openfabric app
    text_to_image_id = "f0997a01-d6d3-a5fe-53d8-561300318557"
    text_image_stub = stub([text_to_image_id])
    text_image_response = text_image_stub.execute({
        "prompt": prompt,
    })

    # Get the image URL
    image_output = text_image_response.get("image_url", None)
    if not image_output:
        image_output = "Image generation failed"

    #Image-to-3D Openfabric app
    image_3d_id = "69543f29-4d41-4afc-7f29-3d51591f11eb"
    image_3d_stub = stub([image_3d_id])
    image_3d_response = image_3d_stub.execute({
        "image_url": image_output
    })

    model_3d_output = image_3d_response.get("model_3d_url", None)
    if not model_3d_output:
        model_3d_output = "3D image generation failed"

    # Save as session memeory which is temporary, after refresh it's gone as short memory
    session_memory['last_prompt'] = request.prompt
    session_memory['expanded_prompt'] = prompt
    session_memory['image_output'] = image_output
    session_memory['model_output'] = model_3d_output

    # Save long-term memory
    user_id = 'Self' #development purpose so 1 user
    save_memory(user_id, request.prompt, prompt, image_output, model_3d_output)
    # ------------------------------

    
    response: OutputClass = model.response
    response.message = (
        f"Original Prompt: {request.prompt}\n"
        f"Expanded Prompt: {prompt}\n"
        f"Image URL: {image_output}\n"
        f"3D Model URL: {model_3d_output}\n"
        f"Session memory stored and long-term memory saved."
    )