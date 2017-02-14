import csv
import argparse

def as_calendar_row(row):
    return row[:7]

def is_empty(row):
    return len([x for x in as_calendar_row(row) if x]) == 0

def as_date_row(row):
    result = []
    for cell in row:
        try:
            day_of_month = int(cell, 10)
        except:
            day_of_month = 0
        result.append(day_of_month)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('csv')
    args = parser.parse_args()

    with open(args.csv, 'r') as f:
        r = csv.reader(f)
        year_row = next(r)
        year = int(year_row[0], 10)
        comments = year_row[-1]
        month = int(next(r)[0])
        days = next(r)[:7]
        for row in r:
            if is_empty(row):
                continue
            day_of_month = as_date_row(row)
            names_row = as_calendar_row(next(r))
            for i, names in enumerate(names_row):
                if names:
                    print('{} {}-{:02d}-{:02d} {}'.format(days[i], year, month, day_of_month[i], names.replace('\n', ' ')))
        print(comments)
