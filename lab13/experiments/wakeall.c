// wakeall.c (experiment for Observe 3): three children wait on semaphore 5,
// which starts at 0. The parent gives ONE unit. How many children pass?
#include "kernel/types.h"
#include "user/user.h"

int
main(void)
{
  sem_init(5, 0);
  for (int i = 1; i <= 3; i++) {
    if (fork() == 0) {
      sem_down(5);
      printf("child %d passed sem_down\n", i);
      exit(0);
    }
  }
  pause(10);                       // let all three go to sleep first
  printf("parent: one sem_up\n");
  sem_up(5);
  pause(20);
  printf("parent: two more sem_up\n");
  sem_up(5);
  sem_up(5);
  for (int i = 0; i < 3; i++)
    wait(0);
  printf("wakeall: done\n");
  exit(0);
}
