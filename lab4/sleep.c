#include "kernel/types.h"
#include "user/user.h"

int
main(int argc, char *argv[])
{
  if(argc != 2){
    fprintf(2, "usage: sleep <ticks>\n");
    exit(1);
  }
  // Match the system call declared in this course tree's user/user.h.
  sleep(atoi(argv[1]));
  exit(0);
}
