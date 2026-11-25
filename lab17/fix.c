/* fix.c - the "on paper" fix from Part 2, built to check it.
 * Same as fire4.c, but counter++ runs inside a mutex: only one thread at a
 * time may do the read-add-write, so no update can be overwritten.
 * Build: gcc -Wall -Wextra -pthread -o fix fix.c
 */
#include <stdio.h>
#include <pthread.h>

#ifndef T
#define T 4
#endif
#define N 1000000
long counter = 0;
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

void *work(void *arg) {
    (void)arg;
    for (int i = 0; i < N; i++) {
        pthread_mutex_lock(&lock);    /* enter: others wait here */
        counter++;                    /* read, add, write: now uninterrupted by the others */
        pthread_mutex_unlock(&lock);  /* leave: let the next one in */
    }
    return NULL;
}

int main(void) {
    pthread_t th[T];
    for (long i = 0; i < T; i++)
        pthread_create(&th[i], NULL, work, (void *)i);
    for (int i = 0; i < T; i++)
        pthread_join(th[i], NULL);
    printf("expected: %ld\ncounter:  %ld\n", (long)T * N, counter);
    return 0;
}
