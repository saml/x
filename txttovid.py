"""
text to video
"""
import subprocess
import argparse
import sys
import logging

_log = logging.getLogger(__name__)


def build_ffmpeg_cmd(txt, audio_path, output_path):
    filter_graph = ';'.join([
        'mandelbrot=s=720x720[mandel]',
        '[0:a]showwaves=s=720x720:mode=line[wav]',
        '[wav]format=rgba,colorchannelmixer=aa=0.6[wavalpha]',
        '[mandel][wavalpha]overlay[vid]',
        '[vid]drawtext=text="{}":fontfile=/usr/share/fonts/naver-nanum/NanumGothic.ttf:fontcolor=white:fontsize=30:x=(w-text_w)/5:y=(h-text_h)/5[out]'.format(txt.replace('"', '\\"')),
    ])
    return [
        'ffmpeg', '-i', audio_path, 
        '-filter_complex', filter_graph,
        '-map', '[out]', 
        '-map', '0:a', 
        '-c:v', 'libx264', 
        '-c:a aac', 
        '-pix_fmt', 'yuv420p',
        '-shortest',
        output_path,
    ]


def main(txt, audio_path, output_path):
    cmd = build_ffmpeg_cmd(txt, audio_path, output_path)
    _log.info('Executing command: %s', cmd)
    subprocess.run(cmd)

if __name__ == '__main__':
    logging.basicConfig(level='DEBUG', format='%(asctime)s %(levelname)s %(message)s')
    parser = argparse.ArgumentParser()
    parser.add_argument('audio')
    parser.add_argument('output')
    parser.add_argument('txt', default=sys.stdin, type=argparse.FileType('r'), nargs='?')
    args = parser.parse_args()
    main(args.txt.read(), args.audio, args.output)