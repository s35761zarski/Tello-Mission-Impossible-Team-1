from djitellopy import Tello
import cv2
import threading
import time

# Flaga bezpieczeństwa - dostępna dla wszystkich wątków
safety_landing_triggered = False

def video_and_data_handler(tello):
    """
    Główny wątek obsługujący obraz oraz wszystkie parametry 
    w czasie rzeczywistym (bez opóźnień czasowych).
    """
    global safety_landing_triggered
    frame_read = tello.get_frame_read()
    
    while True:
        img = frame_read.frame
        if img is not None:
            # POBIERANIE DANYCH W CZASIE RZECZYWISTYM (każda klatka = nowy odczyt)
            height = tello.get_height()
            battery = tello.get_battery()
            temp = tello.get_highest_temperature()
            baro = tello.get_barometer() # dodatkowy parametr - barometr

            # LOGIKA BEZPIECZEŃSTWA (Safety Check)
            # Sprawdzane przy każdej klatce obrazu
            if (battery <= 20 or temp > 80) and not safety_landing_triggered:
                safety_landing_triggered = True
                print(f"\n[ALARM] KRYTYCZNE PARAMETRY! Bateria: {battery}%, Temp: {temp}C. Lądowanie...")
                tello.land()

            # NAKŁADANIE DANYCH NA OBRAZ (OSD)
            # Parametry wyświetlane płynnie na ekranie
            color_stat = (0, 255, 0) # Zielony
            color_warn = (0, 0, 255) # Czerwony
            
            # Wyświetlanie wysokości
            cv2.putText(img, f"Wysokosc: {height} cm", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_stat, 2)
            
            # Wyświetlanie baterii (zmienia kolor na czerwony poniżej 25%)
            bat_color = color_stat if battery > 25 else color_warn
            cv2.putText(img, f"Bateria: {battery}%", (20, 70), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, bat_color, 2)
            
            # Wyświetlanie temperatury
            temp_color = color_stat if temp < 75 else color_warn
            cv2.putText(img, f"Temp: {temp} C", (20, 100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, temp_color, 2)
            
            # Wyświetlanie napisu ALERT jeśli lądowanie awaryjne
            if safety_landing_triggered:
                cv2.putText(img, "LANDING: SAFETY ALERT", (200, 240), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, color_warn, 3)

            cv2.imshow("Tello Real-Time Monitor", img)
        
        # Wyjście klawiszem 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def main():
    tello = Tello()
    tello.connect()
    tello.streamon()

    # Uruchamiamy JEDEN wątek, który zarządza obrazem i danymi
    # Dzięki temu wysokość i bezpieczeństwo sprawdzane są przy każdej klatce obrazu
    monitor_thread = threading.Thread(target=video_and_data_handler, args=(tello,))
    monitor_thread.daemon = True
    monitor_thread.start()

    print("Wszystkie systemy monitorowane real-time. Start...")
    time.sleep(2)

    try:
        if not safety_landing_triggered:
            tello.takeoff()
            
        def safe_move(cmd, val=None):
            if not safety_landing_triggered:
                if val is not None:
                    getattr(tello, cmd)(val)
                else:
                    getattr(tello, cmd)()

        # SEKWENCJA RUCHÓW
        safe_move('move_up', 70) # Do 1.5m
        safe_move('rotate_counter_clockwise', 360) # 360 w lewo
        
        # Flipy
        for f in ['flip_forward', 'flip_left', 'flip_back', 'flip_right']:
            safe_move(f)
            
        safe_move('rotate_clockwise', 360) # 360 w prawo
        
        if not safety_landing_triggered:
            tello.land()

    except Exception as e:
        print(f"Błąd podczas lotu: {e}")
        tello.land()
    finally:
        tello.streamoff()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

  #zobaczymy czy to zadziala. dron startuje, robi obrot w lewo o 360 stopni, robi 4 salta, do przodu, w lewo, w tyl i w prawo, robi obrot w prawo o 360 stopni i ląduje. Caly ten czas przesyla video i dane o temperaturze, wysokosci i baterii do komputera.
  # jesli temperatura przekroczy 80 stopni, lub jesli bateria spadnie ponizej 20 procent, dron przerywa swoje dzialania i automatycznie ląduje
#zostawilem komentarze gemini. jakby mialo to isc dalej, to trzeba je usunac przed prezentacja
  
  # Kod Mateusza (Akrobacje i bateria)
