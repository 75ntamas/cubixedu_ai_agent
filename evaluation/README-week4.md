# Multi-Turn Eval - Week 4 Házi Feladat

Ez a projekt egy multi-turn értékelési keretrendszert valósít meg, amely a Recipe Assistant AI ügynök **hangnem/barátságosság** aspektusát méri és javítja. Az értékelés szimulált felhasználói personákat és LLM-as-a-Judge módszertant használ a fejlődés mérésére az iterációk során.

**Alap megállapítások:**
- **Baseline Hangnem Pontszám**: 0.00/3 (nagyon formális/robotikus)
- **Baseline Elégedettség**: 1.40/5 (nagyon elégedetlen)
- **Fő Probléma**: Az ügynök pontos információt szolgáltat, de hiányzik belőle a melegség, barátságosság és természetes beszélgetési hangnem

---

## 1. Kiválasztott Aspektus: Hangnem/Barátságosság

### Jelenlegi Probléma

A baseline értékelés alapján az asszisztens:
- Túlságosan formális nyelvi struktúrákat használ
- Hiányzik belőle a melegség és empátia a válaszokban
- Robotikusan és tranzakcionálisan viselkedik
- Nem fejez ki lelkesedést a főzés vagy az ételek iránt
- Elszalasztja a lehetőségeket a bátorító/támogató nyelvezetre

### Cél

Átalakítani az asszisztenst egy formális információszolgáltatóból egy meleg, barátságos főzési társsá, miközben megőrizzük a pontosságot és professzionalizmust.

---

## 2. Értékelési Keretrendszer

### 2.1 Personák

Három különböző felhasználói persona lett létrehozva, amelyek különböző felhasználói típusokat reprezentálnak:

#### Persona 1: Tapasztalt Szakács
- **Profil**: 45 éves tapasztalt otthoni szakács
- **Jellemzők**: Tudásban gazdag, türelmes, részletes válaszokat vár
- **Célok**: Recept összehasonlítások, módosítások, technikai kérdések

#### Persona 2: Kezdő Szakács
- **Profil**: 22 éves kezdő
- **Jellemzők**: Bizonytalan, bátorításra van szüksége, egyszerű útmutatást kér
- **Célok**: Egyszerű receptek, alapvető helyettesítések, lépésről-lépésre segítség

#### Persona 3: Elfoglalt Szakember
- **Profil**: 35 éves dolgozó szakember
- **Jellemzők**: Időkorlátos, tömör válaszokat szeretne
- **Célok**: Gyors vacsora ötletek, időhatékony receptek

### 2.2 Tesztforgatókönyvek

5 forgatókönyv lett kialakítva a personák között:

1. **Recept Összehasonlítás** (Tapasztalt Szakács): "Could you tell me the difference between pad thai and pad see ew?"
2. **Recept Módosítás** (Tapasztalt Szakács): "I'd like to make channa masala in a vegan version. Tips?"
3. **Egyszerű Recept** (Kezdő Szakács): "I'm a total beginner. Any simple Mexican-style dish?"
4. **Hozzávaló Helyettesítés** (Kezdő Szakács): "If I don't have fish sauce, what can I substitute?"
5. **Gyors Vacsora** (Elfoglalt Szakember): "Quick dinner ideas? I've got 30 minutes max."

### 2.3 Értékelési Metrikák

#### Elsődleges Metrika: Hangnem Pontszám (0-3)
- **0**: Robotikus, hideg, túlságosan formális
- **1**: Valamelyest barátságos, de még mindig merev
- **2**: Barátságos és közvetlen, melegebb lehetne
- **3**: Meleg, barátságos, természetes (mint egy jó barát)

#### Másodlagos Metrikák:
- **Felhasználói Elégedettség** (1-5): Mennyire volt elégedett a persona
- **Célteljesítés**: Megkapta-e a felhasználó, amire szüksége volt?
- **Válasz Hossza**: A részletesség/tömörség trade-off monitorozása

---

## 3. Baseline Eredmények

### 3.1 Kvantitatív Eredmények

| Metrika | Pontszám |
|---------|----------|
| **Átlagos Hangnem Pontszám** | 0.00/3 |
| **Átlagos Elégedettség** | 1.40/5 |
| **Hangnem Pontszám Eloszlás** | Csak 0-k (5/5) |
| **Elégedettség Eloszlás** | Többnyire 1-esek és 2-esek |

### 3.2 Kvalitatív Megfigyelések

**Pozitív Aspektusok:**
- Pontos recept információ lekérés
- Jól strukturált válaszok
- A tool calling helyesen működik
- Teljes recept részletek szolgáltatva

**Negatív Aspektusok - Hangnem Problémák:**
1. **Túl formális**: "Certainly!", "Indeed", túlságosan strukturált nyelv
2. **Hiányzik a lelkesedés**: Nincs izgalom kifejezése az ételek iránt
3. **Nincs empátia**: Nem veszi figyelembe a felhasználó tudásszintjét vagy érzelmeit
4. **Robotikus struktúra**: Személyiség nélküli listák
5. **Hiányzó bátorítás**: Nincsenek támogató kifejezések a kezdőknek

