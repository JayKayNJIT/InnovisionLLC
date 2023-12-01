import os
from collections import Counter

def count_file_types(directory):
    file_types = Counter()
    file_sizes = {}
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            long_file_path = f"\\\\?\\{file_path}"  # Handling long file paths on Windows
            file_type = os.path.splitext(file)[1].lower()  # Convert file type to lowercase

            if file_type and os.path.exists(long_file_path):  # Check if file exists
                file_size = os.path.getsize(long_file_path)

                file_types[file_type] += 1
                file_sizes[file_type] = file_sizes.get(file_type, 0) + file_size

    # Convert sizes to MB
    for file_type in file_sizes:
        file_sizes[file_type] = file_sizes[file_type] / (1024 * 1024)

    return file_types, file_sizes

# Set the directory path
directory_path = 'D:\\Data\\OneDrive\\OneDrive-2023-11-30\\0.CFIR usaf Library'

file_type_counts, file_type_sizes = count_file_types(directory_path)

# Sorting by count in descending order
sorted_file_types = sorted(file_type_counts.items(), key=lambda x: x[1], reverse=True)

for file_type, count in sorted_file_types:
    size_mb = file_type_sizes[file_type]
    print(f"{file_type}: Count = {count}, Size = {size_mb:.2f} MB")
