#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>

int main(int argc, char* argv[]) {
    int fileno = atoi(argv[1]);
    int secs = atoi(argv[2]);
    printf("Got fileno %d timeout_secs %d\n", fileno, secs);
    struct timeval tv;
    tv.tv_sec = secs;
    errno = 0;
    int ret = setsockopt(fileno, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(struct timeval));
    if (ret != 0) {
        printf("ret %d errno %d (%s)\n", ret, errno, strerror(errno));
    }
    return ret;
}
