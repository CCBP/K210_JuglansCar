#include <Arduino.h>
#include <ArduinoJson.h>
#include <WiFi.h>
#include <SPIFFS.h>

#include "web_server.h"
#include "spi_dma_slave.h"

const char *ssid = "****";
const char *password = "****";

void setup()
{
  // 运行指示灯
  pinMode(2, OUTPUT);
  digitalWrite(2, LOW);

  Serial.begin(115200);
  Serial2.begin(5000000); // RX:GPIO16  TX:GPIO17
  Serial2.setRxBufferSize(4096);

  // SPIFFS 初始化
  if (!SPIFFS.begin(true))
  {
    Serial.println("[E] SPIFFS initialization failed");
    while (true)
      delay(1);
  }
  Serial.println("[I] SPIFFS initialized");

  // WiFi 初始化
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.printf("[I] WiFi [%s|%s] Connecting ", ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    delay(1000);
  }
  Serial.println(" success");
  IPAddress ip = WiFi.localIP();
  char ip_address[15];
  strcpy(ip_address, ip.toString().c_str());
  Serial.printf("[I] WiFi IP address: %s\n", ip_address);

  web_server_init();
  video_server_init();
  digitalWrite(2, HIGH); // 初始化结束
}

void loop()
{
  web_socket_cleanup();
}