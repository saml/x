import sys
import json

def main():
    for line in sys.stdin:
        line = line.strip()
        try:
            i = line.find('{')
            if i > 0:
                line = line[i:]
            o = json.loads(line)
            if 'stack' in o:
                o['err'] = {
                    'stack': o['stack'],
                    'type': 'Error',
                }
                del o['stack']
            line = json.dumps(o)
        except Exception as err:
            print(err)
        finally:
            print(line)

if __name__ == '__main__':
    main()
