# IT Exam to Quizizz Scraper

A Python toolkit designed to scrape question-and-answer sets from `itexamanswers.net` (filtering out diagram/image-dependent questions) and convert them directly into an Excel (`.xlsx`) file formatted for Quizizz spreadsheet import.

## Features
* Strips question numbers (`1. `, `Question 1:`) for clean presentation.
* Filters out image-heavy questions requiring diagrams or exhibits.
* Marks correct choices with an asterisk (`*`).
* Automatically formats output into Quizizz-ready `.xlsx` format (handling single-choice and multi-choice checkbox questions).

## Installation

1. Clone this repository:
   \`\`\`bash
   git clone https://github.com/pimdiaz/itexam-quizizz-scraper.git
   cd itexam-quizizz-scraper
   \`\`\`

2. (Optional) Create and activate a virtual environment:
   \`\`\`bash
   python3 -m venv venv
   source venv/bin/activate
   \`\`\`

3. Install required packages:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

## Usage

### 1. Scrape the Questions
Run `scraper.py` and pass the exam URL:
\`\`\`bash
python scraper.py "https://itexamanswers.net/your-target-exam-page.html"
\`\`\`
This produces `questions_with_answers.txt`.

### 2. Convert to Quizizz Format
Convert the text output into a Quizizz-compatible Excel file:
\`\`\`bash
python convert_to_quizizz.py questions_with_answers.txt
\`\`\`
This creates `quizizz_import.xlsx`.

### 3. Upload to Quizizz
Open [Quizizz](https://quizizz.com), select **Create Quiz** > **Import from spreadsheet**, and upload `quizizz_import.xlsx`.
