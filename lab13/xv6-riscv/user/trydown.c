// trydown.c: the optional sem_trydown (Lab 13). Semaphore 4 starts at 2,
// so the first two calls take a unit and the third returns -1 at once.
#include "kernel/types.h"
#include "user/user.h"

int
main(void)
{
  sem_init(4, 2);
  for (int i = 1; i <= 3; i++)
    printf("try %d: sem_trydown(4) = %d\n", i, sem_trydown(4));
  sem_up(4);
  printf("after sem_up(4): sem_trydown(4) = %d\n", sem_trydown(4));
  printf("bad id: sem_trydown(9) = %d, sem_down(-1) = %d\n", sem_trydown(9), sem_down(-1));
  exit(0);
}
