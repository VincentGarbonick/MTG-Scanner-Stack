#include <stdio.h>
#include <stdlib.h>
#include <time.h>


int main()
{
    /*
    clock_t begin = clock();
    
    for (int i=0; i < 1000; ++i)
    {
        system("echo 1 > test");
        system("echo 1 > test");
    }

    clock_t end = clock();
    double time_spent = (double)(end - begin) / CLOCKS_PER_SEC;
    printf("%g", time_spent);
    return 0;
    */


    // This method seems to be fastest/most consistent 
    FILE* filePointer;
    char writeData1 = '1';
    char writeData0 = '0';

    clock_t begin = clock();


   for (int i=0; i < 1000; ++i)
    {
        filePointer = fopen("test", "wb");
        fputc(writeData1, filePointer);
        fclose(filePointer);

        filePointer = fopen("test", "wb");
        fputc(writeData0, filePointer);
        fclose(filePointer);
    }

    clock_t end = clock();
    double time_spent = (double)(end - begin) / CLOCKS_PER_SEC;
    printf("%g", time_spent);
    return 0;
    
    /*

    FILE* filePointer;
    unsigned int writeData1 = 0b00000001;
    unsigned char writeData1c = writeData1;
    unsigned int writeData0 = 0b00000000;
    unsigned char writeData0c = writeData0;

    clock_t begin = clock();

    for (int i=0; i < 1000; ++i)
    {

        filePointer = fopen("test", "wb");
        fwrite(&writeData1c, 1, 1, filePointer);
        fclose(filePointer);

        filePointer = fopen("test", "wb");
        fwrite(&writeData0c, 1, 1, filePointer);
        fclose(filePointer);
    }

    clock_t end = clock();
    double time_spent = (double)(end - begin) / CLOCKS_PER_SEC;
    printf("%g", time_spent);
    return 0;
    */
}