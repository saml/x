import sqlite3
import argparse
import zipfile
from collections import namedtuple
import uuid
import datetime

Item = namedtuple('Item', ['name', 'file'])

class Book:
    def __init__(self, number, title=None):
        self.title = title
        self.number = number
        self.nav_page = None
        self.chapters = []

class TheBook:
    def __init__(self, title, uid=None):
        self.title = title
        self.uid = uid if uid is not None else uuid.uuid1().urn
        self.books = []
        self.chapters = []

CONTAINER_XML = '''<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
   <rootfiles>
      <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
   </rootfiles>
</container>
'''

STYLESHEET = '''
@font-face { font-family: "hangul"; src: url("NanumBarunGothic.otf"); }
body { margin: 5%; font-size: medium; font-family: "hangul"; }
p { line-height: 1.4; }
ol.toc li { list-style-type: none; padding: 0.5em; }
'''


def as_chapter_xhtml(title, body):
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="ko" xml:lang="ko">
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
        '<item id="a{}" href="{}" media-type="application/xhtml+xml" />'.format(x.replace('.', '_'), x) 
        for x in filenames)
    spine = '\n'.join('<itemref idref="a{}" />'.format(x.replace('.', '_')) for x in filenames)

    return '''<?xml version="1.0" encoding="UTF-8"?>
<package version="2.0" xmlns="http://www.idpf.org/2007/opf" unique-identifier="epub-id-1">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:identifier id="epub-id-1">{uid}</dc:identifier>
    <dc:date id="epub-date-1">{today}</dc:date>
    <dc:language>{language}</dc:language>
    <dc:title>The Bible (Woorimal, Korean)</dc:title>
  </metadata>
  <manifest>
    <item id="NanumBarunGothic" href="NanumBarunGothic.otf" media-type="application/vnd.ms-opentype" />
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml" />
    <item id="style" href="stylesheet.css" media-type="text/css" />
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" />
{manifest}
  </manifest>
  <spine toc="ncx">
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

    all_books = []
    current_book = Book(len(all_books))

    uid = uuid.uuid1().urn
    with zipfile.ZipFile(args.out, 'w') as f:
        f.writestr('mimetype', 'application/epub+zip')
        for book, chapter, text in c.execute('SELECT book,chapter,text FROM chapters'):
            if current_book.title is None:
                current_book.title = book
            if current_book.title != book:
                book_nav = '{}.xhtml'.format(current_book.number)
                current_book.nav_page = Item(current_book.title, book_nav)
                all_books.append(current_book)
                f.writestr(book_nav, as_book_toc(current_book.title, current_book.chapters))
                current_book = Book(len(all_books), book)
            title = '{} - {}'.format(book, chapter)
            body = '<p>{}</p>'.format(text)
            xhtml = as_chapter_xhtml(title, body)
            xhtml_name = '{}_{}.xhtml'.format(current_book.number, chapter)
            current_book.chapters.append(Item(chapter, xhtml_name))
            f.writestr(xhtml_name, xhtml)

        book_nav = '{}.xhtml'.format(current_book.number)
        current_book.nav_page = Item(current_book.title, book_nav)
        all_books.append(current_book)
        f.writestr(book_nav, as_book_toc(current_book.title, current_book.chapters))
            
        f.write('NanumBarunGothic.otf')
        f.writestr('META-INF/container.xml', CONTAINER_XML)
        nav_pages = [book.nav_page for book in all_books]
        f.writestr('toc.ncx', as_toc_ncx(uid, args.title, nav_pages))
        all_filenames = []
        for book in all_books:
            all_filenames.append(book.nav_page.file)
            all_filenames.extend(x.file for x in book.chapters)
        f.writestr('content.opf', as_content_opf(uid, args.title, all_filenames))
        f.writestr('nav.xhtml', as_book_toc(args.title, nav_pages))
        f.writestr('stylesheet.css', STYLESHEET)
