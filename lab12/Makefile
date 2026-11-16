# Lab 12 - Producer, Consumer and the Other Tools
CC     = gcc
CFLAGS = -Wall -pthread
PROGS  = prodcons condvar readers deadlock
VARIANTS = prodcons_swapped condvar_if deadlock_orig deadlock_nosleep

all: $(PROGS) $(VARIANTS)

%: %.c
	$(CC) $(CFLAGS) -o $@ $<

prodcons_swapped: prodcons.c
	$(CC) $(CFLAGS) -DSWAPPED -o $@ $<
condvar_if: condvar.c
	$(CC) $(CFLAGS) -DUSE_IF -o $@ $<
deadlock_orig: deadlock.c
	$(CC) $(CFLAGS) -DORIGINAL -o $@ $<
deadlock_nosleep: deadlock.c
	$(CC) $(CFLAGS) -DORIGINAL -DNOSLEEP -o $@ $<

clean:
	rm -f $(PROGS) $(VARIANTS)

.PHONY: all clean
