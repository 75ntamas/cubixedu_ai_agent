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

## 5. Iteráció 3 (Opcionális): Finomhangolás az Eredmények Alapján

**Az Iteráció 2 eredményeitől függően:**

Ha a hangnem javul, de túl bőbeszédűvé válik:
- Tömörségi irányelvek hozzáadása az Elfoglalt Szakember personához
- Egyensúly a barátságosság és hatékonyság között

Ha a hangnem egyenetlenül javul a personák között:
- Persona-specifikus hangnem beállítások hozzáadása
- "Tapasztalt felhasználóknál őrizd meg a barátságosságot, de légy tömörebb"
- "Kezdőknél helyezd előtérbe a bátorítást és támogatást"

---

## 6. Várható Eredmények Összefoglalása

### Baseline → Iteráció 1 (Hőmérséklet 0.9)
- **Várt Hangnem Javulás**: 0.0 → 0.5-1.0
- **Indoklás**: Természetesebb variáció, kevésbé robotikus minták
- **Kockázat**: Lehet, hogy nem kezeli az alapvető formalitás problémát

### Iteráció 1 → Iteráció 2 (Optimalizált Prompt)
- **Várt Hangnem Javulás**: 0.5-1.0 → 2.0-2.5  
- **Indoklás**: Explicit utasítások barátságos, meleg nyelvezetre
- **Kockázat**: Túl kötetlenné vagy bőbeszédűvé válhat

### Általános Cél
- **Célpont Hangnem Pontszám**: 2.5-3.0/3
- **Célpont Elégedettség**: 4.0-4.5/5
- **Megőrizendő**: Pontosság, segítőkészség, professzionalizmus

---

## 7. Trade-offok és Megfontolások

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

---

## 8. Implementációs Részletek

### Fájl Struktúra
```
evaluation/
├── personas.py           # Persona és forgatókönyv definíciók
├── evaluator.py          # LLM-as-a-Judge implementáció
├── run_evaluation.py     # Fő értékelési szkript
└── results/
    ├── baseline_results.json      # Baseline teszt eredmények
    ├── iteration_1_results.json   # Hőmérséklet 0.9 eredmények
    └── iteration_2_results.json   # Optimalizált prompt eredmények
```

### Értékelések Futtatása

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

## 9. Tanulságok és Meglátások

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

3. **Multi-turn Komplexitás**
   - Még az egy-körös értékelések is értékesek
   - A beszélgetési kontextus komplexitást adna hozzá
   - Az egyszerűvel kezdés helyes megközelítés volt

### Domain Tanulságok:

1. **Főzési Domain Specifikusságok**
   - A felhasználók bátorítást akarnak
   - Az étel iránti lelkesedés elvárás
   - A személyes érintés jobban számít, mint más domaineknél

2. **Kezdő Támogatás**
   - A bátorítás kulcsfontosságú
   - A tudásszint elismerése számít
   - Egyszerű nyelv leereszkedés nélkül

---

## 10. Következő Lépések és Fejlesztések

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

## 11. Következtetés

Ez az értékelési keretrendszer bizonyítja, hogy:

1. **A hangnem mérhető és fejleszthető** szisztematikus értékelésen keresztül
2. **Világos baseline metrikák** lehetővé teszik a fejlődés nyomon követését
3. **Az iteratív fejlesztés** lehetővé teszi a célzott javításokat
4. **Az LLM-as-a-Judge** skálázható értékelést biztosít

**A Cél**: Nem a tökéletesség, hanem a mérés, iteráció és fejlesztés folyamatának megértése az AI asszisztens fejlesztésében.

**Kulcs Üzenet**: Az értékelési pipeline működik. Mérhetjük a hangemet, azonosíthatjuk a problémákat, és tervezhetünk célzott fejlesztéseket. A tényleges javulás a javasolt változtatások implementálásából és hatásuk méréséből származik.

---

## Függelék A: Baseline Adat Minta

### Példa Értékelés - Kezdő Szakács Forgatókönyv

**Felhasználói Üzenet**: "Hi! I'm a total beginner at cooking. Is there any simple Mexican-style dish I could make?"

**Asszisztens Válasz**: [Lásd baseline_results.json]

**Hangnem Értékelés**:
- **Pontszám**: 0/3
- **Indoklás**: "The response lacks warmth and friendliness. While it provides helpful recipe information, it doesn't acknowledge the user as a beginner or offer encouragement. The tone is informational but not particularly supportive or warm."

**Elégedettség**:
- **Pontszám**: 2/5
- **Indoklás**: "I got a recipe, which is what I asked for, but I didn't feel encouraged or supported as a beginner. The response was a bit dry and didn't make me feel confident about trying it."

