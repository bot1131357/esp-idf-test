/* LEDC (LED Controller) fade example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/ledc.h"
#include "esp_err.h"

/*
 * About this example
 *
 * For testing bandwidth using led controller 
 * peripheral to generate square wave signal
 * 
 * Set LEDC_TIMER_FREQ to desired frequency for testing 
 * 
 */
#define LEDC_TIMER_FREQ         800000
#define LEDC_TIMER_RES         1
#define LEDC_HS_TIMER1          LEDC_TIMER_0
#define LEDC_HS_MODE           LEDC_HIGH_SPEED_MODE
#define LEDC_HS_CH0_GPIO       (25)
#define LEDC_HS_CH0_CHANNEL    LEDC_CHANNEL_0

#define LEDC_TEST_CH_NUM       (1)
#define LEDC_MAX_DUTY         1 // ((1<<LEDC_TIMER_RES)-1)
#define LEDC_TEST_DUTY         1 //(LEDC_MAX_DUTY>>1)
#define LEDC_TEST_DELAY_TIME    (3000)


void setDuty(ledc_channel_config_t ledc_channel[LEDC_TEST_CH_NUM], uint32_t v)
{
		ledc_set_duty_and_update(ledc_channel[0].speed_mode, ledc_channel[0].channel, 
			v, ledc_channel[0].hpoint);
}
void app_main(void)
{
    int ch;

    /*
     * Prepare and set configuration of timers
     * that will be used by LED Controller
     */
    ledc_timer_config_t ledc_timer = {
        .duty_resolution = LEDC_TIMER_RES, // resolution of PWM duty
        .freq_hz = LEDC_TIMER_FREQ,                      // frequency of PWM signal
        .speed_mode = LEDC_HS_MODE,           // timer mode
        .timer_num = LEDC_HS_TIMER1,            // timer index
        .clk_cfg = LEDC_AUTO_CLK,              // Auto select the source clock
    };
    // Set configuration of timer0 for high speed channels
    ledc_timer_config(&ledc_timer);
    /*
     * Prepare individual configuration
     * for each channel of LED Controller
     * by selecting:
     * - controller's channel number
     * - output duty cycle, set initially to 0
     * - GPIO number where LED is connected to
     * - speed mode, either high or low
     * - timer servicing selected channel
     *   Note: if different channels use one timer,
     *         then frequency and bit_num of these channels
     *         will be the same
     */
    ledc_channel_config_t ledc_channel[LEDC_TEST_CH_NUM] = {
        {
            .channel    = LEDC_HS_CH0_CHANNEL,
            .duty       = 0,
            .gpio_num   = LEDC_HS_CH0_GPIO,
            .speed_mode = LEDC_HS_MODE,
            .hpoint     = 0,
            .timer_sel  = LEDC_HS_TIMER1
        },
    };

    // Set LED Controller with previously prepared configuration
    for (ch = 0; ch < LEDC_TEST_CH_NUM; ch++) {
        ledc_channel_config(&ledc_channel[ch]);
    }

    // Initialize fade service.
    // Note that the example doesn't work without this even if no fading is used - despite not mentioning in doc
    // E (324) ledc: Fade service not installed, call ledc_fade_func_install
    // E (334) ledc: ledc_set_duty_and_update(848): LEDC fade channel init error, not enough memory or service not installed    
    ledc_fade_func_install(0); 

    printf("LEDC set to on\n");
    setDuty(ledc_channel,LEDC_TEST_DUTY);

    while (1) {
        vTaskDelay(LEDC_TEST_DELAY_TIME / portTICK_PERIOD_MS);
    }
}
