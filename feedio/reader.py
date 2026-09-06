"""Offline article renderer: no scripts, remote requests, or file navigation."""
import html
from bs4 import BeautifulSoup
from PyQt6.QtCore import QUrl, QCoreApplication
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWebEngineCore import (QWebEnginePage, QWebEngineProfile,
                                  QWebEngineSettings, QWebEngineUrlRequestInterceptor)


class OfflineRequests(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        if info.requestUrl().scheme() not in ('data', 'about', 'qrc'):
            info.block(True)


class ReaderPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, kind, main_frame):
        if kind == self.NavigationType.NavigationTypeLinkClicked:
            if url.scheme() in ('https', 'http'):
                QDesktopServices.openUrl(url)
            return False
        return url.scheme() in ('data', 'about', 'qrc')


def configure(view):
    profile = QWebEngineProfile(QCoreApplication.instance())
    interceptor = OfflineRequests(profile)
    profile.setUrlRequestInterceptor(interceptor)
    page = ReaderPage(profile, view)
    view.destroyed.connect(profile.deleteLater)
    settings = page.settings()
    settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, False)
    settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, False)
    settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)
    profile.downloadRequested.connect(lambda download: download.cancel())
    view.setPage(page)
    # Keep Python wrappers alive for Qt virtual callbacks.
    view._reader_objects = (profile, interceptor, page)


def close(view):
    if getattr(view, '_reader_objects', None):
        view.stop()


def article_html(title, body, feed_title=''):
    soup = BeautifulSoup(body or '', 'html.parser')
    for tag in soup(['script', 'iframe', 'object', 'embed', 'form', 'input', 'link', 'meta', 'style']):
        tag.decompose()
    for tag in soup.find_all(True):
        for attribute in list(tag.attrs):
            if attribute.lower().startswith('on') or attribute.lower() in ('style', 'srcset'):
                del tag[attribute]
        for attribute in ('href', 'src'):
            if attribute in tag.attrs:
                url = QUrl(str(tag[attribute]))
                if url.scheme() not in ('https', 'http'):
                    del tag[attribute]
    return ('<!doctype html><html><head><meta charset="utf-8">'
            '<style>body{font:18px sans-serif;line-height:1.6;max-width:850px;margin:32px auto;padding:0 24px}'
            'img{max-width:100%}a{color:#356ac3}pre{white-space:pre-wrap}</style></head><body>'
            f'<h1>{html.escape(title)}</h1><p>{html.escape(feed_title)}</p>{soup}</body></html>')
