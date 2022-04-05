#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

const char GPIO_PIN_11[] = "50"; // Linux GPIO # for Pin 11 on J6
const char GPIO_PIN_13[] = "14"; // Linux GPIO # for Pin 13 on J6
const char GPIO_PIN_15[] = "194"; // Linux GPIO # for Pin 15 on J6
const char GPIO_PIN_33[] = "38"; // Linux GPIO # for Pin 33 on J6
const char SYS_PATH[] = "/sys/class/gpio/gpio194/value";

void constructPinPath(char* pinPath, const char* pin, const char* entity)
{
    strcpy (pinPath, "/sys/class/gpio/gpio");
    strcat(pinPath, pin);
    strcat(pinPath, "/");
    strcat(pinPath, entity);
}

void initialize(const char* pin)
{
    FILE* filePointer;
    char* buffer = malloc(sizeof(char) * 4);
    char* fileName = malloc(64);

    filePointer = fopen("/sys/class/gpio/export", "wb");
    strcpy(buffer, pin);
    fwrite(buffer, sizeof(char), sizeof(buffer), filePointer);
    fclose(filePointer);

    constructPinPath(fileName, pin, "direction");

    filePointer = fopen(fileName, "wb");
    strcpy(buffer, "out");
    fwrite(buffer, sizeof(char), sizeof(buffer), filePointer);
    fclose(filePointer);

    free(buffer);
    free(fileName);
}

void setOutput(char* path, char value)
{
    FILE* filePointer;

    filePointer = fopen(path, "wb");
    fputc(value, filePointer);
    fclose(filePointer);

}


void step_duration(float duration, unsigned int frequency, char* path)
{
    int iterations = frequency * (duration / 2.0);
    double period = (double) (1.0 / frequency) * 1000000.0;

    
    
    FILE* filePointer;
    for (int i=0; i<iterations; i++)
    {
        filePointer = fopen(path, "wb");
        fputc('0', filePointer);
        fclose(filePointer);
        usleep(period/2.0);

        filePointer = fopen(path, "wb");
        fputc('1', filePointer);
        fclose(filePointer); 
        usleep(period/2.0);
    }

    // usleep(10);
    filePointer = fopen(path, "wb");
    fputc('0', filePointer);
    fclose(filePointer);
}

int main()
{
    char* pinPath1 = malloc(64);
    char* pinPath2 = malloc(64);
    char* pinPath3 = malloc(64);

    initialize(GPIO_PIN_15);
    initialize(GPIO_PIN_11);
    initialize(GPIO_PIN_33);

    constructPinPath(pinPath1, GPIO_PIN_11, "value");
    constructPinPath(pinPath2, GPIO_PIN_15, "value");
    constructPinPath(pinPath3, GPIO_PIN_33, "value");

    setOutput(pinPath1, '0');
    setOutput(pinPath3, '1');
    usleep(5000);
    
    for (int i = 0; i < 200000; i++)
    {
        setOutput(pinPath3, '0');
        usleep(5000);

        step_duration(1, 1500, pinPath2);


        setOutput(pinPath3, '1');
        // setOutput(pinPath1, '1');
        // usleep(5000);

        

        // step_duration(1, 2500, pinPath2);
        
        // setOutput(pinPath1, '0');


        sleep(1);

    }

    



    // for (int i = 0; i < 2; i++)
    // {
    //     step_duration(0.25, 2500, pinPath2);

    //     setOutput(pinPath1, '1');
        
    //     sleep(1);

    //     step_duration(0.3, 2000, pinPath2);

    //     setOutput(pinPath1, '0');

    //     sleep(1);

    // }

    free(pinPath1);
    free(pinPath2);
    free(pinPath3);

    return 0;
}