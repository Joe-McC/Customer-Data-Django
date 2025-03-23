#!/usr/bin/env python
"""
Script to manually check and modify the models.py file to ensure
there is no Token class causing conflicts
"""

import os

def main():
    models_file = os.path.join(os.path.dirname(__file__), 'models.py')
    
    if not os.path.exists(models_file):
        print(f"ERROR: Models file not found at {models_file}")
        return
    
    print(f"Opening {models_file} to check for Token class...")
    
    # Read the content
    with open(models_file, 'r') as f:
        lines = f.readlines()
    
    # Print the last 10 lines for analysis
    print("Last 10 lines of the file:")
    for line in lines[-10:]:
        print(f"> {line.rstrip()}")
    
    # Check if there's a Token class at the end
    contains_token = False
    for i in range(len(lines)-1, max(0, len(lines)-30), -1):
        if "class Token" in lines[i]:
            contains_token = True
            print(f"Found 'class Token' at line {i+1}: {lines[i].strip()}")
            # Mark where to start removing
            token_start = i
            # Find where the class definition ends (next class or EOF)
            token_end = len(lines)
            for j in range(i+1, len(lines)):
                if lines[j].startswith('class ') or j == len(lines)-1:
                    token_end = j
                    break
            print(f"Token class spans from line {token_start+1} to {token_end}")
            # Remove the Token class
            lines = lines[:token_start] + lines[token_end:]
            break
    
    if not contains_token:
        print("No Token class found in the last 30 lines of the file")
    
    # Write the modified file
    with open(models_file, 'w') as f:
        f.writelines(lines)
    
    print(f"File processed: {models_file}")
    print("Please restart the Django server")

if __name__ == "__main__":
    main() 