#include "web_server.h"

// 在 80 端口创建 Web Server 对象
AsyncWebServer server(SERVER_PORT);
// 创建 Web Socket 对象
AsyncWebSocket wsDrive("/wsDrive");
AsyncWebSocket wsCalibrate("/wsCalibrate");
AsyncWebSocket wsTest("/wsTest");

#define VIDEO_PORT 81

uint32_t frame_last_time = 0;

bool receive_blank_line(WiFiClient &client, String &req_str)
{
  // Serial.println(req_str);
  req_str = "";
  uint32_t time_out = millis();
  while (true)
  {
    if (client.available())
    {
      req_str = client.readStringUntil('\n');
      // Serial.println(req_str);
      if (req_str.indexOf("\r") == 0)
        return true;
    }
    if (millis() - time_out > 10000)
    {
      Serial.println("[E] Receive to blank line time out");
      break;
    }
    delay(1);
  }
  return false;
}

void video_handler(void *pvParam)
{
  WiFiServer video_server(VIDEO_PORT);
  video_server.begin();
  while (true)
  {
    WiFiClient video_client = video_server.available();

    while (video_client.available())
    {
      String req_str = video_client.readStringUntil('\n');
      if (req_str.indexOf("/video") >= 0)
      {
        Serial.println("[I] Video handler on streaming");
        if (!receive_blank_line(video_client, req_str))
          break;
        const char boundary[] = "--frame";
        String response = "HTTP/1.1 200 OK\r\n";
        response += "Access-Control-Allow-Origin: *\r\n";
        response += "Content-type: multipart/x-mixed-replace;boundary=";
        response += boundary;
        response += "\r\n\r\n";
        video_client.print(response);

        delay(10);
        while (true)
        {
          delay(1);
          // if (image.len == 0)
          //   continue;
          // response = "--frame\r\n";
          // response += "Access-Control-Allow-Origin: *\r\n";
          // response += "Content-Type: image/jpeg\r\n\r\n";
          // response += "Content-Length: " + String(image.len);

          // video_client.print(response);
          // video_client.write(image.frame, image.len);

          // video_client.print("\r\n");

          uint8_t frame = 0;
          uint16_t feed_dog = 0;
          while (Serial2.available())
          {
            if (Serial2.peek() == boundary[frame] && frame < sizeof(boundary))
            {
              if (++frame == sizeof(boundary)) // 完成一帧图像的传输
              {
                float fps = 1000.0 / (millis() - (float)frame_last_time);
                Serial.printf("[I] Frame send [%.02lf(fps)]\n", fps);
                frame_last_time = millis();
                frame = 0;
              }
            }
            video_client.write(Serial2.read());
            if (++feed_dog >= 1024)
            {
              delay(1);
              feed_dog = 0;
            }
          }

          if (!video_client.connected())
            break;
        }
      }
      delay(1);
    }
    delay(1);
  }
}

void video_server_init(void)
{
  TaskHandle_t task;
  if (!xTaskCreatePinnedToCore(&video_handler, "video_handler",
                               9216, NULL, 24, &task, 0))
  {
    Serial.println("[E] Failed to create video server task");
  }
  else
    Serial.printf("[I] Video server initialized, server port %d\n", VIDEO_PORT);
}

void wsDrive_handler(const String &var)
{
  Wire.beginTransmission(0x24);
  Wire.write(var.c_str());
  Wire.endTransmission();
}

void wsCalibrate_handler(const String &var)
{
  // Serial.println("wsCalibrate_handler");
  // Serial.println(var);
}

