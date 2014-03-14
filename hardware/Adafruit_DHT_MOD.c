//  How to access GPIO registers from C-code on the Raspberry-Pi
//  Example program
//  15-January-2012
//  Dom and Gert
//


// Access from ARM Running Linux

#define BCM2708_PERI_BASE        0x20000000
#define GPIO_BASE                (BCM2708_PERI_BASE + 0x200000) /* GPIO controller */
#define MAX_RETRIES		 5

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <dirent.h>
#include <fcntl.h>
#include <assert.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <bcm2835.h>
#include <unistd.h>
#include <sched.h>

#define MAXTIMINGS 40

//#define DEBUG
#define SILENT 1

#define DHT11 11
#define DHT22 22
#define AM2302 22

int bits[MAXTIMINGS+1], data[5];
int readDHT(int type, int pin, int allowRetry);

int main(int argc, char **argv)
{
    if (!bcm2835_init())
        return 1;

    if (argc != 3) {
	printf("usage: %s [11|22|2302] GPIOpin#\n", argv[0]);
	printf("example: %s 2302 4 - Read from an AM2302 connected to GPIO #4\n", argv[0]);
	return 2;
    }
    int type = 0;
    if (strcmp(argv[1], "11") == 0) type = DHT11;
    if (strcmp(argv[1], "22") == 0) type = DHT22;
    if (strcmp(argv[1], "2302") == 0) type = AM2302;
    if (type == 0) {
	printf("Select 11, 22, 2302 as type!\n");
	return 3;
    }  
  
    int dhtpin = atoi(argv[2]);

    if (dhtpin <= 0) {
	printf("Please select a valid GPIO pin #\n");
	return 3;
    } 

    if( SILENT < 1 ) {
    	printf("Using pin #%d\n", dhtpin);
    }
    readDHT(type, dhtpin, MAX_RETRIES);

    return 0;
}

int readDHT(int type, int pin, int allowRetry) {
    int bitidx = 0;
    int counter = 0;
    int j=0;
    int i=0;

    data[0] = data[1] = data[2] = data[3] = data[4] = 0;

    // Set GPIO pin to output
    bcm2835_gpio_fsel(pin, BCM2835_GPIO_FSEL_OUTP);

    bcm2835_gpio_write(pin, LOW);
    bcm2835_gpio_write(pin, HIGH);

    bcm2835_gpio_fsel(pin, BCM2835_GPIO_FSEL_INPT);

    // wait for pin to drop
    while (bcm2835_gpio_lev(pin) == HIGH){
	if( counter++ > 10000 ) {
	    printf( "ERROR: Pin never dropped\n" );
            return 1;
	}
    }

    // read data!
    while (i<= MAXTIMINGS) {
        counter = 0;
        while ( bcm2835_gpio_lev(pin) == LOW) {
            if (counter++ == 1000)
	      break;
        }
        counter = 0;
        while ( bcm2835_gpio_lev(pin) == HIGH) {
            if (counter++ == 1000)
	      break;
        }
        bits[bitidx++] = counter;
        i++;
    }

    // Compile bits
    j = 0;
    for (int i=1; i<bitidx; i++) {
        // shove each bit into the storage bytes
        data[j/8] <<= 1;
        if (bits[i] > 200) {
            data[j/8] |= 1;
	}
        j++;
    }

#ifdef DEBUG
    for (int i=1; i<bitidx; i++) {
        printf("bit %d: %d (%d)\n", i, bits[i], bits[i] > 200);
    }
#endif

    if( SILENT < 1 ) {
    	printf("Data (%d): 0x%x 0x%x 0x%x 0x%x 0x%x\n", j, data[0], data[1], data[2], data[3], data[4]);
    }

    // Check to make sure we have enough bits and a correct checksum
    if ((j >= 39) && (data[4] == ((data[0] + data[1] + data[2] + data[3]) & 0xFF)) ) {
        if (type == DHT11)
	    printf("Temp = %d *C, Hum = %d \%\n", data[2], data[0]);
        if (type == DHT22) {
	    float f, h;
	    h = data[0] * 256 + data[1];
	    h /= 10;

	    f = (data[2] & 0x7F)* 256 + data[3];
            f /= 10.0;
            if (data[2] & 0x80)  f *= -1;
	    // printf("CTemp: %.1f\nFTemp: %.1f\nHum: %.1f%\n", f, ((f*9)/5)+32, h);
	    printf("Temp =  %.1f *C, Hum = %.1f \%\n", f, h);
        }
    } else if( allowRetry > 0 ) {
    	sleep(1);
        if( SILENT < 1 ) {
	    printf( "Error getting information. Retrying\n" );
        }
     	return readDHT( type, pin, --allowRetry );
    } else {
        if( SILENT < 1 ) {
	    printf( "Error getting information. Retries exhausted.\n" );
        }
    	return 1;
    }

    return 0;
}
