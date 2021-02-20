/* ULP assembly files are passed through C preprocessor first, so include directives
   and C macros may be used in these files
 */
#include "soc/rtc_cntl_reg.h"
#include "soc/soc_ulp.h"

// this is called every 5 presses
	.global wake_up
wake_up:
// do something random
	move r1, test_val
	ld r0, r1, 0
	add r0, r0, 1
	st r0, r1, 0

	/* Check if the system can be woken up */
	READ_RTC_FIELD(RTC_CNTL_LOW_POWER_ST_REG, RTC_CNTL_RDY_FOR_WAKEUP)	// read to R0
	and r0, r0, 1		// check if ESP32 ready to wake up (R0 = R0 & 1)
	jump wake_up, eq	// if R0&1 == 0, repeat eheck 

	/* Wake up the SoC, end program */
	wake
	halt