String web_socket_massage_handler(AsyncWebSocket *server, AsyncWebSocketClient *client,
                                  void *arg, uint8_t *data, size_t len)
{
  AwsFrameInfo *info = (AwsFrameInfo *)arg;
  String msg = "";
  if (info->final && info->index == 0 && info->len == len)
  {
    // the whole message is in a single frame and we got all of it's data
    Serial.printf("ws[%s][%u] %s-message[%llu]: ", server->url(), client->id(),
                  (info->opcode == WS_TEXT) ? "text" : "binary", info->len);

    if (info->opcode == WS_TEXT)
    {
      for (size_t i = 0; i < info->len; i++)
      {
        msg += (char)data[i];
      }
    }
    else
    {
      char buff[3];
      for (size_t i = 0; i < info->len; i++)
      {
        sprintf(buff, "%02x ", (uint8_t)data[i]);
        msg += buff;
      }
    }
    Serial.printf("%s\n", msg.c_str());
  }
  else
  {
    // message is comprised of multiple frames or the frame is split into multiple packets
    if (info->index == 0)
    {
      if (info->num == 0)
        Serial.printf("ws[%s][%u] %s-message start\n", server->url(), client->id(),
                      (info->message_opcode == WS_TEXT) ? "text" : "binary");
      Serial.printf("ws[%s][%u] frame[%u] start[%llu]\n", server->url(),
                    client->id(), info->num, info->len);
    }

    Serial.printf("ws[%s][%u] frame[%u] %s[%llu - %llu]: ",
                  server->url(), client->id(), info->num,
                  (info->message_opcode == WS_TEXT) ? "text" : "binary",
                  info->index, info->index + len);

    if (info->opcode == WS_TEXT)
    {
      for (size_t i = 0; i < len; i++)
      {
        msg += (char)data[i];
      }
    }
    else
    {
      char buff[3];
      for (size_t i = 0; i < len; i++)
      {
        sprintf(buff, "%02x ", (uint8_t)data[i]);
        msg += buff;
      }
    }
    Serial.printf("%s\n", msg.c_str());

    if ((info->index + len) == info->len)
    {
      Serial.printf("ws[%s][%u] frame[%u] end[%llu]\n", server->url(), client->id(), info->num, info->len);
      if (info->final)
      {
        Serial.printf("ws[%s][%u] %s-message end\n", server->url(), client->id(),
                      (info->message_opcode == WS_TEXT) ? "text" : "binary");
      }
    }
  }
  return msg;
}

void not_found_handler(AsyncWebServerRequest *request)
{
  Serial.printf("Not found: ");
  if (request->method() == HTTP_GET)
    Serial.printf("GET");
  else if (request->method() == HTTP_POST)
    Serial.printf("POST");
  else if (request->method() == HTTP_DELETE)
    Serial.printf("DELETE");
  else if (request->method() == HTTP_PUT)
    Serial.printf("PUT");
  else if (request->method() == HTTP_PATCH)
    Serial.printf("PATCH");
  else if (request->method() == HTTP_HEAD)
    Serial.printf("HEAD");
  else if (request->method() == HTTP_OPTIONS)
    Serial.printf("OPTIONS");
  else
    Serial.printf("UNKNOWN");
  Serial.printf(" http://%s%s\n", request->host().c_str(), request->url().c_str());

  if (request->contentLength())
  {
    Serial.printf("_CONTENT_TYPE: %s\n", request->contentType().c_str());
    Serial.printf("_CONTENT_LENGTH: %u\n", request->contentLength());
  }

  int headers = request->headers();
  int i;
  for (i = 0; i < headers; i++)
  {
    AsyncWebHeader *h = request->getHeader(i);
    Serial.printf("_HEADER[%s]: %s\n", h->name().c_str(), h->value().c_str());
  }

  int params = request->params();
  for (i = 0; i < params; i++)
  {
    AsyncWebParameter *p = request->getParam(i);
    if (p->isFile())
    {
      Serial.printf("_FILE[%s]: %s, size: %u\n", p->name().c_str(), p->value().c_str(), p->size());
    }
    else if (p->isPost())
    {
      Serial.printf("_POST[%s]: %s\n", p->name().c_str(), p->value().c_str());
    }
    else
    {
      Serial.printf("_GET[%s]: %s\n", p->name().c_str(), p->value().c_str());
    }
  }

  request->send(404);
}

