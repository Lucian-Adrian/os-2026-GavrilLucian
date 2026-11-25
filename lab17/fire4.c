/* fire4.c - Part 2: the same race with T threads (default 4).
 * Build: gcc -Wall -Wextra -pthread -o fire4 fire4.c        (4 threads)
 *        gcc -Wall -Wextra -pthread -DT=8 -o fire8 fire4.c  (8 threads)
 * Each thread also prints the ADDRESS of counter: one address for all threads
 * is the direct proof that they share one variable.
 */
#include <stdio.h>
#include <pthread.h>

#ifndef T
#define T 4
#endif
#define N 1000000
long counter = 0;

void *work(void *arg) {
    long id = (long)arg;
    printf("thread %ld sees counter = %ld at %p\n", id, counter, (void *)&counter);
    for (int i = 0; i < N; i++)
        counter++;
    return NULL;
}

int main(void) {
    pthread_t th[T];
    for (long i = 0; i < T; i++)
        pthread_create(&th[i], NULL, work, (void *)(i + 1));
    for (int i = 0; i < T; i++)
        pthread_join(th[i], NULL);
    long expected = (long)T * N;
    printf("expected: %ld\n", expected);
    printf("counter:  %ld   (lost %ld = %.1f%%)\n", counter, expected - counter,
           100.0 * (expected - counter) / expected);
    return 0;
}
