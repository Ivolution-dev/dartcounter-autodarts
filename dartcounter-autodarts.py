from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------------------------
# Konfiguration
# ---------------------------

AUTODARTS_URL = "YOUR LOCAL AUTODARTS IP"
DARTCOUNTER_URL = "https://app.dartcounter.net"
SPAN_CLASS_NAME = "css-1ny2kle"
INPUT_SELECTOR = 'input.in-game-score-field'

SCORES = [501, 501]
OWNELEMENT = None
COUNTER = 0

# Dart-Symbol zu Punktwert
def dart_to_score(dart_str):
    dart_str = dart_str.strip()

    if dart_str in ['-', '']:
        return 0

    if dart_str == '25':
        return 25

    if dart_str.lower() == 'bull':
        return 50

    if dart_str.startswith('S'):
        return int(dart_str[1:])
    if dart_str.startswith('D'):
        return int(dart_str[1:]) * 2
    if dart_str.startswith('T'):
        return int(dart_str[1:]) * 3

    # Fallback für alles andere, was direkt eine Zahl ist (z. B. 20)
    if dart_str.isdigit():
        return int(dart_str)

    return 0  # Wenn nichts passt

# ---------------------------
# Hauptprogramm
# ---------------------------

# Chrome starten
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(), options=options)

# Beide Tabs öffnen
driver.get(AUTODARTS_URL)
driver.execute_script("window.open('');")
driver.switch_to.window(driver.window_handles[1])
driver.get(DARTCOUNTER_URL)

# Zurück zum AutoDarts-Tab
driver.switch_to.window(driver.window_handles[0])

last_darts = []
previous_valid_darts = []

def read_remaining_scores():
    elems = driver.find_elements(By.TAG_NAME, "app-remaining-score")
    out = []
    for el in elems:
        t = el.text.strip()
        try:
            out.append(int(t))
        except:
            out.append(0)
    return out

def guess_own_index_from_legscores():
    """
    Versucht zu erkennen, welche Seite aktiv ist (am Zug) anhand der animierten '...'-Anzeige.
    """
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, "//app-match-leg-scores"))
        )
        blocks = driver.find_elements(
            By.XPATH,
            "//app-match-leg-scores//div[contains(@class,'flex') and contains(@class,'w-1/2') and contains(@class,'flex-col')]"
        )
        for idx, block in enumerate(blocks):
            pulse = block.find_elements(By.XPATH, ".//div[contains(@class,'animate-pulse')]")
            if pulse:
                return idx
    except:
        pass
    return None

def detect_own_index_by_diff(prev_scores, post_scores, score_entered):
    """
    Fallback nach dem Eintragen: vergleicht vorher/nachher.
    Gibt den Index zurück, dessen Restscore sich geändert hat.
    """
    try:
        diffs = []
        n = min(len(prev_scores), len(post_scores), 2)
        for i in range(n):
            diffs.append(prev_scores[i] - post_scores[i])

        # 1) Eindeutig: nur einer hat sich verändert
        changed = [i for i, d in enumerate(diffs) if d != 0]
        if len(changed) == 1:
            return changed[0]

        # 2) Beide verändert? Dann nimm den, dessen Änderung dem eingegebenen Score entspricht
        exact = [i for i, d in enumerate(diffs) if d == score_entered]
        if len(exact) == 1:
            return exact[0]
    except:
        pass
    return None

def print_leg_scores():
    """Liest die beiden Leg-Scores (mittlere große Zahl je Seite) aus und gibt sie aus."""
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//app-match-leg-scores"))
        )
        # Links & rechts (zwei Spalten) robust auswählen
        blocks = driver.find_elements(
            By.XPATH,
            "//app-match-leg-scores//div[contains(@class,'flex') and contains(@class,'w-1/2') and contains(@class,'flex-col')]"
        )

        vals = []
        for b in blocks:
            mid = b.find_elements(
                By.XPATH,
                ".//div[contains(@class,'col-span-1') and contains(@class,'text-center') and contains(@class,'text-3xl')]"
            )
            txt = mid[0].text.strip() if mid else ""
            vals.append(txt if txt else "N/A")

        while len(vals) < 2:
            vals.append("N/A")

        print(f"📊 Aktuelle Leg-Scores: {vals[0]} | {vals[1]}")
    except Exception as e:
        print("❌ Fehler beim Auslesen der Leg-Scores:", e)
        
