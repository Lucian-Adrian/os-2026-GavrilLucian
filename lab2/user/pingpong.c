#include "kernel/types.h"
#include "user/user.h"

int
main(void)
{
  int parent_to_child[2];
  int child_to_parent[2];
  char byte = 'x';

  if(pipe(parent_to_child) < 0 || pipe(child_to_parent) < 0){
    fprintf(2, "pingpong: cannot create pipes\n");
    exit(1);
  }

  int child = fork();
  if(child < 0){
    fprintf(2, "pingpong: cannot fork\n");
    exit(1);
  }

  if(child == 0){
    close(parent_to_child[1]);
    close(child_to_parent[0]);
    if(read(parent_to_child[0], &byte, 1) != 1){
      fprintf(2, "pingpong: child did not receive a byte\n");
      exit(1);
    }
    printf("%d: received ping\n", getpid());
    if(write(child_to_parent[1], &byte, 1) != 1){
      fprintf(2, "pingpong: child could not return the byte\n");
      exit(1);
    }
    close(parent_to_child[0]);
    close(child_to_parent[1]);
    exit(0);
  }

  close(parent_to_child[0]);
  close(child_to_parent[1]);
  if(write(parent_to_child[1], &byte, 1) != 1 ||
     read(child_to_parent[0], &byte, 1) != 1){
    fprintf(2, "pingpong: parent exchange failed\n");
    exit(1);
  }
  printf("%d: received pong\n", getpid());
  close(parent_to_child[1]);
  close(child_to_parent[0]);
  wait(0);
  exit(0);
}
