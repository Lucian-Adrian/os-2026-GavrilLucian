#include "kernel/types.h"
#include "user/user.h"

int
main(int argc, char *argv[])
{
  if(argc != 2){
    fprintf(2, "usage: sleep <ticks>\n");
    exit(1);
  }
  // Compatible with both traditional xv6 (sleep) and post-Aug 2025 tree (pause)
  sleep(atoi(argv[1]));
  exit(0);
}
