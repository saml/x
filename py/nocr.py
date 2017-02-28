import sqlite3
import argparse
import zipfile
from collections import namedtuple
import uuid
import datetime

Item = namedtuple('Item', ['name', 'file'])

CONTAINER_XML = '''<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
   <rootfiles>
      <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
   </rootfiles>
</container>
'''

STYLESHEET = '''
@font-face { font-family: "hangul"; src: url(res:///system/media/sdcard/fonts/NanumGothicBold.ttf); }
body { margin: 5%; text-align: justify; font-size: medium; font-family: "hangul"; }
code { font-family: monospace; }
h1 { text-align: left; }
h2 { text-align: left; }
h3 { text-align: left; }
h4 { text-align: left; }
h5 { text-align: left; }
h6 { text-align: left; }
h1.title { }
h2.author { }
h3.date { }
ol.toc { padding: 0; margin-left: 1em; }
ol.toc li { list-style-type: none; margin: 0; padding: 0; }
a.footnoteRef { vertical-align: super; }
em, em em em, em em em em em { font-style: italic;}
em em, em em em em { font-style: normal; }
'''


def as_chapter_xhtml(title, body):
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ko">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta http-equiv="Content-Style-Type" content="text/css" />
  <title>{title}</title>
  <link rel="stylesheet" type="text/css" href="stylesheet.css" />
</head>
<body>
{body}
</body>
</html>
'''.format(title=title, body=body)

def as_book_toc(book_name, chapter_files):
    chapter_nav = '\n'.join(
        '<li><a href="{link}">{name}</a></li>'.format(link=chapter.file, name=chapter.name)
        for chapter in chapter_files)
    body = '''<h1>{}</h1>
<ol class="toc">
{}
</ol>'''.format(book_name, chapter_nav)
    return as_chapter_xhtml(book_name, body)

def as_content_opf(uid, title, filenames, language='ko-KR'):
    manifest = '\n'.join(
        '<item id="{}" href="{}" media-type="application/xhtml+xml" />'.format(x.replace('.', '_'), x) 
        for x in filenames)
    spine = '\n'.join('<itemref idref="{}" />'.format(x.replace('.', '_')) for x in filenames)

    return '''<?xml version="1.0" encoding="UTF-8"?>
<package version="2.0" xmlns="http://www.idpf.org/2007/opf" unique-identifier="epub-id-1">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:identifier id="epub-id-1">{uid}</dc:identifier>
    <dc:date id="epub-date-1">{today}</dc:date>
    <dc:language>{language}</dc:language>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml" />
    <item id="style" href="stylesheet.css" media-type="text/css" />
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" />
{manifest}
  </manifest>
  <spine>
{spine}
  </spine>
  <guide>
    <reference type="toc" title="{title}" href="nav.xhtml" />
  </guide>
</package>
'''.format(uid=uid, title=title, today=datetime.datetime.now().isoformat(), language=language, manifest=manifest, spine=spine)
    


def as_toc_ncx(uid, title, items):
    body = '\n'.join('''<navPoint id="navPoint-{id}">
    <navLabel><text>{title}</text></navLabel>
    <content src="{link}" />
</navPoint>'''.format(id=i, title=x.name, link=x.file) for i, x in enumerate(items))

    return '''<?xml version="1.0" encoding="UTF-8"?>
<ncx version="2005-1" xmlns="http://www.daisy.org/z3986/2005/ncx/">
  <head>
    <meta name="dtb:uid" content="{uid}" />
    <meta name="dtb:depth" content="1" />
    <meta name="dtb:totalPageCount" content="0" />
    <meta name="dtb:maxPageNumber" content="0" />
  </head>
  <docTitle><text>{title}</text></docTitle>
  <navMap>
{body}
  </navMap>
</ncx>
  '''.format(uid=uid, title=title, body=body)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--title', default='The Bible', help='title of the book [%(default)s]')
    parser.add_argument('--db', default='nocr.db', help='path to database [%(default)s]')
    parser.add_argument('--out', default='nocr.epub', help='output file path [%(default)s]')
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    c = conn.cursor()

    title_page = Item(args.title, 'title_page.xhtml')
    current_book = None
    chapter_files = []
    book_files = []
    all_filenames = [title_page.file]
    book_index = 0
    uid = uuid.uuid1().urn
    thebook = {}
    with zipfile.ZipFile(args.out, 'w') as f:
        for book, chapter, text in c.execute('SELECT book,chapter,text FROM chapters'):
            title = '{} - {}'.format(book, chapter)
            body = '<p>{}</p>'.format(text)
            xhtml = as_chapter_xhtml(title, body)
            xhtml_name = '{}_{}.xhtml'.format(book_index, chapter)
            chapter_files.append(Item(chapter, xhtml_name))
            all_filenames.append(xhtml_name)
            f.writestr(xhtml_name, xhtml)
            if current_book != book:
                book_nav = '{}.xhtml'.format(book_index)
                all_filenames.append(book_nav)
                book_files.append(Item(book, book_nav))
                f.writestr(book_nav, as_book_toc(book, chapter_files))
                book_index += 1
                current_book = book
                chapter_files = []
        f.writestr(title_page.file, as_chapter_xhtml(args.title, '<h1>{}</h1>'.format(args.title)))
        f.writestr('mimetype', 'application/epub+zip')
        f.writestr('META-INF/container.xml', CONTAINER_XML)
        f.writestr('toc.ncx', as_toc_ncx(uid, args.title, [title_page] + book_files))
        f.writestr('content.opf', as_content_opf(uid, args.title, all_filenames))
        f.writestr('nav.xhtml', as_book_toc(args.title, book_files))
        f.writestr('stylesheet.css', STYLESHEET)
            