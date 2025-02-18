#!/usr/bin/env python3

import os

# Specify the names of the script file and output file to exclude them
SCRIPT_NAME = "FileTree.py"
OUTPUT_FILE = "FileTree.txt"
EXCLUDED_FILES = {SCRIPT_NAME, OUTPUT_FILE, ".DS_Store", "__init__.py", "FileTree.old.txt"}
EXCLUDED_DIRS = {"__pycache__", "migrations", "static", "staticfiles", "media", ".venv", ".idea"}  # Exclude directories like __pycache__

def generate_file_tree(output_file):
    """Generate a pretty file tree of the current directory and subdirectories."""
    with open(output_file, 'w') as f:
        for root, dirs, files in os.walk('.'):  # Walk through the directory tree
            # Remove excluded directories from the traversal
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            level = root.count(os.sep)
            indent = '│   ' * level
            f.write(f"{indent}├── {os.path.basename(root)}/\n")
            sub_indent = '│   ' * (level + 1)
            for i, file in enumerate(files):
                if file not in EXCLUDED_FILES:
                    connector = '└── ' if i == len(files) - 1 else '├── '
                    f.write(f"{sub_indent}{connector}{file}\n")

def append_file_contents(output_file):
    """Append contents of each file in the current directory and subdirectories to the output file, excluding specified files."""
    # Determine the maximum width for the boxes
    max_width = 20  # Default minimum width
    file_paths = []
    for root, dirs, files in os.walk('.'):  # Walk through the directory tree
        # Remove excluded directories from the traversal
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file_name in files:
            if file_name not in EXCLUDED_FILES:
                file_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(file_path, start='.')
                directory = os.path.dirname(relative_path)
                base_name = os.path.basename(relative_path)
                file_paths.append((directory, base_name))
                max_width = max(max_width, len(directory) + 10, len(base_name) + 10)

    max_width += 4  # Add padding for aesthetics

    # Append file contents with uniform box size
    with open(output_file, 'a') as f:
        for directory, base_name in file_paths:
            # Add the formatted header for the file
            horizontal_line = f"┌{'─' * max_width}┐"
            directory_line = f"│ Directory: {directory:<{max_width - 12}}│"
            file_line = f"│ File:      {base_name:<{max_width - 12}}│"
            bottom_line = f"└{'─' * max_width}┘"

            f.write(f"\n{horizontal_line}\n")
            f.write(f"{directory_line}\n")
            f.write(f"{file_line}\n")
            f.write(f"{bottom_line}\n\n")

            # Append the contents of the file
            file_path = os.path.join(directory, base_name)
            try:
                with open(file_path, 'r', errors='ignore') as file:
                    f.write(file.read())
            except Exception as e:
                f.write(f"Error reading {file_path}: {e}\n")

            # Add a visually distinct footer to signify the end of the file
            f.write(f"\n========= END OF FILE =========\n")
            f.write(f"File: {base_name}\n")
            f.write(f"===============================\n\n")

def main():
    generate_file_tree(OUTPUT_FILE)
    append_file_contents(OUTPUT_FILE)

if __name__ == "__main__":
    main()
