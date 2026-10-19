#include "kernel/types.h"
#include "user/user.h"

static void filter(int input_fd) __attribute__((noreturn));

static void
filter(int input_fd)
{
  int prime;
  int bytes = sizeof(prime);
  int result = read(input_fd, &prime, bytes);
  int next_pipe[2];
  int child_pid;
  int candidate;

  if(result == 0){
    close(input_fd);
    exit(0);
  }
  if(result != bytes){
    printf("primes: failed to read a number\n");
    close(input_fd);
    exit(1);
  }

  printf("prime %d\n", prime);

  if(pipe(next_pipe) < 0){
    printf("primes: pipe failed\n");
    close(input_fd);
    exit(1);
  }

  child_pid = fork();
  if(child_pid < 0){
    printf("primes: fork failed\n");
    close(input_fd);
    close(next_pipe[0]);
    close(next_pipe[1]);
    exit(1);
  }

  if(child_pid == 0){
    close(input_fd);
    close(next_pipe[1]);
    filter(next_pipe[0]);
  }

  close(next_pipe[0]);

  while((result = read(input_fd, &candidate, bytes)) > 0){
    if(result != bytes){
      printf("primes: incomplete number\n");
      close(input_fd);
      close(next_pipe[1]);
      wait(0);
      exit(1);
    }

    if(candidate % prime != 0){
      if(write(next_pipe[1], &candidate, bytes) != bytes){
        printf("primes: write failed\n");
        close(input_fd);
        close(next_pipe[1]);
        wait(0);
        exit(1);
      }
    }
  }

  close(input_fd);
  close(next_pipe[1]);
  if(result < 0){
    printf("primes: read failed\n");
    wait(0);
    exit(1);
  }
  if(wait(0) < 0){
    printf("primes: wait failed\n");
    exit(1);
  }
  exit(0);
}

int
main(void)
{
  int input_pipe[2];
  int number;
  int child_pid;
  int bytes = sizeof(number);

  if(pipe(input_pipe) < 0){
    printf("primes: input pipe failed\n");
    exit(1);
  }

  child_pid = fork();
  if(child_pid < 0){
    printf("primes: producer fork failed\n");
    close(input_pipe[0]);
    close(input_pipe[1]);
    exit(1);
  }

  if(child_pid == 0){
    close(input_pipe[1]);
    filter(input_pipe[0]);
  }

  close(input_pipe[0]);
  for(number = 2; number <= 35; number++){
    if(write(input_pipe[1], &number, bytes) != bytes){
      printf("primes: input write failed\n");
      close(input_pipe[1]);
      wait(0);
      exit(1);
    }
  }
  close(input_pipe[1]);

  if(wait(0) < 0){
    printf("primes: producer wait failed\n");
    exit(1);
  }
  exit(0);
}
