import requests, time
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
from collections import deque

#LLM/AI scoring appraoch
# stuff for the LLM/AI score thing
embedder = SentenceTransformer("all-MiniLM-L6-v2")
target_word = "Goku Dragon Ball character"
target_embedding = embedder.encode(target_word, convert_to_tensor=True)
# score = 0 

# header needed to access the wiki content
headers = {
    'User-Agent': 'wiki-race-bot (contact: dedgardo381@gmail.com)'
}

# # starting URL, response to get the content on the page, current link, and the target link
# url ='https://en.wikipedia.org/wiki/Biology'
# response = requests.get(url, headers=headers)
# current_link = "/wiki/Biology"


# set that will help us keep track of every URL we've visited so that our script doesn't end up on an infinite loop or visit the same URL multiple times
# visited = {current_link}


# this functions grabs every on the content page, and adds them to the set as well as the candidate list which will used to determine the next best link to go to
# def get_links(url):
#     response = requests.get(url, headers=headers)

#     # initialize soup and content, soup is the parser and content is the main content on a wiki page
#     soup = BeautifulSoup(response.text, 'html.parser')
#     content = soup.find('div', id="mw-content-text")

#     candidates = []

#     if content:
#         links = content.find_all('a', href=True)
#         for link in links:
#             href = link.get("href")
#             text = link.get_text().strip()

#             if (
#                 href.startswith("/wiki/")
#                 and ":" not in href
#                 and not href.endswith((".png", ".svg", ".jpg", ".jpeg"))
#                 and text
#                 and href not in visited
#             ):
#                 candidate = {
#                     "text": text,
#                     "url": href,
#                     "score": 0
#                 }
#                 candidates.append(candidate)
#         if candidates:
#             text_score = [c['text'] for c in candidates]

#             candidate_embeddings = embedder.encode(text_score, convert_to_tensor=True)
#             cosine_scores = util.cos_sim(candidate_embeddings, target_embedding)

#             for i in range(len(candidates)):
#                 candidates[i]['score'] = cosine_scores[i].item()

#             return max(candidates, key=lambda x: x['score'])

#     return None

# # while loop to keep searching for the target until we find it, this also keeps tracks of waht links we have visited
# while current_link != "/wiki/Goku":
#     full_url = "https://en.wikipedia.org" + current_link
#     winner = get_links(full_url)

#     if winner:
#         current_link = winner['url']
#         visited.add(current_link)

#         print(f"Jumped to: {winner['url']} | Score: {winner['score']:.4f}")

#         time.sleep(0.1)  # be nice to Wikipedia's servers
#     else:
#         break

# bfs appraoch
# visited = set()

# def get_all_links(url):
#     time.sleep(0.1)
#     response = requests.get(url, headers=headers)

#     soup = BeautifulSoup(response.text, 'html.parser')
#     content = soup.find('div', id="mw-content-text")
#     links = []

#     if content:
#         all_links = content.find_all('a', href=True)
#         for link in all_links:
#             href = link.get("href")
#             text = link.get_text().strip()

#             if (
#                 href.startswith("/wiki/")
#                 and ":" not in href
#                 and not href.endswith((".png", ".svg", ".jpg", ".jpeg"))
#                 and text
#             ):
#                 links.append(href)

#     return links


# def bfs(start, target):
#     queue = deque([(start,[start])])
#     visited = {start}

#     while queue:
#         current, path = queue.popleft()
        
#         print(f"Exploring: {current}")

#         if current == target:
#             return path
        
#         links = get_all_links("https://en.wikipedia.org" + current)
#         for link in links:
#             if link not in visited:
#                 visited.add(link)
#                 queue.append((link, path + [link]))

#     return None

# starting_link = "/wiki/Biology"
# target_link = "/wiki/Goku"

# print(f"Starting BFS from {starting_link} to {target_link}")
# result = bfs(starting_link, target_link)

# if result:
#     print("Path found:")
#     for step in result:
#         print(f"-> {step}")
# else:
#     print("No path found.")

# beam search approach

visited = set()

def links_with_scores(url):
    time.sleep(0.1)
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, 'html.parser')
    content = soup.find('div', id="mw-content-text")

    candidates = []

    if content:
        all_links = content.find_all('a', href=True)
        for link in all_links:
            href = link.get("href")
            text = link.get_text().strip()

            if (
                href.startswith("/wiki/")
                and ":" not in href
                and not href.endswith((".png", ".svg", ".jpg", ".jpeg"))
                and text
            ):
                candidates.append({
                    "text": text,
                    "url": href,
                    "score": 0,
                })
        if candidates:
            texts = [c['text'] for c in candidates]
            candidate_embeddings = embedder.encode(texts, convert_to_tensor=True)
            cosine_scores = util.cos_sim(candidate_embeddings, target_embedding)

            for i, candidate in enumerate(candidates):
                candidate['score'] = cosine_scores[i].item()

            candidates.sort(key=lambda x: x['score'], reverse=True)

    
    return candidates

def beam_search(start, target, beam_width = 5):
    current_beam = [(start, [start])]
    visited.add(start)
    
    depth = 0

    while current_beam:
        print(f"Depth: {depth}: Exploring {len(current_beam)} paths")

        next_beam = []

        for current_url, path in current_beam:
            if current_url == target:
                return path
            
            full_url = "https://en.wikipedia.org" + current_url
            candidates = links_with_scores(full_url)

            print(f" {current_url}: Found {len(candidates)} candidates")

            for candidate in candidates[:beam_width]:
                if candidate['url'] not in visited:
                    visited.add(candidate['url'])
                    next_beam.append((candidate['url'], path + [candidate['url']], candidate['score']))

        next_beam.sort(key=lambda x: x[2], reverse=True)
        current_beam = [(url, path) for url, path, score in next_beam[:beam_width]]

        depth += 1

        if depth > 20:
            print("Max depth.")
            break
    return None

start_link = "/wiki/Biology"
target_link = "/wiki/Goku"

print(f"Starting beam search from {start_link} to {target_link}")
print(f"Beam width: 5")

result = beam_search(start_link, target_link, beam_width = 5)

if result:
    print(f"Found path in {len(result)-1} steps:")
    for i, step in enumerate(result):
        print(f" {i}. {step}")
else:
    print("No path found.")
