"""Find RSS feed from site's LINK tag using BeautifulSoup."""

__version__ = "2.0.0"

import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def getRSSLink(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for alternate links
        links = soup.find_all('link', rel='alternate')
        for link in links:
            link_type = link.get('type', '')
            if 'application/rss+xml' in link_type or 'application/atom+xml' in link_type:
                href = link.get('href')
                if href:
                    return urljoin(url, href)
        
        return url
    except Exception:
        return url

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        print(getRSSLink(sys.argv[1]))
