import requests
from bs4 import BeautifulSoup

url = "https://itexamanswers.net/ccna-3-v7-modules-1-2-ospf-concepts-and-configuration-exam-answers.html"
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, "html.parser")
content = soup.find("div", class_="thecontent") or soup.find("div", class_="entry-content")

uls = content.find_all("ul")
print(f"Total <ul> found in content: {len(uls)}")

with_answers = 0
for ul in uls:
    if ul.find(class_="correct_answer"):
        with_answers += 1

print(f"Total <ul> with class 'correct_answer': {with_answers}")