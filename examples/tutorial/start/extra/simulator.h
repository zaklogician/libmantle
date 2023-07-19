/*
** Copyright 2023, COMAS (ABN 11 932 720 318) and the project contributors
** SPDX-License-Identifier: BSD-3-Clause
*/

/* sel4cp API simulator
 * 
 * This lets you simulate an environment for your mantle/sel4cp-based application
 * without having to cross-compile and run a whole system on QEMU.
 * 
 * You can use it simply by including sim4cp instead of the usual libsel4cp.
 * 
 * The simulate() function represents the behavior of the system, apart
 * from the PD you're currently simulating.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Simulation state */
#define SIM_CALLTYPE_RECV 0
#define SIM_CALLTYPE_REPLYRECV 1
#define SIM_CALLTYPE_PPCALL 2
uint64_t sim_calltype = SIM_CALLTYPE_RECV;

uint64_t sim_tick = 0;
uint64_t sim_notified = 0;
uint64_t sim_irq_acked = 0;
uint64_t sim_ppcalled = 0;

uint64_t sim_reply_label = 0;
uint64_t sim_msg_register[121] = {0};

uint64_t sim_return_badge = 0;


/* libseL4 API - the relevant parts */
uint64_t debug = 0;
struct seL4_MessageInfo {
    uint64_t words[1];
};
typedef struct seL4_MessageInfo seL4_MessageInfo_t;

seL4_MessageInfo_t seL4_MessageInfo_new(
    uint64_t label,
    uint64_t capsUnwrapped,
    uint64_t extraCaps,
    uint64_t length) {
    seL4_MessageInfo_t msginfo;
    msginfo.words[0] = 0
        | (label & 0xfffffffffffffull) << 12
        | (capsUnwrapped & 0x7ull) << 9
        | (extraCaps & 0x3ull) << 7
        | (length & 0x7full);
    return msginfo;
}

uint64_t seL4_MessageInfo_get_label(seL4_MessageInfo_t msginfo) {
    return (msginfo.words[0] & 0xfffffffffffff000ull) >> 12;
}

uint64_t seL4_MessageInfo_get_length(seL4_MessageInfo_t msginfo) {
    return msginfo.words[0] & 0x7full;
}

/* sel4cp and sim4cp API */
typedef uint32_t sel4cp_channel;
typedef seL4_MessageInfo_t sel4cp_msginfo;
#define SEL4CP_MAX_CHANNELS 63

void sel4cp_dbg_putc(int c) { }
void sel4cp_dbg_puts(const char *s) { }

void sel4cp_notify(sel4cp_channel ch) {
  if (ch > SEL4CP_MAX_CHANNELS) {
    sel4cp_dbg_puts("[MOCK] sel4cp_notify: ch too large\n");
    return;
  }
  sim_notified |= (1 << ch);
}

void sel4cp_irq_ack(sel4cp_channel ch) {
  if (ch > SEL4CP_MAX_CHANNELS) {
    sel4cp_dbg_puts("[MOCK] sel4cp_irq_ack: ch too large\n");
    return;
  }
  sim_irq_acked |= (1 << ch);
}

sel4cp_msginfo sel4cp_msginfo_new(uint64_t label, uint16_t count) {
  return seL4_MessageInfo_new(label, 0, 0, count);
}

uint64_t sel4cp_msginfo_get_label(sel4cp_msginfo msginfo) {
  return seL4_MessageInfo_get_label(msginfo);
}

void sel4cp_mr_set(uint8_t mr, uint64_t value) {
  if (mr > 120) {
    sel4cp_dbg_puts("[MOCK] sel4cp_mr_set: mr too large\n");
    return;
  }
  sim_msg_register[mr] = value;
}

uint64_t sel4cp_mr_get(uint8_t mr) {
  if (mr > 120) {
    sel4cp_dbg_puts("[MOCK] sel4cp_mr_get: mr too large\n");
    return 0;
  }
  return sim_msg_register[mr];
}

/* User provided function, returns messageinfo */
sel4cp_msginfo simulate();

sel4cp_msginfo sel4cp_ppcall(sel4cp_channel ch, sel4cp_msginfo msginfo) {
  if (ch > SEL4CP_MAX_CHANNELS) {
    sel4cp_dbg_puts("[MOCK] sel4cp_ppcall: ch too large\n");
  }
  sim_tick += 1;
  sim_ppcalled = ch;
  sim_calltype = SIM_CALLTYPE_PPCALL;
  sim_reply_label = sel4cp_msginfo_get_label(msginfo);
  return simulate();
}