void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client,
             AwsEventType type, void *arg, uint8_t *data, size_t len)
{
  String msg = "";
  switch (type)
  {
  case WS_EVT_CONNECT:
    digitalWrite(CONNECT_STATE, HIGH);
    Serial.printf("ws[%s][%u] connect\n", server->url(), client->id());
    break;
  case WS_EVT_DISCONNECT:
    digitalWrite(CONNECT_STATE, LOW);
    Serial.printf("ws[%s][%u] disconnect\n", server->url(), client->id());
    break;
  case WS_EVT_DATA:
    Serial.printf("ws[%s][%u] received data\n", server->url(), client->id());
    msg += web_socket_massage_handler(server, client, arg, data, len);
    if (strcmp(server->url(), "/wsDrive") == 0)
      wsDrive_handler(msg);
    else if (strcmp(server->url(), "/wsCalibrate") == 0)
      wsCalibrate_handler(msg);
    else
      Serial.printf("ws[%s][%u] handler not dound\n", server->url(), client->id());
    break;
  case WS_EVT_PONG:
    Serial.printf("ws[%s][%u] pong[%u]: %s\n", server->url(),
                  client->id(), len, (len) ? (char *)data : "");
    break;
  case WS_EVT_ERROR:
    Serial.printf("ws[%s][%u] error(%u): %s\n", server->url(), client->id(),
                  *((uint16_t *)arg), (char *)data);
    break;
  }
}

void web_server_init(void)
{
  // 客户端连接状态，与 K210 通信
  pinMode(CONNECT_STATE, OUTPUT);
  digitalWrite(CONNECT_STATE, LOW);

  // 配置路由
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request)
            { Serial.printf("Web Server[%s]\n", request->url().c_str());
              request->redirect("/drive"); });
  server.on("/favicon.ico", HTTP_GET, [](AsyncWebServerRequest *request)
            { Serial.printf("Web Server[%s]\n", request->url().c_str());
    request->send(404, "text/plain", "404 Not Found"); });
  // request->send(SPIFFS, "/favicon.ico", "image/ico"); });
  server.on("/drive", HTTP_GET, [](AsyncWebServerRequest *request)
            { Serial.printf("Web Server[%s]\n", request->url().c_str());
              request->send(SPIFFS, "/vehicle.html", String()); });
  server.on("/calibrate", HTTP_GET, [](AsyncWebServerRequest *request)
            { Serial.printf("Web Server[%s]\n", request->url().c_str());
              request->send(SPIFFS, "/calibrate.html", String()); });
  server.on("/wsTest", HTTP_GET, [](AsyncWebServerRequest *request)
            { Serial.printf("Web Server[%s]\n", request->url().c_str());
              request->send(SPIFFS, "/wsTest.html", String()); });
  server.on("^(\\/static\\/)+(.*)$", HTTP_GET, [](AsyncWebServerRequest *request)
            { Serial.printf("Web Server[%s]\n", request->url().c_str());
              request->send(SPIFFS, request->url(), String()); });
  server.onNotFound(not_found_handler);

  // Web Socket 配置
  wsDrive.onEvent(onEvent);
  server.addHandler(&wsDrive);
  wsCalibrate.onEvent(onEvent);
  server.addHandler(&wsCalibrate);
  wsTest.onEvent(onEvent);
  server.addHandler(&wsTest);

  server.begin();

  Serial.printf("[I] Web Server initialized, server port: %d\n", SERVER_PORT);
}

/**
 * @brief Limiting the number of web socket clients
 *
 * Browsers sometimes do not correctly close the websocket connection,
 * even when the close() function is called in javascript. This will
 * eventually exhaust the web server's resources and will cause the
 * server to crash. Periodically calling the cleanClients() function
 * from the main loop() function limits the number of clients by closing
 * the oldest client when the maximum number of clients has been exceeded.
 * This can called be every cycle, however, if you wish to use less power,
 * then calling as infrequently as once per second is sufficient.
 */
void web_socket_cleanup(void)
{
  wsDrive.cleanupClients();
  wsCalibrate.cleanupClients();
  wsTest.cleanupClients();
}