import os
from collections import Counter
import fitz  # PyMuPDF

def count_file_types(directory):
    file_types = Counter()
    file_sizes = {}
    scanned_pdf_count = 0
    non_scanned_pdf_count = 0

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            long_file_path = f"\\\\?\\{file_path}"  # Handling long file paths on Windows
            file_type = os.path.splitext(file)[1].lower()

            if file_type and os.path.exists(long_file_path):
                file_size = os.path.getsize(long_file_path)

                if file_type == '.pdf':
                    if is_scanned_pdf(long_file_path):
                        scanned_pdf_count += 1
                    else:
                        non_scanned_pdf_count += 1

                file_types[file_type] += 1
                file_sizes[file_type] = file_sizes.get(file_type, 0) + file_size

    # Convert sizes to MB
    for file_type in file_sizes:
        file_sizes[file_type] = file_sizes[file_type] / (1024 * 1024)

    return file_types, file_sizes, scanned_pdf_count, non_scanned_pdf_count

def is_scanned_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return len(text.strip()) < 300  # Threshold for considering a PDF as scanned
    except:
        return True  # If there's an error opening the PDF, it might be scanned/image-based

# Set the directory path
directory_path = 'D:\\Data\\OneDrive\\OneDrive-2023-11-30\\0.CFIR usaf Library'

file_type_counts, file_type_sizes, scanned_pdf_count, non_scanned_pdf_count = count_file_types(directory_path)

# Sorting by count in descending order
sorted_file_types = sorted(file_type_counts.items(), key=lambda x: x[1], reverse=True)

for file_type, count in sorted_file_types:
    size_mb = file_type_sizes[file_type]
    print(f"{file_type}: Count = {count}, Size = {size_mb:.2f} MB")

print(f"\nScanned PDFs: {scanned_pdf_count}")
print(f"Non-Scanned PDFs: {non_scanned_pdf_count}")