def on_round_finished(dart_values):
    total = sum(dart_to_score(d) for d in dart_values)
    print(f"🎯 Runde beendet: {dart_values} ➤ Gesamtpunkte: {total}")

    # Wechsle zu DartCounter-Tab
    driver.switch_to.window(driver.window_handles[1])
    time.sleep(0.5)

    try:
        # Restscore VORHER lesen
        prev_scores = read_remaining_scores()
        print(f"Vorherige Remaining-Scores: {prev_scores}")

        # Falls noch unbekannt: versuche, die aktive Seite (deine) aus Leg-Scores zu erraten
        global OWNELEMENT
        if OWNELEMENT is None:
            guessed = guess_own_index_from_legscores()
            if guessed is not None:
                OWNELEMENT = guessed
                print(f"🧭 OWNELEMENT (vor Eintrag) erkannt: {OWNELEMENT}")


        remaining_element = driver.find_elements(By.TAG_NAME, "app-remaining-score") 
        print(f"{remaining_element}") 
        for i in range(0, len(remaining_element)): 
            remaining_text = remaining_element[i].text.strip() 
            remaining_score = int(remaining_text) if remaining_text.isdigit() else 0 
            print(f"🧮 Restscore laut DartCounter: {remaining_score}") 
            SCORES[i] = remaining_score 
            
        # Entscheidung: tatsächlicher Score oder 0 bei Überwurf 
        score_to_enter = total 
        if OWNELEMENT != None: 
            if total > SCORES[OWNELEMENT]:
                score_to_enter = 0
            elif SCORES[OWNELEMENT] - total == 1:
                score_to_enter = 0
            elif total == SCORES[OWNELEMENT]:
                if dart_values[2].startswith("D") or (total == 50 and dart_values[2].lower() == "bull"):
                    score_to_enter = total
                else:
                    score_to_enter = 0
            else:
                score_to_enter = total

        # Score eintragen
        input_field = driver.find_element(By.CSS_SELECTOR, INPUT_SELECTOR)
        input_field.clear()
        input_field.send_keys(str(score_to_enter))
        input_field.send_keys(Keys.ENTER)
        print(f"✅ Eingetragen bei DartCounter: {score_to_enter}")

        # KURZ warten, dann Restscore NACHHER lesen
        time.sleep(0.4)
        post_scores = read_remaining_scores()
        print(f"Nachherige Remaining-Scores: {post_scores}")

        # Falls OWNELEMENT noch unbekannt: per Diff bestimmen
        if OWNELEMENT is None:
            detected = detect_own_index_by_diff(prev_scores, post_scores, score_to_enter)
            if detected is not None:
                OWNELEMENT = detected
                print(f"🧭 OWNELEMENT (nach Eintrag) erkannt: {OWNELEMENT}")
            else:
                print("⚠️ Konnte OWNELEMENT nicht eindeutig bestimmen.")

        # SCORES updaten (auf Länge 2 fix)
        for i in range(min(2, len(post_scores))):
            SCORES[i] = post_scores[i]

        # Ausgabe der Leg-Scores
        print_leg_scores()

    except Exception as e:
        print("❌ Fehler beim Eintragen in DartCounter:", e)


    # ⏳ Warten, bis Dialog geschlossen ist
    print("🔄 Warte auf Checkout-Dialog (falls offen)...")
    while True:
        try:
            dialog = driver.find_element(By.TAG_NAME, "app-darts-for-throwout-dialog")
            if dialog.is_displayed():
                time.sleep(0.5)
                continue
        except:
            break  # Element nicht mehr vorhanden oder nicht sichtbar

    print("🔙 Zurück zu AutoDarts")
    driver.switch_to.window(driver.window_handles[0])


try:
    while True:
        elements = driver.find_elements(By.CLASS_NAME, SPAN_CLASS_NAME)
        try:
            current_darts = [el.text.strip() for el in elements[2:5]]  # Dartwerte
        except:
            pass

        print(current_darts)

        if current_darts == ['-', '-', '-'] and previous_valid_darts:
            on_round_finished(previous_valid_darts)
            previous_valid_darts = []

        elif any(d not in ['-', ''] for d in current_darts):
            previous_valid_darts = current_darts

        time.sleep(0.5)

except KeyboardInterrupt:
    print("Beendet durch Benutzer.")

finally:
    driver.quit()
