#ifndef HVZA_H
#define HVZA_H
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Caller must verify libhvza.so, story.db, and the pinned public key BEFORE loading. */
/* Returns opaque connection, or NULL. */
typedef struct hvza_db hvza_db;
hvza_db* hvza_open(const char *db_path);
void hvza_close(hvza_db *db);
int hvza_count(hvza_db *db);
/* Returns malloc-allocated UTF-8 JSON object or NULL. Caller frees with hvza_free. */
char* hvza_get_by_id(hvza_db *db, long long id);
char* hvza_get_by_tg(hvza_db *db, const char *tg_code);
/* Offset and limit must be nonnegative. Returns JSON array; caller frees. */
char* hvza_list(hvza_db *db, int offset, int limit);
void hvza_free(void *p);
#ifdef __cplusplus
}
#endif
#endif
