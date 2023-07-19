/*
** Copyright 2023, COMAS (ABN 11 932 720 318) and the project contributors
** SPDX-License-Identifier: BSD-3-Clause
*/

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "sel4cp.h"

/* libmantle API - wrappers */

uint64_t mantle_notify(sel4cp_channel ch) {
  sel4cp_notify(ch);
  return 0;
}

uint64_t mantle_irq_ack(sel4cp_channel ch) {
  sel4cp_irq_ack(ch);
  return 0;
}

uint64_t mantle_mr_set(uint8_t mr, uint64_t value) {
  sel4cp_mr_set(mr, value);
  return 0;
}

uint64_t mantle_mr_get(uint8_t mr) {
  return sel4cp_mr_get(mr);
}

uint16_t mantle_ret_count = 0;
uint16_t mantle_get_ret_count() {
  return mantle_ret_count;
}

uint64_t mantle_ppcall(sel4cp_channel ch, uint64_t msginfo_label, uint16_t msginfo_count) {
  sel4cp_msginfo msginfo = sel4cp_msginfo_new(msginfo_label, msginfo_count);
  sel4cp_msginfo ret = sel4cp_ppcall(ch, msginfo);
  mantle_ret_count = seL4_MessageInfo_get_length(msginfo);
  return sel4cp_msginfo_get_label(ret);
}

uint64_t mantle_ret_badge = 0;
uint64_t mantle_get_ret_badge() {
  return mantle_ret_badge;
}

uint64_t mantle_recv() { 
  sel4cp_msginfo ret = seL4_Recv(1, &mantle_ret_badge);
  mantle_ret_count = seL4_MessageInfo_get_length(ret);
  return sel4cp_msginfo_get_label(ret);
}

uint64_t mantle_replyrecv(uint64_t reply_tag_label, uint16_t reply_tag_count) {
  sel4cp_msginfo reply_tag = sel4cp_msginfo_new(reply_tag_label, reply_tag_count);
  sel4cp_msginfo ret = seL4_ReplyRecv(1, reply_tag, &mantle_ret_badge);
  mantle_ret_count = seL4_MessageInfo_get_length(ret);
  return sel4cp_msginfo_get_label(ret);
}

uint8_t* mantle_make_address(uint64_t address) {
  uint8_t *ret = (uint8_t*)address;
  return ret;
}
