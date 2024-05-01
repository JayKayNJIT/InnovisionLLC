import os
from collections import Counter
import shutil
import logging

def count_file_types(directory):
    file_types = Counter()
    file_sizes = {}
    total_file_count = 0  # Initialize a variable to keep track of the total file count
    total_pdf_count = 0
    total_pdf_size = 0

    # Remove existing logfile and target directory if they exist
    log_file = os.path.join(os.path.dirname(directory), '1Preproc_A_onlyPDFsTOsingleDirectory_log.txt')
    if os.path.exists(log_file):
        os.remove(log_file)
    
    pdf_dir = os.path.join(os.path.dirname(directory), '1GB_data_pdfs')
    if os.path.exists(pdf_dir):
        shutil.rmtree(pdf_dir)

    # Initialize logging
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            long_file_path = f"\\\\?\\{file_path}"  # Handling long file paths on Windows
            file_type = os.path.splitext(file)[1].lower()  # Convert file type to lowercase

            if file_type and os.path.exists(long_file_path):  # Check if file exists
                file_size = os.path.getsize(long_file_path)

                file_types[file_type] += 1
                file_sizes[file_type] = file_sizes.get(file_type, 0) + file_size
                total_file_count += 1  # Increment the total file count

                # Move PDF files to a new directory
                if file_type == '.pdf':
                    os.makedirs(pdf_dir, exist_ok=True)

                    # Check if the destination file already exists
                    dest_file = os.path.join(pdf_dir, file.lower())  # Ensure case insensitivity
                    if os.path.exists(dest_file):
                        # Rename the file to avoid conflicts
                        new_filename = file.split('.')[0] + '_1.pdf'
                        dest_file = os.path.join(pdf_dir, new_filename)
                        logging.info(f"Renamed file: {file} to {new_filename}")

                    # Check if the PDF is openable
                    try:
                        if os.path.exists(file_path):  # Check if file still exists
                            with open(file_path, 'rb') as f:
                                # Try to read the file to check if it's openable
                                f.read()
                        else:
                            raise FileNotFoundError(f"File not found: {file_path}")
                    except FileNotFoundError as e:
                        # Log the error without attempting to move the file
                        logging.error(f"File not found: {file_path}. Error: {str(e)}")
                    except Exception as e:
                        # If unable to open the PDF, delete it and log the error
                        os.remove(file_path)
                        logging.error(f"Unable to open PDF: {file}. Error: {str(e)}")
                    else:
                        # If PDF is openable, move it to the destination directory
                        shutil.move(file_path, dest_file)
                        total_pdf_count += 1
                        total_pdf_size += file_size

    # Convert sizes to GB
    for file_type in file_sizes:
        file_sizes[file_type] = file_sizes[file_type] / (1024 * 1024 * 1024)

    return file_types, file_sizes, total_file_count, total_pdf_count, total_pdf_size

# Set the directory path ("1GB_data" contains your raw databse)
directory_path = 'C:\\absolute\\path\\to\\your\\1GB_data'

file_type_counts, file_type_sizes, total_count, pdf_count, pdf_size = count_file_types(directory_path)

# Sorting by count in descending order
sorted_file_types = sorted(file_type_counts.items(), key=lambda x: x[1], reverse=True)

for file_type, count in sorted_file_types:
    size_gb = file_type_sizes[file_type]
    print(f"{file_type}: Count = {count}, Size = {size_gb:.2f} GB")

# Print the total file count
print(f"Total file count: {total_count}")

# Print the total number of PDF files transferred and their cumulative size
print(f"Total PDF files transferred: {pdf_count}, Total PDF size: {pdf_size / (1024 * 1024 * 1024):.2f} GB")
