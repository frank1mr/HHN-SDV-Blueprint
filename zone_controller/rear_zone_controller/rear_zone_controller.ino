#include <Arduino_CAN.h>
#include <Ethernet.h>
#include <EthernetUdp.h>


// Netzwerk-Einstellungen
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192, 168, 1, 11);
IPAddress bc(192, 168, 1, 1);
unsigned int localPort = 6001;
unsigned int bcPort = 5001;

EthernetUDP Udp;

// CAN-Puffer
char packetBuffer[20];

void setup() {
    Ethernet.begin(mac, ip);
    Udp.begin(localPort);
    Serial.begin(9600);

    if (!CAN.begin(CanBitRate::BR_250k)) {
        Serial.println("CAN-Start fehlgeschlagen!");
        while (1);
    }

    Serial.println("CAN-UDP Bridge gestartet...");
}

void loop() {
    // 1. Empfangene UDP-Pakete -> CAN senden
  int packetSize = Udp.parsePacket();
    if (packetSize > 0) {
        Udp.read(packetBuffer, sizeof(packetBuffer));

      // CAN-Nachricht aus UDP-Daten erstellen
      CanMsg canMsg;

      // 29-Bit-ID aus 4 Bytes extrahieren
      canMsg.id = ((uint32_t)packetBuffer[0] << 24) |
                  ((uint32_t)packetBuffer[1] << 16) |
                  ((uint32_t)packetBuffer[2] << 8)  |
                  ((uint32_t)packetBuffer[3]);

      canMsg.id |= 0x80000000;

      canMsg.data_length = packetBuffer[4]; 

        if (canMsg.data_length > 8) {  // Maximale CAN-Datenlänge ist 8 Bytes
            canMsg.data_length = 8;
        }

        memcpy(canMsg.data, &packetBuffer[5], canMsg.data_length);  // Daten kopieren

        if (CAN.write(canMsg)) {  // Nachricht auf den CAN-Bus schreiben und Erfolg prüfen
            Serial.print("Gesendet[CAN-BUS]: CAN-ID: 0x");
            Serial.println(canMsg.id, HEX);
            Serial.print(" DLC: ");
            Serial.print(canMsg.data_length);
            Serial.print(" Data: ");

            for (int i = 0; i < canMsg.data_length; i++) {
                Serial.print(canMsg.data[i], HEX);
                Serial.print(" ");
            }
            Serial.println();
        } else {
            Serial.println("Fehler beim Senden der CAN-Nachricht!");
        }
    }

    // 2. Empfangene CAN-Nachrichten -> per UDP senden
    if (CAN.available()) {
      CanMsg rxMsg = CAN.read();

      // Maske auf 29 Bit – nur nötig, wenn Bit 31 gesetzt ist
      uint32_t id = rxMsg.id & 0x7FFFFFFF;

      // CAN-Nachricht verpacken
      packetBuffer[0] = (id >> 24) & 0xFF;
      packetBuffer[1] = (id >> 16) & 0xFF;
      packetBuffer[2] = (id >> 8) & 0xFF;
      packetBuffer[3] = id & 0xFF;
      packetBuffer[4] = rxMsg.data_length;
      memcpy(&packetBuffer[5], rxMsg.data, rxMsg.data_length);

      Serial.print("Gesendet[UDP]: CAN-ID: 0x");
      Serial.println(rxMsg.id, HEX);
      Serial.println(id, HEX);

      // UDP senden
      Udp.beginPacket(bc, bcPort);
      Udp.write((uint8_t*)packetBuffer, 5 + rxMsg.data_length);
      Udp.endPacket();
      Serial.println("CAN-Nachricht über UDP gesendet!");
    }
}






