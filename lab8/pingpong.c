#include "kernel/types.h"
#include "user/user.h"

int
main(void)
{
  int parent_to_child[2];
  int child_to_parent[2];
  int child_pid;
  int bytes;
  char token = 'x';

  if(pipe(parent_to_child) < 0){
    printf("pingpong: first pipe failed\n");
    exit(1);
  }
  if(pipe(child_to_parent) < 0){
    printf("pingpong: second pipe failed\n");
    close(parent_to_child[0]);
    close(parent_to_child[1]);
    exit(1);
  }

  child_pid = fork();
  if(child_pid < 0){
    printf("pingpong: fork failed\n");
    exit(1);
  }

  if(child_pid == 0){
    close(parent_to_child[1]);
    close(child_to_parent[0]);

    bytes = read(parent_to_child[0], &token, 1);
    if(bytes != 1){
      printf("pingpong: child read failed\n");
      exit(1);
    }
    printf("%d: received ping\n", getpid());

    bytes = write(child_to_parent[1], &token, 1);
    if(bytes != 1){
      printf("pingpong: child write failed\n");
      exit(1);
    }

    close(parent_to_child[0]);
    close(child_to_parent[1]);
    exit(0);
  }

  close(parent_to_child[0]);
  close(child_to_parent[1]);

  bytes = write(parent_to_child[1], &token, 1);
  if(bytes != 1){
    printf("pingpong: parent write failed\n");
    exit(1);
  }
  close(parent_to_child[1]);

  bytes = read(child_to_parent[0], &token, 1);
  if(bytes != 1){
    printf("pingpong: parent read failed\n");
    exit(1);
  }
  printf("%d: received pong\n", getpid());
  close(child_to_parent[0]);

  if(wait(0) < 0){
    printf("pingpong: wait failed\n");
    exit(1);
  }
  exit(0);
}
