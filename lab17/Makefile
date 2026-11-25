CFLAGS = -Wall -Wextra -pthread
all: fire fire4 fire8 fix
fire: fire.c ; gcc $(CFLAGS) -o $@ $<
fire4: fire4.c ; gcc $(CFLAGS) -o $@ $<
fire8: fire4.c ; gcc $(CFLAGS) -DT=8 -o $@ $<
fix: fix.c ; gcc $(CFLAGS) -o $@ $<
fire-O2: fire.c ; gcc $(CFLAGS) -O2 -o $@ $<
fire.s: fire.c ; gcc -S -o $@ $<
clean: ; rm -f fire fire4 fire8 fix fire-O2 fire.s
.PHONY: all clean
