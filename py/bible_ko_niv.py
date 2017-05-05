import sqlite3

if __name__ == '__main__':
    conn = sqlite3.connect('bible_ko_niv.sqlite')
    c = conn.cursor()
    books = {rowid: (ko_name, en_name) for rowid,ko_name,en_name in c.execute('SELECT rowid,ko,en FROM books')}
    for book_id, chapter, verse, ko, en in c.execute('SELECT book_id, chapter, verse, ko, en FROM verses'):
        ko_name, en_name = books[book_id]
        print(u'{} / {} {}:{}'.format(ko_name, en_name, chapter, verse))
        print(ko)
        print(en)
        print(u'\u2029')