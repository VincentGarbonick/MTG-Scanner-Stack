#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

const int GPIO_PIN = 194; // pin 15
const char SYS_PATH[] = "/sys/class/gpio/gpio194/value";


void initialize()
{
    FILE* filePointer;
    char* buffer = malloc(sizeof(char) * 4);

    filePointer = fopen("/sys/class/gpio/export", "wb");
    strcpy(buffer, "194");
    fwrite(buffer, sizeof(char), sizeof(buffer), filePointer);
    fclose(filePointer);

    filePointer = fopen("/sys/class/gpio/gpio194/direction", "wb");
    strcpy(buffer, "out");
    fwrite(buffer, sizeof(char), sizeof(buffer), filePointer);
    fclose(filePointer);

    free(buffer);
}


void step_duration(unsigned int duration, unsigned int frequency)
{
    int iterations = frequency * (duration / 2.0);
    double period = (double) (1.0 / frequency) * 1000000.0;
    
    FILE* filePointer;
    for (int i=0; i<iterations; i++)
    {
        filePointer = fopen(SYS_PATH, "wb");
        fputc('0', filePointer);
        fclose(filePointer);
        usleep(period);

        filePointer = fopen(SYS_PATH, "wb");
        fputc('1', filePointer);
        fclose(filePointer); 
        usleep(period);
    }
    filePointer = fopen(SYS_PATH, "wb");
    fputc('0', filePointer);
    fclose(filePointer);
}

int main()
{
    initialize();
    step_duration(5, 2000);
}