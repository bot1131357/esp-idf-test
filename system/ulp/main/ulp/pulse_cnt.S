/* ULP Example: pulse counting

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.

   This file contains assembly code which runs on the ULP.

   ULP wakes up to run this code at a certain period, determined by the values
   in SENS_ULP_CP_SLEEP_CYCx_REG registers. On each wake up, the program checks
   the input on GPIO0. If the value is different from the previous one, the
   program "debounces" the input: on the next debounce_max_count wake ups,
   it expects to see the same value of input.
   If this condition holds true, the program increments edge_count and starts
   waiting for input signal polarity to change again.
   When the edge counter reaches certain value (set by the main program),
   this program running triggers a wake up from deep sleep.
*/

/* ULP assembly files are passed through C preprocessor first, so include directives
   and C macros may be used in these files
 */
#include "soc/rtc_cntl_reg.h"
#include "soc/rtc_io_reg.h"
#include "soc/soc_ulp.h"

.macro set_gpio2
	WRITE_RTC_REG(RTC_GPIO_OUT_W1TS_REG, RTC_GPIO_OUT_DATA_W1TS_S + 12, 1, 1)	// GPIO2 is RTC_GPIO12
.endm

.macro clear_gpio2
	WRITE_RTC_REG(RTC_GPIO_OUT_W1TC_REG, RTC_GPIO_OUT_DATA_W1TC_S + 12, 1, 1)
.endm

	/* Define variables, which go into .bss section (zero-initialized data) */
	.bss
	
	/* Test variable */
	.global test_val
test_val:
	.long 0

	/* Next input signal edge expected: 0 (negative) or 1 (positive) */
	.global next_edge
next_edge:
	.long 0

	/* Counter started when signal value changes.
	   Edge is "debounced" when the counter reaches zero. */
	.global debounce_counter
debounce_counter:
	.long 0

	/* Value to which debounce_counter gets reset.
	   Set by the main program. */
	.global debounce_max_count
debounce_max_count:
	.long 0

	/* Total number of signal edges acquired */
	.global edge_count
edge_count:
	.long 0

	/* Number of edges to acquire before waking up the SoC.
	   Set by the main program. */
	.global edge_count_to_wake_up
edge_count_to_wake_up:
	.long 0

	/* RTC IO number used to sample the input signal.
	   Set by main program. */
	.global io_number
io_number:
	.long 0

	/* RTC IO number used to sample the output signal.
	   Set by main program. */
	.global io_number_out
io_number_out:
	.long 0

	/* Code goes into .text section */
	.text
	.global entry
entry:
	// first time only
	// for some reason GPIO out doesn't work until the ESP32 wakes up at least once?
	move r1, test_val
	ld r0, r1, 0
	jumpr move_along, 5, gt
	add r0, r0, 1
	st r0, r1, 0
	jump wake_up // wake up
	
	.global move_along
move_along:
	/* Load io_number */
	move r3, io_number 	// load address
	ld r3, r3, 0		// load value stored in address

	/* Random code that generates some square waves */
	move r0, 0
	// move r1, io_number_out
	// ld r1, r1, 0
just_random_gpio_out:
	add r0, r0, 1	// increment
	// about 120 ns high and 120ns low
	set_gpio2
	WAIT     500 
	clear_gpio2
	WAIT     500 
	jumpr just_random_gpio_out, 5, lt // repeat if R0<5

	/* Lower 16 IOs and higher need to be handled separately,
	 * because r0-r3 registers are 16 bit wide.
	 * Check which IO this is.
	 */
	move r0, r3
	jumpr read_io_high, 16, ge

	/* Read the value of lower 16 RTC IOs into R0 */
	READ_RTC_REG(RTC_GPIO_IN_REG, RTC_GPIO_IN_NEXT_S, 16)	// 16 bits
	rsh r0, r0, r3
	jump read_done

	/* Read the value of RTC IOs 16-17, into R0 */
read_io_high:
	READ_RTC_REG(RTC_GPIO_IN_REG, RTC_GPIO_IN_NEXT_S + 16, 2)	// only two bits 
	sub r3, r3, 16	// r3 = r3-16
	rsh r0, r0, r3

read_done:
	and r0, r0, 1
	/* State of input changed? */
	move r3, next_edge	// r3 = &next_edge
	ld r3, r3, 0		// r3 = next_edge
	add r3, r0, r3		// r3 = r0 + r3
	and r3, r3, 1		// r3 = r3 & 1
	jump changed, eq	// if last bit equal, jump
	/* Not changed */
	/* Reset debounce_counter to debounce_max_count */
	move r3, debounce_max_count
	move r2, debounce_counter
	ld r3, r3, 0		// r3 = debounce_max_count
	st r3, r2, 0		// *debounce_counter = r3 (why?)
	/* End program */
	halt

	.global changed
changed:
	/* Input state changed */
	/* Has debounce_counter reached zero? */
	move r3, debounce_counter
	ld r2, r3, 0
	add r2, r2, 0 /* dummy ADD to use "jump if ALU result is zero" */
	jump edge_detected, eq
	/* Not yet. Decrement debounce_counter */
	sub r2, r2, 1
	st r2, r3, 0
	/* End program */
	halt

	.global edge_detected
edge_detected:
	/* Reset debounce_counter to debounce_max_count */
	move r3, debounce_max_count
	move r2, debounce_counter
	ld r3, r3, 0
	st r3, r2, 0
	/* Flip next_edge */
	move r3, next_edge
	ld r2, r3, 0
	add r2, r2, 1
	and r2, r2, 1
	st r2, r3, 0
	/* Increment edge_count */
	move r3, edge_count
	ld r2, r3, 0
	add r2, r2, 1
	st r2, r3, 0
	/* Compare edge_count to edge_count_to_wake_up */
	move r3, edge_count_to_wake_up
	ld r3, r3, 0
	sub r3, r3, r2
	jump wake_up, eq
	/* Not yet. End program */
	halt
