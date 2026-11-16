/* deadlock.c - two threads, two mutexes. This is the FIXED version: both threads
 * take A first, then B, so a circle of waiting can never form.
 * Build: gcc -Wall -pthread -o deadlock deadlock.c
 * Run:   timeout 5 ./deadlock; echo "exit code: $?"
 * The original, deadlocking order (two() takes B, then A):
 *        gcc -Wall -pthread -DORIGINAL -o deadlock_orig deadlock.c
 *        add -DNOSLEEP to drop the two sleep(1) lines (Observe 4.2)
 */
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>

#ifdef NOSLEEP
#define PAUSE()
#else
#define PAUSE() sleep(1)
#endif

pthread_mutex_t A = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t B = PTHREAD_MUTEX_INITIALIZER;

void *one(void *arg) {
    pthread_mutex_lock(&A);
    printf("one: I have A, I want B\n");
    PAUSE();
    pthread_mutex_lock(&B);             /* waits for two */
    printf("one: I have both\n");
    pthread_mutex_unlock(&B);
    pthread_mutex_unlock(&A);
    return NULL;
}

#ifndef ORIGINAL
void *two(void *arg) {                  /* the fix: lock A first here too */
    pthread_mutex_lock(&A);
    printf("two: I have A, I want B\n");
    PAUSE();
    pthread_mutex_lock(&B);
    printf("two: I have both\n");
    pthread_mutex_unlock(&B);
    pthread_mutex_unlock(&A);
    return NULL;
}
#else
void *two(void *arg) {                  /* opposite order: the deadlock */
    pthread_mutex_lock(&B);
    printf("two: I have B, I want A\n");
    PAUSE();
    pthread_mutex_lock(&A);             /* waits for one */
    printf("two: I have both\n");
    pthread_mutex_unlock(&A);
    pthread_mutex_unlock(&B);
    return NULL;
}
#endif

int main(void) {
    setvbuf(stdout, NULL, _IOLBF, 0);
    pthread_t t1, t2;
    pthread_create(&t1, NULL, one, NULL);
    pthread_create(&t2, NULL, two, NULL);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    printf("done\n");
    return 0;
}