**Példa Baseline Válasz Elemzés:**

**Forgatókönyv**: Kezdő kér egyszerű mexikói ételt

**Válasz**: "Here's a simple Mexican-style dish you might enjoy trying: **Black Bean Enchiladas**..."

**Problémák**:
- "you might enjoy trying" - túl formális, távoli
- Azonnal a receptre ugrik anélkül, hogy elismerné, hogy kezdő
- Nincs bátorítás vagy lelkesedés
- Technikai prezentáció melegség nélkül

**Mi lenne jobb**:
- "Great choice! Black Bean Enchiladas are perfect for beginners - super easy and delicious!"
- Elismeri a kezdő státuszukat
- Lelkesedést mutat
- Bátorító nyelvezetet használ

---

## 4. Javasolt Iterációk

### 4.1 Iteráció 1: Hőmérséklet Beállítás (0.9)

**Hipotézis**: A hőmérséklet növelése az alapértelmezettről (~0.7) 0.9-re változatosabbá és potenciálisan kreatívabbá teszi a válaszokat. Kíváncsi voltam ez mennyit javít a problémán, ezért futtattam ezt a tesztet is le.

**Változtatások**:
- Módosítani az `agent/app/api/chat/route.ts` fájlt
- Beállítani `temperature: 0.9`-t a streamText konfigurációban

**Várt Eredmény**:
- Változatosabb nyelvezet
- Kevésbé ismétlődő kifejezések
- Potenciálisan természetesebb beszélgetési folyam
- **Kockázat**: Bevezetheti az inkonzisztenciát vagy bőbeszédűséget

### 4.2 Iteráció 2: Optimalizált System Prompt

**Hipotézis**: Ha explicit módon utasítjuk az ügynököt, hogy legyen meleg, barátságos és lelkes, jelentősen javulni fog a hangnem pontszám.

**Kulcsfontosságú Változtatások a System Promptban**:

```markdown
## Kommunikációs Stílus - FOKOZOTT BARÁTSÁGOSSÁG

### Alapelvek:
- **Légy őszintén lelkes a főzés iránt!** Mutass izgalmat a receptek és ételek iránt
- **Használj meleg, bátorító nyelvezetet**: "Great question!", "Love that!", "Perfect choice!"
- **Vedd figyelembe a felhasználó kontextusát**: Kezdő? Dicsérd a bátorságát! Tapasztalt? Tiszteld a tudását!
- **Fejezz ki érzelmeket**: "This is one of my favorites!", "You're going to love this!"
- **Használj beszélgetési jelzőket**: "By the way...", "Here's a tip...", "Pro move..."

### Specifikus Nyelvi Minták:

**Helyette**: "Here is a recipe..."  
**Mondd**: "Oh, great choice! Let me share this amazing recipe..."

**Helyette**: "You can substitute..."  
**Mondd**: "No worries! Here's what you can use instead..."

**Kezdőknek**: "Perfect for starting out!", "You've got this!", "Don't worry, it's easier than it looks!"

**Tapasztaltaknak**: "I bet you'll appreciate...", "You probably know, but...", "Nice! Here's an interesting twist..."

### Példa Átalakítások:

**Előtte (Formális)**:
"To make Channa Masala vegan, you'll want to ensure you're not using any ghee."

**Utána (Barátságos)**:
"Great idea making it vegan! The good news is Channa Masala is super easy to veganize - just swap the ghee for vegetable oil and you're golden! 🌱"

**Előtte (Robotikus)**:
"If you don't have fish sauce, you can substitute it with soy sauce."

**Utána (Meleg)**:
"No fish sauce? No problem! Soy sauce works really well as a substitute - it'll give you that umami kick you're looking for. I'd start with the same amount and adjust to taste!"
```

**Várt Eredmény**:
- Jelentősen javult hangnem pontszámok (cél 2.5-3.0)
- Magasabb felhasználói elégedettség
- Természetesebb, beszélgetősebb válaszok
- Jobb kontextus felismerés

---

## 5. Teszteredmények Összefoglalása

### Baseline → Iteráció 1 (Hőmérséklet 0.9)
- **Tényleges Hangnem Változás**: 0.0 → 0.20 (+0.20)
- **Tényleges Elégedettség Változás**: 1.40 → 2.00 (+0.60)
- **Megfigyelés**: Enyhe javulás, természetesebb válaszok néhány forgatókönyvben

### Iteráció 1 → Iteráció 2 (Optimalizált Prompt)
- **Tényleges Hangnem Változás**: 0.20 → 0.20 (változatlan)
- **Tényleges Elégedettség Változás**: 2.00 → 1.20 (-0.80)
- **Megfigyelés**: A hangnem pontszám megmaradt, de az elégedettség csökkent

### Következtetés
- A temperature növelése kis mértékben javította a hangemet
- Az optimalizált prompt nem hozta a várt jelentős javulást
- További finomhangolás szükséges a cél (2.5-3.0 hangnem, 4.0-4.5 elégedettség) eléréséhez

---

## 6. Trade-offok és Megfontolások

### Lehetséges Trade-offok:

