#!/bin/bash
ffmpeg -i ~/Videos/4k.webm -filter_complex 'scale=w=640:h=480:force_original_aspect_ratio=decrease' -c:a aac -c:v h264 -profile:v main -g 48 -keyint_min 48 -sc_threshold 0 -hls_time 4 -hls_playlist_type vod -hls_segment_filename 'http://localhost:8080/bucketname/%03d.ts' http://localhost:8080/bucketname/x.m3u8

