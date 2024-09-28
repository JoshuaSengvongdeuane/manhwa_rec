import requests
import os

manga_id = '4141c5dc-c525-4df5-afd7-cc7d192a832f'
languages = ['en']
base_url = "https://api.mangadex.org"

# Fetch all chapter IDs in the correct order
all_chapters = []
limit = 100
offset = 0

while True:
    response = requests.get(
        f"{base_url}/manga/{manga_id}/feed",
        params={
            "translatedLanguage[]": languages,
            "limit": limit,
            "offset": offset
        }
    )
    if response.status_code == 200:
        data = response.json()
        if not data["data"]:
            break
        for chapter in data["data"]:
            chapter_id = chapter["id"]
            chapter_number = chapter["attributes"]["chapter"]
            all_chapters.append((chapter_id, chapter_number))
        offset += limit
    else:
        print(f"Failed to retrieve chapters: {response.status_code}")
        break

# Sort chapters by chapter number
all_chapters.sort(key=lambda x: float(x[1]))

seen = set()

filtered_chaps= []
for id, chp_num in all_chapters:
    if chp_num not in seen:
        filtered_chaps.append((id, chp_num))
        seen.add(chp_num)

# Obtain all chapter IDs sorted in order
sorted_chapter_ids = [i[0] for i in filtered_chaps]
print(sorted_chapter_ids)
# Create the main folder for storing manga images
main_folder = "Mangadex"
os.makedirs(main_folder, exist_ok=True)

# Manual chapter counter
chapter_counter = 1

# Fetch and save chapter images
for chapter_id in sorted_chapter_ids:
    r = requests.get(f"{base_url}/at-home/server/{chapter_id}")
    r_json = r.json()

    host = r_json["baseUrl"]
    chapter_hash = r_json["chapter"]["hash"]
    data = r_json["chapter"]["data"]

    # Skip chapters with 0 pages
    if not data:
        print(f"Chapter (ID: {chapter_id}) has 0 pages. Skipping.")
        continue

    # Create a folder for each chapter only if it has pages
    folder_path = f"{main_folder}/Chapter_{chapter_counter}"
    os.makedirs(folder_path, exist_ok=True)

    # Save each page in the chapter
    for page_num, page in enumerate(data, 1):
        image_url = f"{host}/data/{chapter_hash}/{page}"
        image_response = requests.get(image_url)

        # Extract file extension from the image name
        ext = os.path.splitext(page)[-1]

        # Save the image with the correct extension and page number
        with open(f"{folder_path}/Page_{page_num}{ext}", mode="wb") as f:
            f.write(image_response.content)

    print(f"Downloaded {len(data)} pages for Chapter {chapter_counter} and ID: {chapter_id}")
    
    # Increment chapter counter only if pages were downloaded
    chapter_counter += 1
