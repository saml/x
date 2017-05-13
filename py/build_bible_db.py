# niv2011.sqlite3 https://github.com/liudongmiao/bibledata/blob/master/bibledata-en-niv2011.zip
# niv.db https://github.com/anderson916/FreeWorship/blob/master/database/niv.db

import sqlite3
import argparse
import re
import decimal

verse_re = re.compile(r'\d+:(\d+)')
books = [(ko.replace(' ', ''), en.strip()) for ko,en in (x.split('-', 2) for x in '''
창세기- Genesis
출애굽기 - Exodus
레위기 - Leviticus
민수기 - Numbers
신명기 - Deuteronomy
여호수아 - Joshua
사사기 - Judges
룻기 - Ruth
사무엘상 - 1 Samuel
사무엘하 - 2 Samuel
열왕기상- 1 Kings
열왕기하- 2 Kings
역대상- 1 Chronicles
역대하- 2 Chronicles
에스라 - Ezra
느헤미야 - Nehemiah
에스더 - Esther
욥기 - Job
시편 - Psalm
잠언 - Proverbs
전도서 - Ecclesiastes
아가 - Song of Songs
이사야 - Isaiah
예레미야 - Jeremiah
예레미야애가 - Lamentations
에스겔 - Ezekiel
다니엘 - Daniel
호세아 - Hosea
요엘 - Joel
아모스 - Amos
오바댜 - Obadiah
요나 - Jonah
미가 - Micah
나훔 - Nahum
하박국 - Habakkuk
스바냐 - Zephaniah
학개 - Haggai
스가랴 - Zechariah
말라기 - Malachi
마태복음- Matthew
마가복음- Mark
누가복음- Luke
요한복음- John
사도행전- Acts
로마서 -Romans
고린도전서 - 1 Corinthians
고린도후서 - 2 Corinthians
갈라디아서 - Galatians
에베소서 - Ephesians
빌립보서- Philippians
골로새서- Colossians
데살로니가전서 - 1 Thessalonians
데살로니가후서- 2 Thessalonians
디모데전서 - 1 Timothy
디모데후서- 2 Timothy
디도서- Titus
빌레몬서- Philemon
히브리서 - Hebrews
야고보서- James
베드로전서- 1 Peter
베드로후서- 2 Peter
요한일서- 1 John
요한이서 - 2 John
요한삼서- 3 John
유다서- Jude
요한계시록- Revelation
'''.splitlines() if x)]

def create_db(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE books (ko TEXT UNIQUE, en TEXT UNIQUE)''')
    c.executemany('''INSERT INTO books VALUES (?, ?)''', books)
    c.execute('''CREATE TABLE verses (
        book_id INT, chapter INT, verse INT, ko TEXT, en TEXT,
        FOREIGN KEY (book_id) REFERENCES books(rowid))''')
    conn.commit()

def get_kor_iter(kor, book_id_ko):
    for kor_book,_ in books:
        for book,chapter,chapter_text in kor.execute('SELECT book,chapter,text FROM chapters WHERE book = ? ORDER BY chapter ASC', [kor_book]):
            book_id = book_id_ko[book]
            verse_and_text = (x for x in verse_re.split(chapter_text) if x)
            for verse in verse_and_text:
                text = next(verse_and_text).strip()
                yield book_id,chapter,int(verse),text

def _get_niv_iter(niv, book_id_en, book_key_name, book_name_key):
    decimal.getcontext().prec = 3
    for _,en_book in books:
        for book_key,chapter_verse,text in niv.execute('SELECT book, verse, unformatted FROM verses WHERE book = ?', [book_name_key[en_book]]):
            book = book_key_name[book_key]
            book_id = book_id_en[book]
            chapter = int(chapter_verse)
            verse = int((decimal.Decimal(str(chapter_verse)) - chapter) * 1000)
            print(chapter_verse, chapter, verse)
            yield book_id,chapter,verse,text

def get_niv_iter(niv):
    modify_niv(niv)
    decimal.getcontext().prec = 3
    for book_id,chapter,verse,text in niv.execute('SELECT bookid,chapterid,verseid,content from verse order by bookid,chapterid,verseid'):
        yield book_id,chapter,verse,text
    

def insert_na(niv, bookid, chapterid, verseid, content='(N/A)'):
    if next(niv.execute('SELECT * from verse where bookid = ? and chapterid = ? and verseid = ?', [bookid, chapterid, verseid]), None) is None:
        niv.execute('INSERT INTO verse (bookid, chapterid, verseid, content) VALUES (?,?,?,?)', [bookid, chapterid, verseid, content])
    
def modify_niv(niv):
    # matthew
    insert_na(niv, 40, 17, 21)
    insert_na(niv, 40, 18, 11)
    insert_na(niv, 40, 23, 14)

    # mark
    insert_na(niv, 41, 7, 16)
    insert_na(niv, 41, 9, 44)
    insert_na(niv, 41, 9, 46)
    insert_na(niv, 41, 11, 26)
    insert_na(niv, 41, 15, 28)

    # luke
    insert_na(niv, 42, 17, 36)
    insert_na(niv, 42, 23, 17)

    # john
    insert_na(niv, 43, 5, 4)

    # acts
    insert_na(niv, 44, 8, 37)
    insert_na(niv, 44, 15, 34)
    insert_na(niv, 44, 24, 7)
    insert_na(niv, 44, 28, 29)

    # romans
    insert_na(niv, 45, 16, 24)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--nocr', default='nocr.db')
    parser.add_argument('--niv', default='niv.db')
    # parser.add_argument('--niv', default='niv2011.sqlite3')
    # parser.add_argument('--nivtxt', default='niv.db')
    parser.add_argument('--output', default='bible_ko_niv.sqlite')
    args = parser.parse_args()

    niv_conn = sqlite3.connect(args.niv)
    kor_conn = sqlite3.connect(args.nocr)
    out_conn = sqlite3.connect(args.output)
    
    create_db(out_conn)
    out = out_conn.cursor()
    niv = niv_conn.cursor()
    kor = kor_conn.cursor()
    book_id_map = {rowid:(ko,en) for rowid,ko,en in out.execute('SELECT rowid,ko,en FROM books')}
    book_id_ko = {ko:rowid for rowid,(ko,_) in book_id_map.items()}
    book_id_en = {en:rowid for rowid,(_,en) in book_id_map.items()}
    # book_name_key_en = {book:book_key for book_key,book in niv.execute('SELECT osis,human FROM books')}
    # book_key_name_en = {book_key:book for book_key,book in niv.execute('SELECT osis,human FROM books')}
    niv_iter = get_niv_iter(niv)
    kor_iter = get_kor_iter(kor, book_id_ko)
    for niv_row, kor_row in zip(niv_iter, kor_iter):
        niv_book_id,niv_chapter,niv_verse,niv_text = niv_row
        kor_book_id,kor_chapter,kor_verse,kor_text = kor_row
        if niv_book_id != kor_book_id or niv_chapter != kor_chapter or niv_verse != kor_verse:
            print('{} {} {}:{} / {} {}:{} {} {}'.format(book_id_map[niv_book_id], niv_book_id, niv_chapter, niv_verse, kor_book_id, kor_chapter, kor_verse, niv_text, kor_text))
            break
        out.execute('INSERT INTO verses (book_id, chapter, verse, ko, en) VALUES (?, ?, ?, ?, ?)', [niv_book_id, niv_chapter, niv_verse, kor_text, niv_text])
    out_conn.commit()
        
    #insert_kor(kor, out)
    #update_niv(niv, out)
