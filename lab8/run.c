#include "kernel/types.h"
#include "user/user.h"

int
main(void)
{
  int child_pid;
  int child_status;

  printf("parent pid: %d\n", getpid());

  child_pid = fork();
  if(child_pid < 0){
    printf("fork failed\n");
    exit(1);
  }

  if(child_pid == 0){
    char *args[] = {"echo", "hello", "from", "the", "child", 0};

    printf("child pid: %d\n", getpid());
    exec("echo", args);
    printf("exec failed\n");
    exit(1);
  }

  if(wait(&child_status) < 0){
    printf("wait failed\n");
    exit(1);
  }

  printf("child %d ended with status %d\n", child_pid, child_status);
  exit(0);
}
