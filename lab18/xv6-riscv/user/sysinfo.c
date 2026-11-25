#include "kernel/types.h"
#include "kernel/sysinfo.h"
#include "user/user.h"

// Print free memory and process count, then show that both react:
// a fork adds a process, an sbrk takes pages from the free list.
static void
show(char *when)
{
  struct sysinfo info;
  if (sysinfo(&info) < 0) {
    fprintf(2, "sysinfo: failed\n");
    exit(1);
  }
  printf("%s: free %ld bytes (%ld pages), %ld processes\n", when, info.freemem, info.freemem / 4096, info.nproc);
}

int
main(void)
{
  show("start      ");
  int pid = fork();
  if (pid == 0) {
    pause(10);
    exit(0);
  }
  show("after fork ");
  sbrk(40960);
  show("after sbrk ");
  wait(0);
  show("after wait ");
  if (sysinfo((struct sysinfo *)0xffffffffff) < 0)
    printf("bad pointer: sysinfo returned -1\n");
  exit(0);
}
