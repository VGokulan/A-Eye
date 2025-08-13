#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>
#include <ESP32Servo.h>
#include <Ultrasonic.h>

// === WiFi ===
const char* WIFI_SSID = "project12345";
const char* WIFI_PASS = "project12345"; 
WebServer server(80);

// === Camera Resolution Presets ===
static auto loRes = esp32cam::Resolution::find(320, 240);
static auto midRes = esp32cam::Resolution::find(350, 530);
static auto hiRes = esp32cam::Resolution::find(800, 600);

// === Pins ===
#define SERVO_PIN 13
#define TRIG_PIN 14
#define ECHO_PIN 12
#define BUZZER_PIN 15

Servo myServo;
Ultrasonic ultrasonic(TRIG_PIN, ECHO_PIN);

// === Camera Capture ===
void serveJpg()
{
  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("CAPTURE FAIL");
    server.send(503, "", "");
    return;
  }
  Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));

  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}

void handleJpgLo() {
  if (!esp32cam::Camera.changeResolution(loRes)) {
    Serial.println("SET-LO-RES FAIL");
  }
  serveJpg();
}

void handleJpgHi() {
  if (!esp32cam::Camera.changeResolution(hiRes)) {
    Serial.println("SET-HI-RES FAIL");
  }
  serveJpg();
}

void handleJpgMid() {
  if (!esp32cam::Camera.changeResolution(midRes)) {
    Serial.println("SET-MID-RES FAIL");
  }
  serveJpg();
}

// === MJPEG Stream ===
void handleStream()
{
  WiFiClient client = server.client();
  String responseHeader = "HTTP/1.1 200 OK\r\n"
                          "Content-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n";
  client.print(responseHeader);

  while (client.connected()) {
    auto frame = esp32cam::capture();
    if (frame == nullptr) {
      Serial.println("STREAM CAPTURE FAIL");
      continue;
    }

    client.print("--frame\r\n");
    client.print("Content-Type: image/jpeg\r\n");
    client.print("Content-Length: " + String(frame->size()) + "\r\n\r\n");
    frame->writeTo(client);
    client.print("\r\n");

    Serial.println("STREAM FRAME SENT");
    delay(100);
  }
}

// === Servo Control ===
void handleServoControl() {
  if (server.hasArg("value")) {
    int angle = server.arg("value").toInt();
    angle = constrain(angle, 0, 180);
    myServo.write(angle);
    Serial.printf("Servo angle set to %d\n", angle);
    server.send(200, "text/plain", "Servo moved");
  } else {
    server.send(400, "text/plain", "Missing angle value");
  }
}

// === Setup ===
void setup() {
  Serial.begin(115200);
  Serial.println();

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  myServo.attach(SERVO_PIN);

  // Camera init
  using namespace esp32cam;
  Config cfg;
  cfg.setPins(pins::AiThinker);
  cfg.setResolution(hiRes);
  cfg.setBufferCount(2);
  cfg.setJpeg(80);

  bool ok = Camera.begin(cfg);
  Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");

  // Wi-Fi
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  Serial.print("Stream URL: http://");
  Serial.println(WiFi.localIP());
  Serial.println("  /cam-lo.jpg");
  Serial.println("  /cam-hi.jpg");
  Serial.println("  /cam-mid.jpg");
  Serial.println("  /stream");
  Serial.println("  /servo_angle?value=90");

  // Routes
  server.on("/cam-lo.jpg", handleJpgLo);
  server.on("/cam-hi.jpg", handleJpgHi);
  server.on("/cam-mid.jpg", handleJpgMid);
  server.on("/stream", handleStream);
  server.on("/servo_angle", handleServoControl); // New route for servo control

  server.begin();
}

// === Loop: Ultrasonic + Buzzer ===
void loop()
{
  server.handleClient();

  long distance = ultrasonic.read();
  Serial.print("Distance: ");
  Serial.println(distance);

  if (distance > 0 && distance < 100) {
    digitalWrite(BUZZER_PIN, HIGH);
  } else {
    digitalWrite(BUZZER_PIN, LOW);
  }

  delay(300);
}
