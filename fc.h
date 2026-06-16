// fc.h
// C declarations for FileConnect (fc) loading logic

#ifndef FC_H
#define FC_H

// Expose a function to programmatically link to text files
char* fc_link_text(const char* filepath);

// Expose a function to run other script/executable file formats
char* fc_link_run(const char* filepath, const char* args);

#endif
