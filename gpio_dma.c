#include "gpio_dma.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <time.h>
#define GPIO_BASE 0x3F200000
#define GPLEV0 13
static volatile uint32_t *gpio=NULL; static int fd=-1; static uint8_t *buf=NULL; static uint32_t bufsz=0; static capture_config_t cfg;
int gpio_dma_init(void){fd=open("/dev/mem",O_RDWR|O_SYNC);if(fd<0){perror("open");return -1;}void*m=mmap(NULL,4096,PROT_READ|PROT_WRITE,MAP_SHARED,fd,GPIO_BASE);if(m==MAP_FAILED){perror("mmap");close(fd);return -1;}gpio=(volatile uint32_t*)m;printf("[+] GPIO OK\n");return 0;}
int gpio_dma_configure(capture_config_t *c){memcpy(&cfg,c,sizeof(cfg));bufsz=c->duration_samples+c->pretrigger_samples;buf=malloc(bufsz*2);if(!buf){perror("malloc");return -1;}printf("[+] Config: %dch %dHz\n",c->num_channels,c->sample_rate);return 0;}
int gpio_dma_start_capture(void){if(!gpio||!buf)return -1;uint32_t ns=1000000000/cfg.sample_rate;struct timespec ts={0,ns};uint8_t last=0;int trig=0;uint32_t i=0;printf("[*] Waiting trigger...\n");while(i<bufsz){uint32_t st=gpio[GPLEV0];uint16_t s=(uint16_t)(st&0xFFFF);uint8_t b=(s>>cfg.trigger_channel)&1;if(!trig){if(cfg.trigger_type==2&&last&&!b)trig=1;else if(cfg.trigger_type==1&&!last&&b)trig=1;last=b;if(trig)printf("[+] Trigger!\n");else{nanosleep(&ts,NULL);continue;}}buf[i*2]=s&0xFF;buf[i*2+1]=(s>>8)&0xFF;i++;nanosleep(&ts,NULL);}printf("[+] Done: %d samples\n",i);return 0;}
void gpio_dma_cleanup(void){if(buf)free(buf);if(gpio)munmap((void*)gpio,4096);if(fd>=0)close(fd);}
int main(int c,char**v){if(c<2){printf("Usage: %s <out.bin>\n",v[0]);return 1;}if(gpio_dma_init()<0)return 1;capture_config_t cf={8,1000000,1000000,100000,0,2,0xFFFF};if(gpio_dma_configure(&cf)<0){gpio_dma_cleanup();return 1;}gpio_dma_start_capture();FILE*f=fopen(v[1],"wb");if(f){fwrite(&cf,sizeof(cf),1,f);fwrite(buf,bufsz*2,1,f);fclose(f);}printf("[+] Saved: %s\n",v[1]);gpio_dma_cleanup();return 0;}
