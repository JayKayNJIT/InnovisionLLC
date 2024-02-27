#Step 1: Setup the environment
from dotenv import load_dotenv
load_dotenv()
import os
import openai
import glob
import time

openai_api_key = "sk-XXX"
openai_client = openai.OpenAI(api_key=openai_api_key)

# Specify the directory for PDF files and output file
pdf_files_dir = "C:\\Users\\JatinK\\OneDrive - Innovision, LLC\\onGoing_projects\\IDEEP\\knowledge_center\\AssistantAPI\\files"
output_file_path = os.path.join(pdf_files_dir, "output.txt")

# Delete the old output.txt file if it exists
try:
    os.remove(output_file_path)
    print("Existing output.txt file deleted.")
except FileNotFoundError:
    print("No existing output.txt file to delete.")

#Step 2: Loop over all the PDF files in the directory and all sub-directories
pdf_files = glob.glob(os.path.join(pdf_files_dir, "**", "*.pdf"), recursive=True)

for pdf_file in pdf_files:
    # Print the name and path of the PDF file
    print(f"Processing file: {pdf_file}")
    
    # Upload the PDF file
    with open(pdf_file, "rb") as file:
        uploaded_file = openai_client.files.create(file=file, purpose='assistants')
    
    # Retrieve the file by id to make sure the file is successfully uploaded.
    retrieved_file = openai_client.files.retrieve(uploaded_file.id)
    
    # Create an Assistant
    assistant = openai_client.beta.assistants.create(
      instructions="Use the file provided as your knowledge base to best respond to customer queries.",
      model="gpt-3.5-turbo-0125",
      tools=[{ "type": "retrieval" }],
      file_ids=[retrieved_file.id]
    )
    
    # Create a Thread
    thread = openai_client.beta.threads.create()
    
    # Create a Message
    thread_message = openai_client.beta.threads.messages.create(
      thread_id=thread.id,
      role="user",
      content="Please show me the content architecture of this document",
    )
    
    # Create a Run
    run = openai_client.beta.threads.runs.create(
      thread_id=thread.id,
      assistant_id=assistant.id
    )
    
    # Wait for the Run to complete
    while True:
        retrieved_run = openai_client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if retrieved_run.status == "completed":
            break
        time.sleep(5)  # Wait for 5 seconds before checking again
    
    # Retrieve the message list of the Thread.
    thread_messages = openai_client.beta.threads.messages.list(thread.id)
    response_message = thread_messages.data[0].content[0].text.value
    print(response_message)
    
    # Write the response message to the output file, specifying UTF-8 encoding
    with open(output_file_path, "a", encoding="utf-8") as output_file:
        output_file.write(f"File: {pdf_file}\n{response_message}\n\n")

    
    # Delete the attached file, Thread, and Assistant before continuing to the next file
    openai_client.files.delete(retrieved_file.id)
    openai_client.beta.threads.delete(thread.id)
    openai_client.beta.assistants.delete(assistant.id)
