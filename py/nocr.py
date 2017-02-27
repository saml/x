import sqlite3
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='nocr.db', help='path to database [%(default)s]')
    parser.add_argument('--out', default='nocr.md', help='output file path [%(default)s]')
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    c = conn.cursor()
    current_book = None
    with open(args.out, 'w') as f:
        for book, chapter, text in c.execute('SELECT book,chapter,text FROM chapters'):
            if current_book != book:
                f.write('# {}\n\n'.format(book))
                current_book = book
            f.write('## {}\n\n'.format(chapter))
            f.write(text)
            f.write('\n\n\n')
            