#ifndef _WEB_SERVER_
#define _WEB_SERVER_

// 服务器监听端口
#define SERVER_PORT 80

#include <WiFi.h>
#include <WebServer.h>
#include "ESPAsyncWebServer.h"
#include "SPIFFS.h"

// #include "spi_dma_slave.h"

#define CONNECT_STATE 0

void video_server_init(void);
void web_server_init(void);
void web_socket_cleanup(void);

#endif