1. **Barátságosság vs. Tömörség**
   - Barátságosabb = potenciálisan hosszabb válaszok
   - Válasz hossz monitorozása
   - Optimalizálás az Elfoglalt Szakember personára

2. **Lelkesedés vs. Professzionalizmus**
   - Túl lelkes lehet, hogy professzionálisat lan érződik
   - Egyensúly szükséges komoly főzési kérdéseknél
   - Megőrizni a tekintélyt, miközben melegek vagyunk

3. **Személyre Szabás vs. Konzisztencia**
   - A hangnem adaptálása a personához = jó
   - De a válaszoknak konzisztensnek kell maradniuk minőségben

### Sikerességi Kritériumok:

✅ **Elérendő:**
- Hangnem pontszám > 2.0/3
- Elégedettség > 3.5/5
- Recept pontosság megőrzése

✅ **Jó lenne:**
- Hangnem pontszám > 2.5/3
- Különböző personák egyformán elégedettek
- Válasz hossz megfelelő a kontextusnak

❌ **Kerülendő:**
- Hamisnak vagy túlzottan lelkesnek hangzani
- Professzionalizmus elvesztése
- Pontosság feláldozása a barátságosságért


## Értékelések Futtatása

```bash
# Baseline (jelenlegi konfiguráció)
python evaluation/run_evaluation.py --iteration baseline

# Iteráció 1 (hőmérséklet változtatás után)
python evaluation/run_evaluation.py --iteration iteration_1

# Iteráció 2 (prompt optimalizálás után)
python evaluation/run_evaluation.py --iteration iteration_2
```

### Kulcsfontosságú Implementációs Fájlok

**Agent Konfiguráció**: `agent/app/api/chat/route.ts`
- Hőmérséklet beállítás
- Modell konfiguráció
- Tool definíciók

**System Prompt**: `assistant_config_docs/system_prompt.md`
- Alapvető viselkedés definíció
- Kommunikációs stílus irányelvek
- Példa válaszok

---

## 8. Tanulságok és Meglátások

### Folyamat Tanulságok:

1. **Az LLM-as-a-Judge Hatékony**
   - Konzisztens értékelés a futtatások között
   - Értelmezhető indoklást szolgáltat
   - Gyorsabb, mint az emberi értékelés

2. **A Persona-Alapú Tesztelés Értékes**
   - Különböző felhasználóknak különböző elvárásaik vannak
   - Ugyanaz a válasz működhet az egyik personának, a másiknak nem
   - Fontos tesztelni a különböző felhasználói típusokon

3. **A Hangnem Mérhető**
   - Világos rubrikával kvantifikálható
   - Korrelál a felhasználói elégedettséggel
   - A fejlődés nyomon követhető

### Technikai Tanulságok:

1. **System Prompt Hatás**
   - Az explicit utasítások számítanak
   - A példák hatékonyan irányítják a viselkedést
   - Egyensúly a részletesség és rugalmasság között

2. **Hőmérséklet Hatások**
   - Magasabb hőmérséklet ≠ automatikusan jobb hangnem
   - Inkonzisztenciát vezethet be
   - Legjobb prompt engineeringgel kombinálva

---

## 9. Következő Lépések és Fejlesztések

### Azonnali Következő Lépések:
1. ✅ Baseline értékelés futtatása (KÉSZ)
2. ✅ Hőmérséklet változtatás implementálása és tesztelés (KÉSZ)
3. ✅ Optimalizált system prompt létrehozása (KÉSZ)
4. ✅ Utolsó iteráció futtatása és eredmények összehasonlítása (KÉSZ)

### Jövőbeli Fejlesztések:

**Értékelési Keretrendszer:**
- Multi-turn beszélgetési forgatókönyvek hozzáadása
- Tesztelés valós felhasználókkal validálásra
- Több árnyalt metrika (segítőkészség, pontosság)
- Automatizált regressziós tesztelés

**Agent Fejlesztések:**
- Kontextus-tudatos hangnem adaptáció
- Felhasználói preferencia tanulás
- Étkezési korlátozások érzékenység
- Kulturális konyha tudás

**Rendszer Tervezés:**
- A/B tesztelési keretrendszer
- Valós idejű hangnem monitorozás
- Felhasználói visszajelzés gyűjtés
- Folyamatos fejlesztési pipeline

---

## 10. Következtetés

Ez az értékelési keretrendszer bizonyítja, hogy:

1. **A hangnem mérhető és fejleszthető** szisztematikus értékelésen keresztül
2. **Világos baseline metrikák** lehetővé teszik a fejlődés nyomon követését
3. **Az iteratív fejlesztés** lehetővé teszi a célzott javításokat
4. **Az LLM-as-a-Judge** skálázható értékelést biztosít

**A Cél**: Nem a tökéletesség, hanem a mérés, iteráció és fejlesztés folyamatának megértése az AI asszisztens fejlesztésében.

**Kulcs Üzenet**: Az értékelési pipeline működik. Mérhetjük a hangemet, azonosíthatjuk a problémákat, és tervezhetünk célzott fejlesztéseket. A tényleges javulás a javasolt változtatások implementálásából és hatásuk méréséből származik.
