/* MCPWM basic config example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/

#include <stdio.h>
// #include <stdlib.h>
#include "string.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_attr.h"
#include "soc/rtc.h"
#include "driver/mcpwm.h"
#include "soc/mcpwm_periph.h"
#include "esp_task_wdt.h"

#define GPIO_PWM0A_OUT 19   // Pin output - connect to Triac gate
#define GPIO_SYNC0_IN   2   // Pin input - connect to ZC circuit

static void mcpwm_example_gpio_initialize(void)
{
    printf("initializing mcpwm gpio...\n");
    mcpwm_gpio_init(MCPWM_UNIT_0, MCPWM0A, GPIO_PWM0A_OUT);
    mcpwm_gpio_init(MCPWM_UNIT_0, MCPWM_SYNC_0, GPIO_SYNC0_IN); // need to modify esp_rom_gpio_connect_in_signal in components/drivers/mcpwm.c
    gpio_pulldown_en(GPIO_SYNC0_IN);   //Enable pull down on SYNC0  signal
}

/**
 * @brief Set gpio 12 as our test signal that generates high-low waveform continuously, connect this gpio to capture pin.
 */
static void gpio_test_signal(void *arg)
{
    printf("intializing test signal...\n");
    gpio_config_t gp;
    gp.intr_type = GPIO_INTR_DISABLE;
    gp.mode = GPIO_MODE_OUTPUT;
    gp.pin_bit_mask = GPIO_SEL_12;
    gpio_config(&gp);
    while (1) {
        // static int x = 0;
        {
            // ++x;
            gpio_set_level(GPIO_NUM_12, 1);  
            vTaskDelay(10 / portTICK_PERIOD_MS);            
            gpio_set_level(GPIO_NUM_12, 0); 
            vTaskDelay(10 / portTICK_PERIOD_MS);    

            // simulating fluctuation
            // vTaskDelay(4/ portTICK_RATE_MS);        
            // vTaskDelay(8/ portTICK_RATE_MS);   

            // esp_task_wdt_reset();     
        }
    }
}

/**
 * @brief Configure whole MCPWM module
 */
static void mcpwm_example_config(void *arg)
{
    // mcpwm gpio initialization
    mcpwm_example_gpio_initialize();

    // initialize mcpwm configuration
    printf("Configuring Initial Parameters of mcpwm...\n");
    mcpwm_config_t pwm_config;
    pwm_config.frequency = 100;    //frequency = 100Hz , double of AC 50Hz since we drive for two halves of the waveform 
    // pwm_config.frequency = 200;    // doubled to 200Hz for symmetric up-down counter
    pwm_config.cmpr_a = 50.0;       //duty cycle of PWMxA = 50.0%
    // pwm_config.counter_mode = MCPWM_UP_DOWN_COUNTER;
    pwm_config.counter_mode = MCPWM_DOWN_COUNTER;
    // pwm_config.counter_mode = MCPWM_UP_COUNTER;
    pwm_config.duty_mode = MCPWM_DUTY_MODE_0; // active high
    // pwm_config.duty_mode = MCPWM_DUTY_MODE_1; // active low
    mcpwm_init(MCPWM_UNIT_0, MCPWM_TIMER_0, &pwm_config);   //Configure PWM0A & PWM0B with above settings

    // Syncronization configuration
        // mcpwm_sync_enable(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM_SELECT_SYNC0, 0); // % phase offset
        // mcpwm_sync_enable(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM_SELECT_SYNC0, 250); // % phase offset
        // mcpwm_sync_enable(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM_SELECT_SYNC0, 500); // % phase offset
        mcpwm_sync_enable(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM_SELECT_SYNC0, 850); // % phase offset
    // mcpwm_sync_enable(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM_SELECT_SYNC0, 950); // 95% phase offset
    
    const int MIN_PWM_DUTY = 0; // 14% on refboard 
    const int MAX_PWM_DUTY = 70; // 75% on refboard

    // vary duty cycle 
    float x = 50;
    float delta = .1;
    for(;;)
    {
        if(MAX_PWM_DUTY<x) delta = -.1;
        else if(MIN_PWM_DUTY>x) delta = .1;
        
        // mcpwm_set_duty(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM0A, MIN_PWM_DUTY);
        mcpwm_set_duty(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM0A, x);
        
        vTaskDelay(5 / portTICK_PERIOD_MS);            
        x+=delta;

        if(0==x || MAX_PWM_DUTY==x) vTaskDelay(1000 / portTICK_PERIOD_MS);     
        // esp_task_wdt_reset();  
    }

//     // vary phase offset
//     for(;;)
//     {
//         mcpwm_set_duty(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM0A, MIN_PWM_DUTY);

//         mcpwm_sync_enable(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM_SELECT_SYNC0, 0); // % phase offset
//         vTaskDelay(3000 / portTICK_PERIOD_MS); 
//         mcpwm_sync_enable(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM_SELECT_SYNC0, 250); // % phase offset
//         vTaskDelay(3000 / portTICK_PERIOD_MS); 
//         mcpwm_sync_enable(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM_SELECT_SYNC0, 500); // % phase offset
//         vTaskDelay(3000 / portTICK_PERIOD_MS); 
//         mcpwm_sync_enable(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM_SELECT_SYNC0, 750); // % phase offset
//         vTaskDelay(3000 / portTICK_PERIOD_MS); 

//         //rest
//         mcpwm_set_duty(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM0A, 0);
//         vTaskDelay(3000 / portTICK_PERIOD_MS); 
//     }

//     vTaskDelete(NULL);
}

void app_main(void)
{
    printf("Testing MCPWM for Triac control...\n");

    // xTaskCreate(gpio_test_signal, "gpio_test_signal", 4096, NULL, 5, NULL);
    xTaskCreatePinnedToCore(gpio_test_signal, "gpio_test_signal", 4096, NULL, 5, NULL, 0); // pin to core 0
    xTaskCreate(mcpwm_example_config, "mcpwm_example_config", 4096, NULL, 5, NULL);
}

