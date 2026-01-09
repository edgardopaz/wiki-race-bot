import requests, time
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util


# stuff for the LLM/AI score thing
embedder = SentenceTransformer("all-MiniLM-L6-v2")
target_word = "Goku Dragon Ball character"
target_embedding = embedder.encode(target_word, convert_to_tensor=True)
score = 0 

# header needed to access the wiki content
headers = {
    'User-Agent': 'wiki-race-bot (contact: dedgardo381@gmail.com)'
}

# starting URL, response to get the content on the page, current link, and the target link
url ='https://en.wikipedia.org/wiki/Biology'
response = requests.get(url, headers=headers)
current_link = "/wiki/Biology"


# set that will help us keep track of every URL we've visited so that our script doesn't end up on an infinite loop or visit the same URL multiple times
visited = {current_link}

# this functions grabs every on the content page, and adds them to the set as well as the candidate list which will used to determine the next best link to go to
def get_links(url):
    response = requests.get(url, headers=headers)

    # initialize soup and content, soup is the parser and content is the main content on a wiki page
    soup = BeautifulSoup(response.text, 'html.parser')
    content = soup.find('div', id="mw-content-text")

    candidates = []

    if content:
        links = content.find_all('a', href=True)
        for link in links:
            href = link.get("href")
            text = link.get_text().strip()

            if (
                href.startswith("/wiki/")
                and ":" not in href
                and not href.endswith((".png", ".svg", ".jpg", ".jpeg"))
                and text
                and href not in visited
            ):
                candidate = {
                    "text": text,
                    "url": href,
                    "score": 0
                }
                candidates.append(candidate)
        if candidates:
            text_score = [c['text'] for c in candidates]

            candidate_embeddings = embedder.encode(text_score, convert_to_tensor=True)
            cosine_scores = util.cos_sim(candidate_embeddings, target_embedding)

            for i in range(len(candidates)):
                candidates[i]['score'] = cosine_scores[i].item()

            return max(candidates, key=lambda x: x['score'])

    return None

# while loop to keep searching for the target until we find it, this also keeps tracks of waht links we have visited
while current_link != "/wiki/Goku":
    full_url = "https://en.wikipedia.org" + current_link
    winner = get_links(full_url)

    if winner:
        current_link = winner['url']
        visited.add(current_link)

        print(f"Jumped to: {winner['url']} | Score: {winner['score']:.4f}")

        time.sleep(0.1)  # be nice to Wikipedia's servers
    else:
        break
