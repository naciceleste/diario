#!/usr/bin/env python3
"""Recheck configured endpoints with real HTTP GET + RSS/Atom parsing."""
import concurrent.futures as cf
from datetime import datetime, timezone
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from build_diario import fetch, local_tag, atomic_json

ROOT = Path(__file__).resolve().parents[1]

def verify(source):
    source = dict(source)
    report = dict(outlet=source['outlet'], rss=source['rss'])
    try:
        raw, final, content_type = fetch(source['rss'])
        root = ET.fromstring(raw)
        entries = [e for e in root.iter() if local_tag(e) in ('item', 'entry')]
        if local_tag(root) not in ('rss', 'RDF', 'feed') or not entries:
            raise ValueError('No es un RSS/Atom con entradas')
        source['verified'] = True
        report.update(status=200, entries=len(entries), final_url=final, content_type=content_type)
    except Exception as exc:
        source['verified'] = False
        report['error'] = str(exc)
    report['verified'] = source['verified']
    return source, report

if __name__ == '__main__':
    sources = json.loads((ROOT/'sources.json').read_text())
    with cf.ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(verify, sources))
    atomic_json(ROOT/'sources.json', [a for a, _ in results])
    atomic_json(ROOT/'data/feed-verification.json', dict(checked_at=datetime.now(timezone.utc).isoformat(), results=[b for _, b in results]))
    for source, report in results:
        print(source['region'], source['outlet'], 'independiente='+str(source['independent']), 'verificado='+str(source['verified']), report.get('error', 'HTTP 200 / '+str(report.get('entries'))+' entradas'))
