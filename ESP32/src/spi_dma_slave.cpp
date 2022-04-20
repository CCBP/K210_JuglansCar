#include "spi_dma_slave.h"

ESP32DMASPI::Slave spi;

uint16_t MAX_SIZE = SPI_BUFFER_SIZE;

IMAGE image;
SPI_TX spi_tx;

uint8_t *spi_rx_buf;
uint8_t *spi_tx_buf;
bool block = false;

bool spi_wait_write(uint8_t *tx_buf, const size_t size)
{
    return spi.wait(NULL, tx_buf, size);
}

bool spi_wait_read(uint8_t *rx_buf, const size_t size)
{
    return spi.wait(rx_buf, size);
}

bool spi_wait(uint8_t *rx_buf, uint8_t *tx_buf, const size_t size)
{
    return spi.wait(rx_buf, tx_buf, size);
}

bool spi_readwrite(uint8_t *rx_buf, uint8_t *tx_buf, const size_t size)
{
    return spi.queue(rx_buf, tx_buf, size);
}

bool spi_read(uint8_t *rx_buf, const size_t size)
{
    return spi.queue(rx_buf, size);
}

bool spi_write(uint8_t *tx_buf, const size_t size)
{
    return spi.queue(NULL, tx_buf, size);
}

uint8_t *spi_alloc_dma_buf(size_t size)
{
    return spi.allocDMABuffer(size);
}

bool _spi_block(uint16_t time)
{
    while (block && time--)
        delay(1);

    if (!time)
    {
        Serial.println("[E] SPI block time out");
        return true;
    }
    return false;
}

uint8_t spi_print(String tag, uint8_t *msg, uint16_t max_len, String end)
{
    Serial.print(tag);
    uint16_t i;
    for (i = 0; msg[i] != '\0' && i < max_len; i++)
    {
        Serial.printf("%c", msg[i]);
    }
    Serial.print(end);
    return i;
}

bool spi_buf_serialization(uint8_t *buf)
{
    StaticJsonDocument<SPI_BUFFER_SIZE> json;
    json["state"] = spi_tx.state;
    json["drive"] = spi_tx.drive;
    serializeJson(json, buf, measureJson(json) + 1);
    // Serial.printf("[D] Serialization: %s\n", buf);
    return true;
}

bool spi_buf_deserialization(uint8_t *buf)
{
    StaticJsonDocument<SPI_BUFFER_SIZE> json;
    DeserializationError error = deserializeJson(json, buf);
    if (error)
    {
        spi_print("[E] SPI massage: ", buf);
        Serial.print("[E] Json deserialize failed :");
        Serial.println(error.c_str());
        return false;
    }
    JsonObject root = json.as<JsonObject>();
    if (root.containsKey("len"))
    {
        image.len = root.getMember("len");
        Serial.printf("[D] Image length: %d\n", image.len);
    }

    return true;
}

void spi_updata(void)
{
    if (spi.remained() == 0)
    {
        if (_spi_block())
            return;
        block = true;
        spi_buf_serialization(spi_tx_buf);
        spi.queue(spi_rx_buf, spi_tx_buf, MAX_SIZE);
        spi.queue(image.frame, MAX_SIZE);
        // spi_print("[D] SPI massage: ", spi_rx_buf);
        spi_buf_deserialization(spi_rx_buf);
        block = false;
    }
}

/**
 * @brief SPI 初始化
 */
bool spi_init(void)
{
    return spi_init(MAX_SIZE);
}

bool spi_init(size_t size)
{
    if (size > SPI_BUFFER_SIZE)
    {
        Serial.printf("[E] spi_init: declare size \'%d\' out of SPI_BUFFER_SIZE\n", size);
        return false;
    }
    MAX_SIZE = size;
    spi_rx_buf = spi.allocDMABuffer(size);
    spi_tx_buf = spi.allocDMABuffer(size);
    image.frame = spi.allocDMABuffer(size);
    spi.setDataMode(SPI_MODE0);
    spi.setMaxTransferSize(size);
    spi.setDMAChannel(1);
    /* HSPI = CS: 15, CLK: 14, MOSI: 13, MISO: 12 -> default
     * VSPI = CS:  5, CLK: 18, MOSI: 23, MISO: 19 */
    spi.begin();
    spi.remained();

    return ESP_OK;
}