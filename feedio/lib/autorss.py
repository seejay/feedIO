"""Feed discovery resolves links against the final document URL."""
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from ..network import retrieve
from ..portability import http_url


def discover(response):
    soup = BeautifulSoup(response.content, 'html.parser')
    for link in soup.find_all('link', rel='alternate'):
        if link.get('type', '').lower() in ('application/rss+xml', 'application/atom+xml'):
            href = link.get('href')
            if href:
                return http_url(urljoin(response.url, href))
    return response.url


def getRSSLink(url):
    return discover(retrieve(url))
