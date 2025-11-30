#ifndef GPIO_DMA_H
#define GPIO_DMA_H
#include <stdint.h>
typedef struct { uint32_t num_channels, sample_rate, duration_samples, pretrigger_samples; uint8_t trigger_channel, trigger_type; uint32_t gpio_mask; } capture_config_t;
int gpio_dma_init(void);
int gpio_dma_configure(capture_config_t *cfg);
int gpio_dma_start_capture(void);
void gpio_dma_cleanup(void);
#endif
