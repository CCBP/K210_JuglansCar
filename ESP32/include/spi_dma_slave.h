#ifndef _SPI_DMA_SLAVE_H_
#define _SPI_DMA_SLAVE_H_

#include <Arduino.h>
#include <ESP32DMASPISlave.h>
#include <ArduinoJson.h>

#include "web_server.h"

#define SPI_BUFFER_SIZE 4096

struct IMAGE
{
    uint16_t width = 320;
    uint16_t high = 240;
    uint16_t len = 0;
    float fps = 0;
    uint8_t *frame;
};
extern IMAGE image;

struct SPI_TX
{
    bool state = false;
    String drive = "";
    uint8_t *buf;
};
extern SPI_TX spi_tx;

#define WEB_CONNECT true
#define WEB_DISCONNECT false

bool spi_wait_write(uint8_t *tx_buf, const size_t size);
bool spi_wait_read(uint8_t *rx_buf, const size_t size);
bool spi_wait(uint8_t *rx_buf, uint8_t *tx_buf, const size_t size);
bool spi_readwrite(uint8_t *rx_buf, uint8_t *tx_buf, const size_t size);
bool spi_write(uint8_t *tx_buf, const size_t size);
uint8_t *spi_alloc_dma_buf(size_t size);

void spi_updata(void);
bool spi_init(void);
bool spi_init(size_t size);

extern bool block;
bool _spi_block(uint16_t time = 1000);
#define SPI_BLOCK(callback) \
    if (_spi_block())       \
        return;             \
    block = true;           \
    callback;               \
    block = false;
uint8_t spi_print(String tag, uint8_t *msg,
                  uint16_t max_len = 128, String end = "\n");

#endif