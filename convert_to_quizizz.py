import sys
import os
import re
import pandas as pd

def parse_txt_to_quizizz(txt_filepath):
    if not os.path.exists(txt_filepath):
        print(f"[!] File not found: {txt_filepath}")
        sys.exit(1)

    with open(txt_filepath, "r", encoding="utf-8") as f:
        raw_text = f.read()

    blocks = [b.strip() for b in raw_text.split("\n\n") if b.strip()]
    rows = []

    for block in blocks:
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        if len(lines) < 3:
            continue

        question_text = lines[0]
        image_url = ""
        choice_lines = []

        for line in lines[1:]:
            img_match = re.match(r"^\[IMAGE:\s*(https?://[^\s\]]+)\]", line, re.IGNORECASE)
            if img_match:
                image_url = img_match.group(1)
            else:
                choice_lines.append(line)

        options = []
        correct_answers = []

        for idx, line in enumerate(choice_lines, start=1):
            if line.startswith("*"):
                options.append(line.lstrip("*").strip())
                correct_answers.append(str(idx))
            else:
                options.append(line)

        if not correct_answers or len(options) < 2:
            continue

        # Quizizz expects "Checkbox" for multiple correct answers
        question_type = "Checkbox" if len(correct_answers) > 1 else "Multiple Choice"
        correct_ans_str = ",".join(correct_answers)

        row = {
            "Question Text": question_text,
            "Question Type": question_type,
            "Option 1": options[0] if len(options) > 0 else "",
            "Option 2": options[1] if len(options) > 1 else "",
            "Option 3": options[2] if len(options) > 2 else "",
            "Option 4": options[3] if len(options) > 3 else "",
            "Option 5": options[4] if len(options) > 4 else "",
            "Correct Answer": correct_ans_str,
            "Time in seconds": 45,
            "Image Link": image_url
        }
        rows.append(row)

    columns = [
        "Question Text",
        "Question Type",
        "Option 1",
        "Option 2",
        "Option 3",
        "Option 4",
        "Option 5",
        "Correct Answer",
        "Time in seconds",
        "Image Link"
    ]

    df = pd.DataFrame(rows, columns=columns)
    output_xlsx = "quizizz_import.xlsx"
    df.to_excel(output_xlsx, index=False)
    print(f"[+] Converted {len(rows)} questions into '{output_xlsx}' with Image Links included!")

if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "questions_with_answers.txt"
    parse_txt_to_quizizz(filepath)