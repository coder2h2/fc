// fc.c
// C implementation of FileConnect loading functions

#include <stdio.h>
#include <stdlib.h>
#include "fc.h"

char* fc_link_text(const char* filepath) {
    FILE* file = fopen(filepath, "r");
    if (!file) {
        return NULL;
    }

    // Determine file size
    fseek(file, 0, SEEK_END);
    long size = ftell(file);
    fseek(file, 0, SEEK_SET);

    char* buffer = (char*)malloc(size + 1);
    if (!buffer) {
        fclose(file);
        return NULL;
    }

    fread(buffer, 1, size, file);
    buffer[size] = '\0';

    fclose(file);
    return buffer;
}

char* fc_link_run(const char* filepath, const char* args) {
    // Basic subprocess launcher using popen
    char command[1024];
    snprintf(command, sizeof(command), "%s %s", filepath, args);

    FILE* pipe = popen(command, "r");
    if (!pipe) {
        return NULL;
    }

    // Read pipe output into dynamically allocated buffer
    char* output = (char*)malloc(4096);
    int total_read = 0;
    char temp[256];

    while (fgets(temp, sizeof(temp), pipe) != NULL) {
        snprintf(output + total_read, 4096 - total_read, "%s", temp);
        total_read += sizeof(temp);
    }
    
    pclose(pipe);
    return output;
}