seL4_MessageInfo_t seL4_Recv(uint64_t src, uint64_t *sender) { 
  sim_tick += 1;
  sim_calltype = SIM_CALLTYPE_RECV;
  sim_return_badge = 0;
  sel4cp_msginfo ret = simulate();

  *sender = sim_return_badge;
  sim_notified = 0;
  sim_irq_acked = 0;
  sim_ppcalled = 0;
  return ret;
};

seL4_MessageInfo_t seL4_ReplyRecv(uint64_t src, seL4_MessageInfo_t reply_tag, uint64_t *sender) { 
  sim_tick += 1;
  sim_calltype = SIM_CALLTYPE_REPLYRECV;
  sim_reply_label = sel4cp_msginfo_get_label(reply_tag);
  sim_return_badge = 0;
  sel4cp_msginfo ret = simulate();

  *sender = sim_return_badge;
  sim_notified = 0;
  sim_irq_acked = 0;
  sim_ppcalled = 0;
  return ret;
};

/* User defined section */

extern uint64_t pinpad_input;
uint8_t sim_pinpad_input[1] = {0};

#ifdef LOCALSTATE
extern uint64_t local_state;
uint8_t sim_local_state[4096] = {0};
#endif

uint64_t sim_stage = 0;
uint64_t sim_irq_delay = 1000000;
uint64_t sim_next_digit = 5;

sel4cp_msginfo simulate() {
  // memory region simulation
  pinpad_input = (uint64_t)(&sim_pinpad_input);
#ifdef LOCALSTATE
  local_state = (uint64_t)(&sim_local_state);
#endif

  // no handling of sent ppcalls in the simulation
  if (sim_calltype == SIM_CALLTYPE_PPCALL) {
    return sel4cp_msginfo_new(0, 0);
  }

  // stage 0: client1 makes a ppcall
  if (sim_stage == 0) {
    sim_return_badge = 9223372036854775808ull; //ppcall
    sim_return_badge |= 1; // channel 1
    sim_stage = 1;
  }

  // stage 1: client1 waits for positive response
  if (sim_stage == 1) {
    if (sim_reply_label == 1) {
      sim_stage = 2;
    }
  }

  // stage 2: user enters PIN (generates IRQs)
  if (sim_stage == 2) {
    if (sim_irq_delay > 1) sim_irq_delay--;

    if (sim_irq_delay == 1) {
      sim_irq_delay = 0;
      sim_pinpad_input[0] = sim_next_digit;
      sim_return_badge = 0; // notification
      sim_return_badge |= 1; // channel 0
    }

    if (sim_irq_delay == 0) {
      // keep IRQ masked
      // unmask if acked
      if (sim_irq_acked & 1) {
        sim_next_digit--;
        // large delay for typing the next character
        sim_irq_delay = 5000000;
      }
    }

    if (sim_next_digit < 2) {
      sim_stage = 3;
    }
  }

  // stage 3: client 1 awaits notification
  // and then client2 makes ppcall
  if (sim_stage == 3) {
    if (sim_notified & 2) {
      sim_return_badge = 9223372036854775808ull; //ppcall
      sim_return_badge |= 2; // channel 2
      sim_stage = 4;
      sim_reply_label = 0;
    }
  }

  // stage 4: client2 waits for positive response
  if (sim_stage == 4) {
    debug = 1;
    if (sim_reply_label == 1) {
      sim_irq_delay = 10000;
      sim_next_digit = 5;
      sim_stage = 5;
    }
  }

  // stage 5: user enters PIN (generates IRQs)
  //  while client 1 tries to screw things up
  if (sim_stage == 5) {
    debug = 0;
    if (sim_irq_delay > 1) sim_irq_delay--;

    if (sim_irq_delay == 100) {
        sim_return_badge = 9223372036854775808ull; //ppcall
        sim_return_badge |= 1; // channel 1
    }

    if (sim_irq_delay == 1) {
      sim_irq_delay = 0;
      sim_pinpad_input[0] = sim_next_digit;
      sim_return_badge = 0; // notification
      sim_return_badge |= 1; // channel 0
    }

    if (sim_irq_delay == 0) {
      // keep IRQ masked
      // unmask if acked
      if (sim_irq_acked & 1) {
        sim_next_digit--;
        // large delay for typing the next character
        sim_irq_delay = 7500000;
      }
    }

    if (sim_next_digit < 2) {
      sim_stage = 6;
    }
  }

  // stage 6: hang forever

  return sel4cp_msginfo_new(0, 0);
}
