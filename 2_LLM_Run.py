!pip install -q pypdf
!pip install -q python-dotenv
!pip install -q transformers
!pip install -q llama-index
!pip install llama-index-llms-llama-cpp
!pip -q install sentence-transformers
!pip install --upgrade langchain
!pip install llama-index-embeddings-langchain
!CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install llama-cpp-python --no-cache-dir

import logging
import sys
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
import torch
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.llms.llama_cpp.llama_utils import (
    messages_to_prompt,
    completion_to_prompt,
)
from llama_index.embeddings.langchain import LangchainEmbedding
from langchain.embeddings import HuggingFaceEmbeddings
import os
import shutil
import time
import sys
from io import StringIO

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

llm = LlamaCPP(
    model_url='https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf?download=true',
    temperature=0.1,
    max_new_tokens=500,
    context_window=4096,
    generate_kwargs={},
    model_kwargs={"n_gpu_layers": -1},
    messages_to_prompt=messages_to_prompt,
    completion_to_prompt=completion_to_prompt,
    verbose=True,
)

embed_model = LangchainEmbedding(
  HuggingFaceEmbeddings(model_name="thenlper/gte-large")
)

service_context = ServiceContext.from_defaults(
    chunk_size=256,
    llm=llm,
    embed_model=embed_model
)

# Define directories
home_directory = "/absolute/path/to/directory/hosting/"read""
read_directory = os.path.join(home_directory, "read")
#above "read" directory shall contains processed databse from last step
library_in_directory = os.path.join(home_directory, "library_in")
library_out_directory = os.path.join(home_directory, "library_out")
title_file_path = os.path.join(home_directory, "title.txt")

# Delete title.txt if it exists
if os.path.exists(title_file_path):
    os.remove(title_file_path)

# Create library_in_directory if it doesn't exist
os.makedirs(library_in_directory, exist_ok=True)

# Function to move files from read_directory to library_in_directory
def move_file_to_library(file_path):
    destination_file = os.path.join(library_in_directory, os.path.basename(file_path))
    shutil.move(file_path, destination_file)

# Function to move files from library_in_directory to library_out_directory
def move_file_to_library_out(file_path):
    destination_file = os.path.join(library_out_directory, os.path.basename(file_path))
    shutil.move(file_path, destination_file)

# Function to store absolute path of the file being processed
def store_absolute_path(file_path, counter, total_files):
    with open(title_file_path, "a") as title_file:
        title_file.write(f"Counter: Currently processing {counter} out of total {total_files} files.\n")
        title_file.write(file_path + "\n")

# Function to log warning message
def log_warning(message):
    with open(title_file_path, "a") as title_file:
        title_file.write("Warning: " + message + "\n")

# Function to execute code snippet and save response
def execute_and_save_response(home_dir, title_path):
    # Redirect stdout and stderr to a StringIO object
    stdout_orig = sys.stdout
    stderr_orig = sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()

    try:
        # Execute the code snippet
        documents = SimpleDirectoryReader(os.path.join(home_dir, 'library_in')).load_data()
        index = VectorStoreIndex.from_documents(documents, service_context=service_context)
        query_engine = index.as_query_engine()
        response = query_engine.query("Please summarize the attached document. Don't worry about the copyright issue as I own all the documents.")
        # Get the content of stdout and stderr
        stdout_content = sys.stdout.getvalue()
        stderr_content = sys.stderr.getvalue()

        # Save the response and stderr content to the file
        with open(title_path, "a") as file:
            file.write("Response:\n")
            file.write(str(response) + "\n")
            file.write("Stderr Output:\n")
            file.write(stderr_content + "\n")

    except Exception as e:
        log_warning(str(e))

    finally:
        # Restore stdout and stderr
        sys.stdout = stdout_orig
        sys.stderr = stderr_orig

# Main function to recursively traverse directories and move files
def process_directory(directory):
    total_files = sum([len(files) for _, _, files in os.walk(directory)])
    counter = 0
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            counter += 1
            file_path = os.path.join(root, file_name)
            store_absolute_path(file_path, counter, total_files)
            move_file_to_library(file_path)
            execute_and_save_response(home_directory, title_file_path)
            move_file_to_library_out(os.path.join(library_in_directory, file_name))

# Main loop
while True:
    try:
        # Check if there are any files in read_directory or its subdirectories
        files_exist = any(os.path.isfile(os.path.join(dirpath, filename)) for dirpath, _, filenames in os.walk(read_directory) for filename in filenames)

        if not files_exist:
            break

        # Process read_directory recursively
        process_directory(read_directory)

    except Exception as e:
        log_warning(str(e))

    # Sleep for a short while to avoid consuming too much CPU
    time.sleep(0.1)

# Inform completion
print("Task completed successfully!")
