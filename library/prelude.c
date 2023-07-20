/*
** Copyright 2023, COMAS (ABN 11 932 720 318) and the project contributors
** SPDX-License-Identifier: BSD-3-Clause
*/

#include <stdint.h>
#include <stddef.h>
#include <stdarg.h>

/* libmantle prelude: constant definitions */
#define AU_STORE(ptr, val) (*(ptr) = (val), nil)
#define false 0
#define nil   0
#define true  1

/* libmantle prelude: Austral types */
typedef int8_t    au_int8_t;
typedef int16_t   au_int16_t;
typedef int32_t   au_int32_t;
typedef int64_t   au_int64_t;
typedef size_t    au_index_t;
typedef uint8_t   au_nat8_t;
typedef uint16_t  au_nat16_t;
typedef uint32_t  au_nat32_t;
typedef uint64_t  au_nat64_t;
typedef uint8_t   au_bool_t;
typedef uint8_t   au_region_t;
typedef uint8_t   au_unit_t;
typedef void*     au_fnptr_t;


/* libmantle: Austral spans 1 */
typedef struct {
  void* data;
  size_t size;
} au_span_t;
au_span_t au_make_span(void* data, size_t size) {
  return (au_span_t){ .data = data, .size = size };
}
au_span_t au_make_span_from_string(const char* data, size_t size) {
  return (au_span_t){ .data = (void*) data, .size = size };
}

/* libmantle: sel4cp-provided printing and hang-on-abort */
au_unit_t au_abort_internal(const char* message) {
  extern void sel4cp_dbg_puts(const char *s);
  sel4cp_dbg_puts("[libmantle] abort: ");
  sel4cp_dbg_puts(message);
  for (;;) {
    continue;
  }
  return nil;
}

au_unit_t au_abort(au_span_t message) {
  extern void sel4cp_dbg_puts(const char *s);
  sel4cp_dbg_puts("[libmantle] abort: on user request");
  for (;;) {
    continue;
  }
  return nil;
}

/* libmantle: Austral spans 2 */
au_unit_t au_printf(const char* format, ...) {
  // print is for mock debugging only, we do not print in sel4cp mode
  return nil;
}

void* au_array_index(au_span_t* array, size_t index, size_t elem_size) {
  if (index >= array->size) {
    au_abort_internal("Array index out of bounds.");
  }

  au_index_t offset = 0;
  if (__builtin_mul_overflow(index, elem_size, &offset)) {
    au_abort_internal("Multiplication overflow in array indexing operation.");
  }

  char* data = (char*) array->data;
  char* ptr = data + offset;
  return (void*)(ptr);
}

/* libmantle: fail to compile w/ dynamic memory */
/*
void* au_calloc(size_t size, size_t count) {
  au_abort_internal("Dynamic memory allocation is not supported.");
  return NULL;
}
void* au_realloc(void* ptr, size_t count) {
  au_abort_internal("Dynamic memory allocation is not supported.");
  return NULL;
}
void* au_memmove(void* destination, void* source, size_t count) {
  au_abort_internal("Dynamic memory allocation is not supported.");
  return NULL;
}
void* au_memcpy(void* destination, void* source, size_t count) {
  au_abort_internal("Dynamic memory allocation is not supported.");
  return NULL;
}
au_unit_t au_free(void* ptr) {
  au_abort_internal("Dynamic memory allocation is not supported.");
  return nil;
};
*/

/* libmantle: Austral CLI handling is disabled */
static int _au_argc = -1;
static char** _au_argv = NULL;
void au_store_cli_args(int argc, char** argv) {
  return;
}
size_t au_get_argc() {
  au_abort_internal("Prelude error: argc not available on sel4cp.");
  return (size_t)(0);
}
au_span_t au_get_nth_arg(size_t n) {
  au_abort_internal("Prelude error: arguments not available on sel4cp.");
  au_span_t arg_array = ((au_span_t){ .data = NULL, .size = 0 });
  return arg_array;
}
