CC=gcc
CFLAGS=-Wall -O2
all: capture
capture: gpio_dma.c
	$(CC) $(CFLAGS) -o $@ $< -lrt
clean:
	rm -f capture
