import pandas as pd
import sys
import os

def parse_text_to_quizizz_df(input_txt_file):
    with open(input_txt_file, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    # Split the file by double newlines to separate questions
    blocks = content.split('\n\n')
    
    quizizz_rows = []
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 2:
            continue
            
        question_text = lines[0].strip()
        choices = lines[1:]
        
        correct_answers = []
        option_columns = ["", "", "", "", ""] # Quizizz allows up to 5 options
        
        # Determine options and correct answer indices
        for idx, choice in enumerate(choices):
            if idx >= 5: # Quizizz maxes out at 5 options
                break
                
            clean_choice = choice.strip()
            if clean_choice.startswith('*'):
                correct_answers.append(str(idx + 1))
                clean_choice = clean_choice[1:] # Remove the asterisk
                
            option_columns[idx] = clean_choice
            
        # Determine question type
        if len(correct_answers) > 1:
            q_type = "Checkbox"
        else:
            q_type = "Multiple Choice"
            
        correct_answer_str = ",".join(correct_answers)
        
        # Build the row dictionary according to the Quizizz template
        row = {
            "Question Text": question_text,
            "Question Type": q_type,
            "Option 1": option_columns[0],
            "Option 2": option_columns[1],
            "Option 3": option_columns[2],
            "Option 4": option_columns[3],
            "Option 5": option_columns[4],
            "Correct Answer": correct_answer_str,
            "Time in seconds": 45,
            "Image Link": "",
            "Answer explanation": ""
        }
        quizizz_rows.append(row)
        
    df = pd.DataFrame(quizizz_rows)
    return df

def save_to_excel(df, output_filename="quizizz_import.xlsx"):
    # Create the exact header structure expected by Quizizz
    headers = [
        "Question Text", "Question Type", 
        "Option 1", "Option 2", "Option 3", "Option 4", "Option 5", 
        "Correct Answer", "Time in seconds", "Image Link", "Answer explanation"
    ]
    
    # Reorder columns to ensure exact match
    df = df[headers]
    
    # Save to Excel
    df.to_excel(output_filename, index=False, sheet_name="Create a Quiz")
    print(f"Successfully converted {len(df)} questions to {output_filename}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "questions_with_answers.txt"
        
    if not os.path.exists(input_file):
        print(f"Error: Could not find input file '{input_file}'")
        sys.exit(1)
        
    df = parse_text_to_quizizz_df(input_file)
    save_to_excel(df, "quizizz_import.xlsx")