#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <sys/stat.h>
#include <string.h>
#include "rslv.h"

int get_data(char * path, char * read_filename, FILE * out_file) {
    char * file_path = calloc(sizeof(path) + sizeof(read_filename), sizeof(char));
    strcat(file_path, path);
    // path missing trailing slash
    if (path[strlen(path) - 1 ] != '\\') { 
        strcat(file_path, "\\");
    }
    strcat(file_path, read_filename);

    printf("Grabbing data from %s...\n", file_path);
    FILE * pfile = fopen(file_path, "r");
    if (pfile == NULL) { 
        perror("fopen");
        printf("Failed to open file %s for reading. Exiting %d\n", file_path, RSLVE_READERR);
        exit(RSLVE_READERR);
    }

    char line[100000] = {0};
    char siteid[1000] = {0};
    char date[11] = {0};
    char time[9] = {0};
    char method[5] = {0};
    char uri[1000] = {0};
    char username[36] = {0};
    char src_ip[160] = {0};
    int port = {0};
    int status = {0};
    int substatus = {0};
    int rslvtime = {0};
    int win32stat = {0};
    char useragent[1000] = {0};
    char referer[1000] = {0};
    char ip[160] = {0};
    while (fgets(line, 100000, pfile)) {
        if (line[0] != '#') {
            sscanf(line, "%s %s %s %s %s %s %d %s %s %s %s %d %d %d %d", date, time, ip, method, uri, siteid, &port, username, src_ip, useragent, referer, &status, &substatus, &win32stat, &rslvtime);
            fprintf(out_file,"%s,%s,%s,%s,%s,%s,%s,%d,%d,%d\n", date, time, method, uri, siteid, username, src_ip, status, substatus, rslvtime);
        }
    }
    fclose(pfile);
    printf("\nDone\n");
    return RSLVE_OK;


}

int main(int argc, char ** argv) { 
    struct dirent *entry = NULL;
    DIR *pdir = NULL;
    char * path = argc > 1 ? argv[1] : ".";
    pdir = opendir(path);
    FILE * pOutFile = fopen("output.csv", "w");
    if (pOutFile == NULL) {
        perror("fopen");
        printf("Failed to open output file. Exiting %d", RSLVE_WRITEERR);
        exit(RSLVE_WRITEERR);
    }
    fprintf(pOutFile, "Date,Time,Method,URI,Query Params,Username,Source IP, Response Code, SubCode, Response Time\n");
    if (pdir != NULL) { 
        while ((entry = readdir(pdir))) { 
            // Skip hidden files / . / ..
            if (entry->d_name[0] != '.') { 
                if (get_data(path, entry->d_name,pOutFile) != RSLVE_OK) { 
                    printf("Error while getting data\n");
                }
            }
        }
    } else {
        printf("Failed to open directory: %s", path);
        return RSLVE_ERROR;
    }
    printf("Finished\n");
    closedir(pdir);
    fclose(pOutFile);
    return RSLVE_OK;
}
