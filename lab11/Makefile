# Lab 11 - no -O2 on purpose: the optimizer would hide the race of Part 1.
CC     = gcc
CFLAGS = -Wall -pthread
PROGS  = race mutex sem order parking atomic
VARIANTS = sem2 order1 parking1

all: $(PROGS) $(VARIANTS)

%: %.c
	$(CC) $(CFLAGS) -o $@ $<

sem2: sem.c
	$(CC) $(CFLAGS) -DSTART=2 -o $@ $<
order1: order.c
	$(CC) $(CFLAGS) -DSTART=1 -o $@ $<
parking1: parking.c
	$(CC) $(CFLAGS) -DPLACES=1 -o $@ $<

# the three instructions behind counter++ (Observe 1.1)
race.s: race.c
	$(CC) -S -o $@ $<

clean:
	rm -f $(PROGS) $(VARIANTS) race.s

.PHONY: all clean
