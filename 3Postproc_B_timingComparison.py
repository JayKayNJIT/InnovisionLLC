import re

file_paths = [
    'C:\\absolute\\path\\to\\title3060_2.txt',
    'C:\\absolute\\path\\to\\title3090_Ti_2.txt'
]

def remove_empty_lines(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Remove empty lines
    non_empty_lines = [line for line in lines if line.strip()]
    
    # Remove anything before "/read/" in specific lines
    for i in range(0, len(non_empty_lines), 4):
        non_empty_lines[i] = re.sub(r'.*/read/', '/read/', non_empty_lines[i])

    with open(file_path, 'w') as file:
        file.writelines(non_empty_lines)

def extract_float(string):
    # Use regular expression to find the floating point number
    match = re.search(r'[-+]?\d*\.\d+|\d+', string)
    if match:
        return float(match.group())
    else:
        return None

def compare_metadata_blocks(file1, file2):
    with open(file1, 'r') as f1:
        lines1 = f1.readlines()
    with open(file2, 'r') as f2:
        lines2 = f2.readlines()

    comparison_file = open("comparison.txt", "w")
    log_file = open("comparison_log.txt", "w")

    count_bigger = 0
    total_comparisons = 0

    for i in range(0, len(lines1), 4):
        pdf_name = lines1[i].strip()
        time1_str = lines1[i+3].strip()
        time1 = extract_float(time1_str)
        found_match = False

        for j in range(0, len(lines2), 4):
            if pdf_name == lines2[j].strip():
                time2_str = lines2[j+3].strip()
                time2 = extract_float(time2_str)
                if time1 is not None and time2 is not None:
                    difference = time1 - time2
                    comparison_file.write(f"Difference for {pdf_name}: {difference}\n")
                    comparison_file.write(f"Time in file1: {time1_str}\n")
                    comparison_file.write(f"Time in file2: {time2_str}\n\n")
                    if difference > 0:
                        count_bigger += 1
                    found_match = True
                else:
                    log_file.write(f"Error extracting time for PDF: {pdf_name}\n")
                break

        if not found_match:
            log_file.write(f"No match found for PDF: {pdf_name}\n")

        total_comparisons += 1

    comparison_file.write(f"Percentage of times first timing was bigger than second: {(count_bigger / total_comparisons) * 100:.2f}%\n")

    comparison_file.close()
    log_file.close()

def main():
    for path in file_paths:
        remove_empty_lines(path)

    compare_metadata_blocks(file_paths[0], file_paths[1])

if __name__ == "__main__":
    main()
