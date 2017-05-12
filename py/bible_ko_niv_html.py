import sqlite3
import re

newline = re.compile(r'\n+')

if __name__ == '__main__':
    conn = sqlite3.connect('bible_ko_niv.sqlite')
    c = conn.cursor()
    books = {rowid: (ko_name, en_name) for rowid,ko_name,en_name in c.execute('SELECT rowid,ko,en FROM books')}
    print('''<!doctype html>
<meta charset="utf-8">
<title>b</title>    
''')
    for book_id, chapter, verse, ko, en in c.execute('SELECT book_id, chapter, verse, ko, en FROM verses'):
        ko_name, en_name = books[book_id]
        if verse == 1:
            print('<p>[{} {}] / [{} {}]</p>'.format(ko_name, chapter, en_name, chapter))
        print('<p>{} {}<br>{} {}</p>'.format(verse, ko, verse, en))