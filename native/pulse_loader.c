// pulse_loader.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#ifdef _WIN32
#define SEP '\\'
#else
#define SEP '/'
#endif

static void module_to_relpath(const char *name, char *out, size_t out_size)
{
    size_t i;
    size_t len = strlen(name);
    if (len + 5 >= out_size)
    {
        out[0] = '\0';
        return;
    }

    for (i = 0; i < len; ++i)
    {
        out[i] = (name[i] == '.') ? SEP : name[i];
    }

    out[len] = '.';
    out[len + 1] = 'p';
    out[len + 2] = 'u';
    out[len + 3] = 'l';
    out[len + 4] = '\0';
}

int pulse_find_module(const char *name, const char **search_dirs, char *out_path, size_t out_size)
{
    char relpath[512];
    struct stat st;

    module_to_relpath(name, relpath, sizeof(relpath));
    if (relpath[0] == '\0')
        return 0;

    for (int i = 0; search_dirs[i] != NULL; ++i)
    {
        size_t base_len = strlen(search_dirs[i]);
        size_t rel_len = strlen(relpath);

        if (base_len + rel_len + 2 >= out_size)
            continue;

        memcpy(out_path, search_dirs[i], base_len);
        out_path[base_len] = SEP;
        memcpy(out_path + base_len + 1, relpath, rel_len + 1);

        if (stat(out_path, &st) == 0 && S_ISREG(st.st_mode))
            return 1;
    }

    return 0;
}

char *pulse_read_file(const char *path, size_t *out_len)
{
    FILE *f = fopen(path, "rb");
    if (!f)
        return NULL;

    if (fseek(f, 0, SEEK_END) != 0)
    {
        fclose(f);
        return NULL;
    }
    long size = ftell(f);
    if (size < 0)
    {
        fclose(f);
        return NULL;
    }
    rewind(f);

    char *buf = (char *)malloc((size_t)size + 1);
    if (!buf)
    {
        fclose(f);
        return NULL;
    }

    size_t read = fread(buf, 1, (size_t)size, f);
    fclose(f);

    buf[read] = '\0';
    *out_len = read;
    return buf;
}

void pulse_free_buffer(char *buf)
{
    free(buf);
}