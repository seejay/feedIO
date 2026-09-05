"""Portable subscription exchange; profile snapshots include history and votes."""
from pathlib import Path
from xml.etree import ElementTree as ET
from urllib.parse import urlsplit
import os
import tempfile
from . import models as m


def http_url(value):
    parts = urlsplit(value.strip())
    if parts.scheme not in ('http', 'https') or not parts.hostname or parts.username or parts.password:
        raise ValueError('Use an HTTP(S) URL without embedded credentials')
    return value.strip()


def export_opml(destination):
    root = ET.Element('opml', version='2.0')
    ET.SubElement(ET.SubElement(root, 'head'), 'title').text = 'feedIO subscriptions'
    body = ET.SubElement(root, 'body')
    for feed in m.session.query(m.Feed).order_by(m.Feed.id):
        ET.SubElement(body, 'outline', text=feed.title, title=feed.title, type='rss', xmlUrl=feed.url)
    destination = Path(destination)
    descriptor, temporary = tempfile.mkstemp(dir=destination.parent, suffix='.opml')
    try:
        with os.fdopen(descriptor, 'wb') as file:
            file.write(ET.tostring(root, encoding='utf-8', xml_declaration=True))
        os.replace(temporary, destination)
    finally:
        Path(temporary).unlink(missing_ok=True)


def import_opml(source):
    with open(source, 'rb') as file:
        data = file.read(5_000_001)
    if len(data) > 5_000_000 or b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
        raise ValueError('OPML is too large or contains unsupported declarations')
    root = ET.fromstring(data)
    if root.tag != 'opml':
        raise ValueError('Not an OPML document')
    entries = [(http_url(node.attrib['xmlUrl']), node.attrib.get('title') or node.attrib.get('text'))
               for node in root.iter('outline') if 'xmlUrl' in node.attrib]
    added = 0
    try:
        for url, title in entries:
            if m.session.query(m.Feed).filter_by(url=url).first():
                continue
            feed = m.Feed(url=url, title=title or url)
            m.session.add(feed)
            feed.topics.extend(m.session.query(m.Topic).all())
            added += 1
        m.session.commit()
    except Exception:
        m.session.rollback()
        raise
    return added
