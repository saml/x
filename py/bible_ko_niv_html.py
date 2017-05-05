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
        print(u'<p>{} / {} {}:{}<br>'.format(ko_name, en_name, chapter, verse))
        print(newline.sub('<br>', ko))
        print(newline.sub('<br>', en))
        print(u'</p>')