import sys
import re
import requests
from bs4 import BeautifulSoup

def clean_question_text(raw_text):
    """Strips leading question numbers or labels like '1. ', '12) ', 'Question 3: '."""
    pattern = r"^\s*(Question\s+\d+[\.\:\-]?\s*|\d+[\.\)\:\-]\s*)"
    return re.sub(pattern, "", raw_text, flags=re.IGNORECASE).strip()

def scrape_exam(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Ch-Ua": '"Chromium";v="124", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Linux"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    }

    print(f"[*] Fetching URL: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[!] Network error: {e}")
        sys.exit(1)

    soup = BeautifulSoup(response.text, "html.parser")
    content_area = soup.find("div", class_="entry-content") or soup.find("article")

    if not content_area:
        print("[!] Could not locate main post content.")
        sys.exit(1)

    cards = []
    question_regex = re.compile(r"^\s*(\d+[\.\)]|Question\s+\d+[:\.]?)", re.IGNORECASE)
    
    # Filter for diagram/image-dependent questions
    image_keywords_regex = re.compile(
        r"\b(refer\s+to\s+the\s+(exhibit|diagram|graphic|figure|image|topology)|"
        r"shown\s+in\s+the\s+(exhibit|diagram|figure)|"
        r"based\s+on\s+the\s+(exhibit|diagram|figure))\b",
        re.IGNORECASE
    )

    current_question = None
    current_choices = []
    has_image = False

    def should_keep_question(q_text, choices, had_img):
        """Returns True only if the question has choices, no img tag, and no exhibit keywords."""
        if not q_text or not choices or had_img:
            return False
        if image_keywords_regex.search(q_text):
            return False
        return True

    # Traverse child elements in order
    for element in content_area.find_all(["p", "ul", "ol", "div"]):
        text = element.get_text(" ", strip=True)

        # Flag presence of an image
        if element.find("img"):
            has_image = True

        # 1. Detect a new question starting
        if question_regex.match(text):
            # Evaluate and save previous question
            if should_keep_question(current_question, current_choices, has_image):
                cards.append({
                    "question": clean_question_text(current_question),
                    "choices": current_choices
                })

            current_question = text
            current_choices = []
            has_image = bool(element.find("img"))

        # 2. Detect the choices list (ul or ol)
        elif element.name in ["ul", "ol"] and current_question:
            if element.find("img"):
                has_image = True

            for li in element.find_all("li"):
                choice_text = li.get_text(" ", strip=True)
                if not choice_text:
                    continue

                # Check if choice or any child has class 'correct_answer'
                has_correct_class = (
                    "correct_answer" in li.get("class", []) or
                    bool(li.find(class_="correct_answer"))
                )

                if has_correct_class:
                    choice_text = f"*{choice_text}"

                current_choices.append(choice_text)

    # Process the final question block after loop ends
    if should_keep_question(current_question, current_choices, has_image):
        cards.append({
            "question": clean_question_text(current_question),
            "choices": current_choices
        })

    return cards

def save_output(cards, output_txt="questions_with_answers.txt"):
    if not cards:
        print("[!] No text-only questions found.")
        return

    with open(output_txt, "w", encoding="utf-8") as f:
        for item in cards:
            f.write(f"{item['question']}\n")
            for choice in item["choices"]:
                f.write(f"{choice}\n")
            f.write("\n")

    print(f"[+] Successfully extracted {len(cards)} clean questions (without numbers).")
    print(f"[+] Saved output to: {output_txt}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        target_url = input("Enter exam URL: ").strip()

    extracted_cards = scrape_exam(target_url)
    save_output(extracted_cards)