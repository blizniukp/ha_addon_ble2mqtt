# Wtyczka do Home Assistant: Bluetooth LE to MQTT
             
## Instalacja

Ta wtyczka wymaga zainstalowanej i działającej wtyczki Mosquitto MQTT Broker.                

Wykonaj poniższe kroki, aby zainstalować dodatek w swoim systemie:

1. Przejdź do **Konfiguracja**->**Dodatki, kopie zapasowe oraz Supervisor**->**Sklep z dodatkami**.
2. Z menu wybierz **Repozytoria** i dodaj repozytorium: https://github.com/blizniukp/ha_addon_ble2mqtt
3. Wyszukaj dodatek "Bluetooth LE to MQTT" i kilknij na niego.
4. Kliknij na przycisk "Instaluj"


## Sposób użycia

Po zainstalowaniu wtyczki przejdź na stronę konfiguracji.

Tam uzupełnij dane dotyczące brokera Mqtt (nazwe oraz hasło użytkownika).

Następnie musisz podać informację o urządzeniu Roundpad do tablicy `devices`. Z uwagi na limit bramki maksymalna liczba obsługiwanych urządzeń to 4.
      
Przykładowa konfiguracja wtyczki:
<pre>      
address: homeassistant
port: 1883
qos: 1
username: mqttuser
password: mqttpassword
anonymous: false
sub_topic: /ble2mqtt/app/#
pub_topic: /ble2mqtt/dev/
devices:
  - name: ROUND_PAD_1
    address_type: random
    address: DA:D5:10:DC:D0:3A
    service_uuid: 71F1BB00-1C43-5BAC-B24B-FDABEEC53913
    char_uuid: 71F1BB01-1C43-5BAC-B24B-FDABEEC53913
  - name: ROUND_PAD_2
    address_type: random
    address: DF:E2:FB:80:50:3E
    service_uuid: 71F1BB00-1C43-5BAC-B24B-FDABEEC53913
    char_uuid: 71F1BB01-1C43-5BAC-B24B-FDABEEC53913
</pre>
  
## Opis

Wtyczka współpracuje z bramką dostępną na ESP32 [esp32_ble2mqtt](https://github.com/blizniukp/esp32_ble2mqtt) oraz z urządzeniem [Roundpad](https://github.com/piotrvvilk).

Służy do tworzenia przycisków `switch` w Home Assistant które są sterowane z urządzeń Bluetooth.

Urządzenie RoundPad posiada 6 przycisków z których każdy może przesyłać informacje o pojedyńczym, podwójnym kliknięciu oraz długim przytrzymaniu klawisza.
Wobec powyższego wtyczka tworzy 18 przycisków (6 przycisków * 3 funkcjonalności).

Nazwa każdego z przycisku składa się z nazwy urządzenia, numeru przycisku oraz rodzaju kliknięcia.

Przykłady:
                                     
                -- Numer przycisku
                |  -- Rodzaj kliknięcia
                |  |
    ROUND_PAD_2_B1_F1 << urządzenie o nazwie ROUND_PAD_2, przycisk 1, funkcja pojedyńczego kliknięcia
    
    ROUND_PAD_2_B4_F2 << urządzenie o nazwie ROUND_PAD_2, przycisk 4, funkcja podwójnego kliknięcia
    
    ROUND_PAD_2_B4_F3 << urządzenie o nazwie ROUND_PAD_2, przycisk 4, funkcja długiego naciśnięcia klawisza

Natomiast nazwa encji zawiera adres MAC urządzenia (dwukropek zamieniony na znak podkreślenia), numer przycisku oraz rodzaj kliknięcia.

Przykłady:                                                                                            
                                                                                                      
                       -- Numer przycisku                                                                    
                       |  -- Rodzaj kliknięcia                                                               
                       |  |                                                                                  
    DF_E2_FB_80_50_3E_B1_F1 << urządzenie o adresie MAC DF:E2:FB:80:50:3E, przycisk 1, funkcja pojedyńczego kliknięcia 
                                                                                                      
    DF_E2_FB_80_50_3E_B4_F2 << urządzenie o adresie MAC DF:E2:FB:80:50:3E, przycisk 4, funkcja podwójnego kliknięcia   
                                                                                                  
    DF_E2_FB_80_50_3E_B4_F3 << urządzenie o adresie MAC DF:E2:FB:80:50:3E, przycisk 4, funkcja długiego naciśnięcia klawisza 

Dane przesyłane z bramki ble2mqtt posiadają informację o adresie MAC urządzenia z którego zostały wysłane dane, a także dane przesłane z przycisku.

Przykład: 

    {"address": "DA:D5:10:DC:D0:3A", "is_notify": true, "val_len": 8, "val": "0202000000000000"}

Wartość w 'val' zawiera dane dotyczące stanu urządzenia oraz stanu przycisków.
        
    D7   D6   D5   D4   D3   D2   D1   D0   << Numeracja bajtów
    02 | 02 | 00 | 00 | 00 | 00 | 00 | 00   << Dane przesłane z urządzenia

W `D7` znajduje się informacja zawierająca numer naduszonego przycisku oraz typ kliknięcia. 

Możliwe wartości to: 

    0x11 - Przycisk 1 / krótkie kliknięcie
    0x12 - Przycisk 1 / podówujne kliknięcie
    0x13 - Przycisk 1 / długie naciśnięcie
    0x21 - Przycisk 2 / krótkie kliknięcie
    0x22 - Przycisk 2 / podówujne kliknięcie
    0x23 - Przycisk 2 / długie naciśnięcie
    ...
    0x61 - Przycisk 6 / krótkie kliknięcie
    0x62 - Przycisk 6 / podówujne kliknięcie
    0x63 - Przycisk 6 / długie naciśnięcie

W `D6` znajduje się rodzaj kliknięcia/zdarzenia. 

Możliwe wartości to:

    0x00 - Przycisk nie jest wduszony
    0x01 - Przycisk jest wduszony
