# niv2011.sqlite3 https://github.com/liudongmiao/bibledata/blob/master/bibledata-en-niv2011.zip

import sqlite3
import argparse
import re

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

def insert_kor(kor_conn, out_conn):
    # CREATE TABLE chapters(book TEXT, chapter INT, text TEXT);
    kor = kor_conn.cursor()
    out = out_conn.cursor()
    for book,chapter,chapter_text in kor.execute('''SELECT book,chapter,text FROM chapters'''):
        print(book)
        out.execute('SELECT rowid FROM books WHERE ko = ?', [book])
        book_id = out.fetchone()[0]
        verse_and_text = (x for x in verse_re.split(chapter_text) if x)
        for verse in verse_and_text:
            text = next(verse_and_text).strip()
            print([book_id, chapter, verse, text])
            out.execute('INSERT INTO verses (book_id, chapter, verse, ko) VALUES (?, ?, ?, ?)', [book_id, chapter, verse, text])
    out_conn.commit()

def update_niv(niv_conn, out_conn):
    # CREATE TABLE verses (id INTEGER PRIMARY KEY, book CHAR(7), verse REAL, unformatted TEXT);
    # CREATE TABLE "books" (number INTEGER PRIMARY KEY, osis TEXT NOT NULL, human TEXT NOT NULL, chapters INTEGER NOT NULL);
    niv =  niv_conn.cursor()
    out = out_conn.cursor()

    book_names = {book_key:book for book_key,book in niv.execute('SELECT osis,human FROM books')}
    for book_key,chapter_verse,text in niv.execute('SELECT book, verse, unformatted FROM verses'):
        book = book_names[book_key]
        print(book)
        out.execute('SELECT rowid FROM books WHERE en = ?', [book])
        book_id = out.fetchone()[0]
        chapter = int(chapter_verse)
        verse = int((chapter_verse - chapter) * 1000)
        print([book_id, chapter, verse, text])
        out.execute('UPDATE verses SET en = ? WHERE book_id = ? AND chapter = ? AND verse = ?', [text, book_id, chapter, verse])
    out_conn.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--nocr', default='nocr.db')
    parser.add_argument('--niv', default='niv2011.sqlite3')
    parser.add_argument('--output', default='bible.sqlite')
    args = parser.parse_args()

    niv = sqlite3.connect(args.niv)
    kor = sqlite3.connect(args.nocr)
    out = sqlite3.connect(args.output)
    #create_db(out)
    #insert_kor(kor, out)
    update_niv(niv, out)
