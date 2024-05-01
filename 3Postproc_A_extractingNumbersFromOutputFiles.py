def clean_metadata_file(input_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        lines = input_file.readlines()

    # Find and remove metadata blocks containing "Empty Response"
    cleaned_lines = []
    skip_block = False
    for index, line in enumerate(lines):
        if 'Empty Response' in line and line.strip() == 'Empty Response':
            skip_block = True
            # Delete 3 lines before "Empty Response"
            if index >= 3:
                del cleaned_lines[-3:]
            else:
                cleaned_lines = []
            continue
        elif skip_block:
            # Delete 2 lines after "Empty Response"
            if index - lines.index(line) <= 2:
                continue
            else:
                skip_block = False
        cleaned_lines.append(line)

    # Write cleaned lines back to the original file
    with open(input_file_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(cleaned_lines)

    print("Input file cleaned.")

    # Now continue with the tasks from the previous code
    clean_metadata_continued(input_file_path)


def clean_metadata_continued(input_file_path):
    output_file_path = input_file_path.replace('.txt', '_2.txt')

    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        lines = input_file.readlines()

    # Remove lines starting with "Counter: Currently processing"
    lines = [line for line in lines if not line.startswith('Counter: Currently processing')]

    # Find and remove text chunks between "Response:" and "Stderr Output:"
    cleaned_lines = []
    skip_chunk = False
    for line in lines:
        if 'Response:' in line:
            skip_chunk = True
            continue
        elif 'Stderr Output:' in line:
            skip_chunk = False
            continue
        if not skip_chunk:
            cleaned_lines.append(line)

    # Delete the first four lines out of every five consecutive lines starting with "llama_print_timings:"
    consecutive_count = 0
    for index, line in enumerate(cleaned_lines):
        if line.startswith('llama_print_timings:'):
            consecutive_count += 1
            if consecutive_count <= 4:
                cleaned_lines[index] = ''
        else:
            consecutive_count = 0

    # Delete every line that starts with "Llama.generate:"
    cleaned_lines = [line for line in cleaned_lines if not line.startswith('Llama.generate:')]

    # Remove empty lines
    cleaned_lines = [line for line in cleaned_lines if line.strip()]

    # Process lines starting with "llama_print_timings:"
    for index, line in enumerate(cleaned_lines):
        if line.startswith('llama_print_timings:'):
            # Extract the two floating values
            values = line.split()
            first_value = float(values[4]) / 1000.0
            second_value = float(values[7])

            # Calculate TPS value
            tps_value = second_value / first_value

            # Replace the line with first floating value
            cleaned_lines[index] = f"Time in ms: {first_value:.2f}\n"

            # Insert second floating value and TPS value on subsequent lines
            cleaned_lines.insert(index + 1, f"Tokens: {second_value:.2f}\n")
            cleaned_lines.insert(index + 2, f"TPS: {tps_value:.2f}\n")

    # Add an empty line after every line that starts with "TPS:"
    for index, line in enumerate(cleaned_lines):
        if line.startswith('TPS:'):
            cleaned_lines.insert(index + 1, '\n')

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(cleaned_lines)

    print(f"Cleaned file saved as: {output_file_path}")


# Path to the input file
input_file_path = r'C:\absolute\path\to\title3060.txt'

# Call the function to clean the metadata file
clean_metadata_file(input_file_path)