### Mi Javítaná Ezt:

**Jobb Válasz Példa**:
"Hey! Welcome to cooking - you're going to do great! 🎉 

For a total beginner, Black Bean Enchiladas are PERFECT. Seriously, they're super easy and you can't really mess them up. Here's what makes them beginner-friendly:
- Just a few simple ingredients
- No complicated techniques
- Comes together in about 15 minutes
- Tastes amazing!

[Recept részletek...]

You've got this! And hey, even if your first attempt isn't perfect, that's totally normal. Every chef started exactly where you are now. Feel free to ask if you have any questions while you're cooking! 👨‍🍳"

**Miért Ez Jobb**:
- ✅ Elismeri a kezdő státuszt
- ✅ Bátorítást nyújt
- ✅ Lelkesedést mutat
- ✅ Megvalósíthatónak tünteti fel
- ✅ Folyamatos támogatást kínál
- ✅ Emotikonokat használ melegségért (opcionális, de hatékony)

---

## Függelék B: Technikai Specifikációk

### LLM Bíró Prompt

```
Evaluate the TONE/FRIENDLINESS of the following AI assistant response on a 0-3 scale.

USER QUESTION:
{user_message}

AI ASSISTANT RESPONSE:
{assistant_response}

EVALUATION SCALE:
0 - Robotic, cold, overly formal
1 - Somewhat friendly but still stiff  
2 - Friendly and direct, could be warmer
3 - Warm, friendly, natural (like a good friend)

Provide score (0-3) and brief reasoning.

FORMAT:
Score: X
Reasoning: ...
```

### Értékelési Metrikák Gyűjtése

Minden teszt futtatás gyűjti:
```json
{
  "iteration_name": "baseline",
  "timestamp": "2026-02-01T17:51:44",
  "total_scenarios": 5,
  "scenarios": [
    {
      "persona": {"name": "...", "description": "..."},
      "goal": "...",
      "conversation": {
        "user_message": "...",
        "assistant_response": "...",
        "response_length": 123
      },
      "evaluation": {
        "tone": {"score": 0, "reasoning": "..."},
        "satisfaction": {"satisfaction": 1, "reasoning": "..."}
      }
    }
  ],
  "summary": {
    "average_tone_score": 0.0,
    "average_satisfaction": 1.4,
    "tone_scores_distribution": {...},
    "satisfaction_distribution": {...}
  }
}
```

---

## Függelék C: Tényleges Teszteredmények

### Baseline Eredmények
- **Fájl**: `evaluation/results/baseline_results.json`
- **Átlagos Hangnem**: 0.00/3
- **Átlagos Elégedettség**: 1.40/5
- **Konfigur áció**: Eredeti system prompt, alapértelmezett temperature

### Iteráció 1 Eredmények (Temperature 0.9)
- **Fájl**: `evaluation/results/iteration_1_results.json`
- **Átlagos Hangnem**: 0.20/3 (+0.20 javulás)
- **Átlagos Elégedettség**: 2.00/5 (+0.60 javulás)
- **Konfiguráció**: Temperature 0.9, eredeti system prompt
- **Megfigyelés**: Enyhe javulás, de a válaszok még mindig formálisak

### Iteráció 2 Eredmények (Optimalizált Prompt)
- **Fájl**: `evaluation/results/iteration_2_results.json`
- **Átlagos Hangnem**: 0.20/3 (változatlan)
- **Átlagos Elégedettség**: 1.20/5 (csökkent)
- **Konfiguráció**: Temperature 0.9, optimalizált system prompt
- **Megfigyelés**: A hangnem pontszám megmaradt, de az elégedettség vegyes eredményeket mutatott

### Tanulságok az Eredményekből

**Mi működött:**
- A temperature növelése kis mértékben javította a hangemet
- Néhány forgatókönyvben jobb, természetesebb válaszok

**Mi nem működött elvárás szerint:**
- Az optimalizált prompt nem hozta a várt jelentős javulást
- Az elégedettség ingadozott az iterációk között
- A válaszok még mindig túl formálisak maradtak

**További Fejlesztési Lehetőségek:**
- Erőteljesebb példák a promptban
- Több temperatura kísérletezés
- Finomabb persona-specifikus hangnem adaptáció
- Valós felhasználói tesztelés az LLM értékelés kiegészítésére

---

**Dokumentum Verzió**: 2.0  
**Dátum**: 2026. február 1.  
**Szerző**: AI Engineering Week 4 Házi Feladat  
**Státusz**: Mind a 3 iteráció teljesítve és dokumentálva
