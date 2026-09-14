import sys
import re
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

def clean_question_text(raw_text):
    """Strips leading question numbers like '1. ', '50. ', 'Question 1: ', etc."""
    pattern = r"^\s*(Question\s+\d+[\.\:\-]?\s*|\d+[\.\)\:\-]\s*)"
    return re.sub(pattern, "", raw_text, flags=re.IGNORECASE).strip()

async def fetch_full_rendered_html(url):
    print(f"[*] Launching headless browser for: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Navigate to the page
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Scroll down incrementally to trigger FlyingPress lazy-loading
        print("[*] Scrolling to trigger lazy-loaded questions...")
        for _ in range(10):
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight / 10);")
            await asyncio.sleep(0.5)

        # Ensure we hit the very bottom
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        await asyncio.sleep(2)

        content = await page.content()
        await browser.close()
        return content

def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    content_area = (
        soup.find("div", class_="thecontent") or 
        soup.find("div", class_="entry-content") or 
        soup.find("article")
    )

    if not content_area:
        print("[!] Could not locate content area.")
        return []

    # Filter out questions that explicitly require an image/diagram
    image_keywords_regex = re.compile(
        r"\b(refer\s+to\s+the\s+(exhibit|diagram|graphic|figure|image|topology)|"
        r"shown\s+in\s+the\s+(exhibit|diagram|figure)|"
        r"based\s+on\s+the\s+(exhibit|diagram|figure))\b",
        re.IGNORECASE
    )

    cards = []
    
    # Target all unordered lists
    for ul in content_area.find_all("ul"):
        if ul.find_parent(class_=re.compile(r"(sharedaddy|heateor|menu|widget|nav|comments|sidebar)", re.I)):
            continue

        # Look for the correct_answer class
        has_correct = False
        choices = []

        # Remove copy buttons injected by scripts
        for btn in ul.find_all("button", class_=re.compile("copy", re.I)):
            btn.decompose()

        for li in ul.find_all("li", recursive=False):
            choice_text = li.get_text(" ", strip=True)
            if not choice_text:
                continue

            is_correct = (
                "correct_answer" in li.get("class", []) or
                bool(li.find(class_=re.compile(r"correct_answer", re.I))) or
                bool(li.find(["strong", "b"]))
            )

            if is_correct:
                choice_text = f"*{choice_text}"
                has_correct = True

            choices.append(choice_text)

        if not choices or not has_correct:
            continue

        # Find the question paragraph preceding this list
        q_text = None
        for prev in ul.find_all_previous(["p", "h2", "h3", "h4"]):
            text = prev.get_text(" ", strip=True)
            if len(text) < 15:
                continue
            if re.search(r'^(Explanation|How to find|Note:|Advertisements)', text, re.IGNORECASE):
                continue
            q_text = text
            break

        if not q_text or image_keywords_regex.search(q_text):
            continue

        cards.append({
            "question": clean_question_text(q_text),
            "choices": choices
        })

    return cards

def save_output(cards, output_txt="questions_with_answers.txt"):
    if not cards:
        print("[!] No questions extracted.")
        return

    with open(output_txt, "w", encoding="utf-8") as f:
        for item in cards:
            f.write(f"{item['question']}\n")
            for choice in item["choices"]:
                f.write(f"{choice}\n")
            f.write("\n")

    print(f"[+] Successfully extracted {len(cards)} clean questions!")
    print(f"[+] Output written to: {output_txt}")

async def main():
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        target_url = input("Enter exam URL: ").strip()

    html = await fetch_full_rendered_html(target_url)
    cards = parse_html(html)
    save_output(cards)

if __name__ == "__main__":
    asyncio.run(main())
