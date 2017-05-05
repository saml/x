import sqlite3

if __name__ == '__main__':
    conn = sqlite3.connect('bible_ko_niv.sqlite')
    c = conn.cursor()
    book_names = {rowid: (ko_name, en_name) for rowid,ko_name,en_name in c.execute('SELECT rowid,ko,en FROM books')}
    tree = []
    bible = {
        'ko': {ko:book_id-1 for book_id,(ko,_) in book_names.items()},
        'en': {en:book_id-1 for book_id,(_,en) in book_names.items()},
        'data': tree,
    }
    for book_id, chapter, verse, ko, en in c.execute('SELECT book_id, chapter, verse, ko, en FROM verses'):
        if len(tree) < book_id: # book_id is not in the tree. insert it
            tree.append([])
        chapters = tree[book_id-1]
        if len(chapters) < chapter:
            chapters.append([])
        verses = chapters[chapter-1]
        verses.append([ko, en])
    
    import json
    import sys
    json.dump(bible, sys.stdout)