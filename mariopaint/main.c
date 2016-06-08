#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>

#include <pulse/simple.h>
#include <pulse/error.h>

#define BUFSIZE 1024

int main(int argc, char* argv[]) {
  int err;
  int ret;
  int sample_rate = 44100;
  int channels = 2;

  if (argc > 1) {
    sample_rate = atoi(argv[1]);
  }
  if (argc > 2) {
    channels = atoi(argv[2]);
  }
  
  // opterr = 0;
  // while ((c = getopt(argc, argv, "s:c:")) != -1) {
  //   switch (c) {
  //     case 's':
  //     sample_rate = atoi(optarg);
  //     break;
  //     case 'c':
  //     channels = atoi(optarg);
  //     break;
  //     case '?':

  //   }
  // }

  pa_sample_spec sample_spec = {
    .format = PA_SAMPLE_S16LE,
    .rate = sample_rate,
    .channels = channels,
  };
  printf("Using samplerate: %d channels: %d\n", sample_spec.rate, sample_spec.channels);
  pa_simple *s;
  if (!(s = pa_simple_new(NULL, argv[0], PA_STREAM_PLAYBACK, NULL, "playback", &sample_spec, NULL, NULL, &err))) {
    fprintf(stderr, __FILE__ ": pa_simple_new() failed: %s\n", pa_strerror(err));
    goto finish;
  }

  while (1) {
    uint8_t buf[BUFSIZE];
    ssize_t r;
    if ((r = read(STDIN_FILENO, buf, sizeof(buf))) <= 0) {
      if (r == 0) {/* EOF */
        break;
      }
      fprintf(stderr, __FILE__ ": read() failed: %s\n", strerror(errno));
      goto finish;
    }
    if (pa_simple_write(s, buf, (size_t) r, &err) < 0) {
      fprintf(stderr, __FILE__ ": pa_simple_write() failed: %s\n", pa_strerror(err));
      goto finish;
    }
  }

  if (pa_simple_drain(s, &err) < 0) {
    fprintf(stderr, __FILE__ ": pa_simple_drain() failed: %s\n", pa_strerror(err));
    goto finish;
  }

finish:
  if (s) {
    pa_simple_free(s);
  }
  return ret;
}
