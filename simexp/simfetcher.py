import requests

def fetch_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def fetch_all_content(sources):
    content = {}
    for url in sources.keys():
        html_content = fetch_content(url)
        if html_content:
            content[url] = html_content
    return content