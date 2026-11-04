import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import build_diario as b

NOW = datetime(2026,11,4,3,tzinfo=timezone.utc)
SOURCE = dict(outlet='Prueba',region='Argentina',topics=['Política','Economía'],independent=True,rss='https://example.org/feed',verified=True)

def item(title, outlet='A', independent=True, section='Política', index=0, region='Argentina'):
    return dict(title=title,url=f'https://example.org/{outlet}/{section}/{index}',outlet=outlet,region=region,independent=independent,section=section,published_at=NOW.isoformat(),excerpt='',image_src=None)

def only_entry(xml):
    root = ET.fromstring(xml)
    return next(e for e in root.iter() if b.local_tag(e) in ('item','entry'))

class BuildTests(unittest.TestCase):
    def test_dates_rss_atom_and_window(self):
        xml = b'''<rss><channel><item><title>El gobierno anuncia elecciones</title><link>https://example.org/hoy</link><pubDate>Tue, 03 Nov 2026 22:00:00 -0300</pubDate></item><item><title>El gobierno viejo</title><link>https://example.org/viejo</link><pubDate>Sun, 01 Nov 2026 12:00:00 GMT</pubDate></item><item><title>El gobierno futuro</title><link>https://example.org/futuro</link><pubDate>Fri, 06 Nov 2026 12:00:00 GMT</pubDate></item><item><title>Sin fecha</title><link>https://example.org/sin-fecha</link></item></channel></rss>'''
        articles, _ = b.parse_feed(xml,SOURCE,NOW)
        self.assertEqual(len(articles),1)
        atom=b'''<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>El gobierno anuncia elecciones</title><link rel="alternate" href="https://example.org/atom"/><published>2026-11-03T23:00:00Z</published></entry></feed>'''
        self.assertEqual(b.parse_feed(atom,SOURCE,NOW)[0][0]['url'],'https://example.org/atom')
        self.assertEqual(b.parse_feed(b'<rss><channel><language>pt-BR</language></channel></rss>',SOURCE,NOW)[0],[])

    def test_classification_avoids_ambiguous_keywords(self):
        self.assertNotEqual(b.classify('Ministerio de Defensa Nacional recibió informe', '', '', ['Política','Economía']), 'Fútbol')
        self.assertIsNone(b.classify('Equipar la cocina con poco presupuesto', '', '', ['Política','Economía']))
        self.assertIsNone(b.classify('Maestros lijaron bancos', '', '', ['Política','Economía']))
        self.assertEqual(b.classify('El Banco Central baja las tasas', '', '', ['Política','Economía']), 'Economía')
        self.assertNotEqual(b.classify('La plantilla del Hospital de Barcelona en huelga', '', '', ['Política','Economía']), 'Fútbol')
        self.assertEqual(b.classify('Liga Uruguaya: ganaron Larrañaga y Peñarol', '', 'Básquetbol', ['Política','Economía','Fútbol']), 'Básquetbol')
        self.assertEqual(b.classify('Alcaraz gana en París', '', '', ['Fútbol','Tenis']), 'Tenis')
        self.assertEqual(b.classify('OpenAI presenta un nuevo modelo', '', '', ['Tech','IA']), 'IA')
        self.assertEqual(b.classify('Nueva ruta por Navarra', '', '', ['Viajes']), 'Viajes')

    def test_dedupe_prefers_independent_and_keeps_coverage(self):
        articles = [item('El dólar alcanzó un nuevo récord',independent=False), item('El dolar alcanzo un nuevo record',outlet='B'), item('La inflación desciende durante octubre',outlet='C')]
        result = b.dedupe_rank(articles,NOW)
        self.assertEqual(len(result),2)
        duplicate = next(a for a in result if a['outlet']=='B')
        self.assertEqual(duplicate['coverage'],['A','B'])
        self.assertLessEqual(len(b.shorten('Una noticia muy larga '*30)),110)
        self.assertFalse(b.similar('Alcaraz gana ante Sinner en París','Alcaraz pierde ante Sinner en París'))

    def test_exact_archive_and_index(self):
        edition = dict(date='2026-11-02',generated_at=NOW.isoformat(),lead={'title':'Antes'},counts={'total':30})
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            b.save_edition(edition,root)
            before=(root/'diario.json').read_bytes()
            updated=copy.deepcopy(edition);updated['date']='2026-11-03';updated['lead']['title']='Después'
            b.save_edition(updated,root)
            self.assertEqual((root/'archivo/2026-11-02.json').read_bytes(),before)
            self.assertEqual(json.loads((root/'archivo/index.json').read_text())[0]['date'],'2026-11-02')
            self.assertEqual(json.loads((root/'diario.json').read_text())['lead']['title'],'Después')

    def test_failed_build_preserves_previous_edition(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'data').mkdir()
            (root/'sources.json').write_text(json.dumps([SOURCE]))
            previous=b'{"previous":"unchanged"}'
            (root/'data/diario.json').write_bytes(previous)
            with patch.object(b,'ROOT',root), patch.object(b,'collect',return_value=([],{'error':'timeout'})):
                self.assertEqual(b.build(),1)
            self.assertEqual((root/'data/diario.json').read_bytes(),previous)
            self.assertFalse((root/'data/archivo').exists())

    def test_feed_image_extraction_order(self):
        media = '<rss xmlns:media="http://search.yahoo.com/mrss/"><channel><item><title>t</title>'\
                '<media:thumbnail url="img/thumb.jpg"/>'\
                '<media:content medium="image" url="https://cdn.example.org/big.jpg"/>'\
                '</item></channel></rss>'
        self.assertEqual(b.feed_image(only_entry(media), 'https://example.org/n/'), 'https://example.org/n/img/thumb.jpg')
        content = '<rss xmlns:media="http://search.yahoo.com/mrss/"><channel><item><title>t</title>'\
                  '<media:content medium="video" url="https://cdn.example.org/clip.mp4"/>'\
                  '<media:content type="image/jpeg" url="https://cdn.example.org/photo.jpg"/>'\
                  '</item></channel></rss>'
        self.assertEqual(b.feed_image(only_entry(content), 'https://example.org/n/'), 'https://cdn.example.org/photo.jpg')
        enclosure = '<rss><channel><item><title>t</title><enclosure url="https://cdn.example.org/e.png" type="image/png"/></item></channel></rss>'
        self.assertEqual(b.feed_image(only_entry(enclosure), 'https://example.org/n/'), 'https://cdn.example.org/e.png')
        html = '<rss><channel><item><title>t</title><description>&lt;p&gt;Hola &lt;img src="/media/foto.webp"&gt;&lt;/p&gt;</description></item></channel></rss>'
        self.assertEqual(b.feed_image(only_entry(html), 'https://example.org/n/'), 'https://example.org/media/foto.webp')
        atom = '<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>t</title><content type="html">sin imagen</content></entry></feed>'
        self.assertIsNone(b.feed_image(only_entry(atom), 'https://example.org/n/'))

    def test_feed_image_populated_by_parse(self):
        xml = '<rss xmlns:media="http://search.yahoo.com/mrss/"><channel><item>'\
              '<title>El gobierno anuncia elecciones</title><link>https://example.org/hoy</link>'\
              '<pubDate>Tue, 03 Nov 2026 22:00:00 -0300</pubDate>'\
              '<media:thumbnail url="https://cdn.example.org/x.jpg"/></item></channel></rss>'
        articles, _ = b.parse_feed(xml.encode(), SOURCE, NOW)
        self.assertEqual(articles[0]['image_src'], 'https://cdn.example.org/x.jpg')

    def test_select_caps_region_and_section(self):
        import random
        rng = random.Random(1234)
        vocab = [a + v + c + v2 for a in 'bcdfgp' for v in 'aeiou' for c in 'lmnrst' for v2 in 'aeiou']
        articles = []
        n = 0
        # Each title is five distinct words so dedupe keeps every story separate;
        # both regions then supply far more than their cap across every section, so
        # the per-region caps (not the section pools) decide the final balance.
        def title(k):
            return ' '.join(rng.sample(vocab, 5))
        for section in b.SECTIONS:
            for region in ('Argentina', 'España'):
                for i in range(6):
                    n += 1
                    articles.append(item(title(n), outlet=f'{region[:2]}{n}',
                                         independent=(i % 2 == 0), section=section, index=n, region=region))
        for region in ('Uruguay', 'Costa Rica', 'Mundo'):
            for i in range(2):
                n += 1
                articles.append(item(title(n), outlet=f'{region[:2]}{n}',
                                     independent=True, section='Política', index=n, region=region))
        ranked = b.dedupe_rank(articles, NOW)
        with patch.object(b, 'verify_article', lambda it: (dict(it, url_verified=True, url_status=200), None)):
            lead, featured, sections, _ = b.select(ranked)
        edition = [lead, *featured, *(a for g in sections.values() for a in g)]
        counts = {r: sum(a['region'] == r for a in edition) for r in b.REGIONS}
        # España offered 24 verifiable stories but is held at or under its cap.
        self.assertLessEqual(counts['España'], b.REGION_CAPS['España'])
        self.assertLess(counts['España'], 24)
        self.assertLessEqual(counts['Argentina'], b.REGION_CAPS['Argentina'])
        self.assertGreater(counts['Argentina'], counts['España'])  # Argentina keeps a strong presence
        for topic, group in sections.items():
            for region in b.REGIONS:
                self.assertLessEqual(sum(a['region'] == region for a in group), b.SECTION_REGION_CAP, f'{topic}/{region}')
        self.assertEqual(len({a['id'] for a in edition}), len(edition))  # no duplicates across the edition

    def test_optional_summary_falls_back(self):
        articles=[item('Titular '+str(n)) for n in range(4)]
        with patch.dict('os.environ',{'DIARIO_RESUMEN':'1'}),patch.object(b.subprocess,'run',side_effect=FileNotFoundError):
            lines,method=b.summary(articles)
        self.assertEqual((len(lines),method),(4,'extractivo'))

if __name__=='__main__': unittest.main()
