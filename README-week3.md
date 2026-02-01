# AI Assistant Backend - Document Processing System

Ez a projekt egy dokumentum feldolgozó rendszer, amely Python-ban írt backend script-et és Next.js alapú frontend alkalmazást tartalmaz. A rendszer képes szöveges dokumentumokat (.txt, .md) feldolgozni, darabokra vágni és API-n keresztül feltölteni.

------------

## Tartalomjegyzék

- [Projekt Áttekintés](#projekt-áttekintés)
- [Előfeltételek](#előfeltételek)
- [Telepítés](#telepítés)
  - [Next.js Alkalmazás](#1-nextjs-alkalmazás-telepítése)
  - [Python Script](#2-python-script-telepítése)
- [Konfigurálás](#konfigurálás)
- [Használat](#használat)
  - [Next.js Szerver Indítása](#1-nextjs-szerver-indítása)
  - [Dokumentumok Feldolgozása](#2-dokumentumok-feldolgozása)

------------

## Projekt Áttekintés

A projekt két fő komponensből áll:

1. **Next.js Alkalmazás** (`agent/`) - Web alkalmazás API endpoint-tal, amely fogadja a feldolgozott dokumentum chunk-okat
2. **Python Document Processor** (`document_processor/`) - Script, amely dokumentumokat dolgoz fel és feltölti az API-ra

### Munkafolyamat

**Dokumentum Feldolgozás:**
```
Dokumentumok (.txt/.md) → Python Script → Feldolgozás/Chunking → API Upload → Next.js Backend → PGVector DB
```

**Chat Folyamat:**
```
Felhasználói Kérdés → Chat API → Embedding Generálás → Vektor Keresés (PGVector) → Relevans Dokumentumok → AI Válasz Generálás → Válasz
```

------------

## Telepítés

### 1. Előfeltételek

A következő szoftvereknek telepítve kell lenniük:

- **Node.js** (v18 vagy újabb) és **npm**
- **Python** (v3.8 vagy újabb) és **pip**
- **Docker Desktop** - futnia kell az adatbázis indítása előtt

#### PGVector Adatbázis Indítása

A projekt használ egy lokális pgvector PostgreSQL adatbázist, amelyet Docker konténerben kell futtatni.

Részletes információk az adatbázis konfigurációjáról és használatáról a [`pgvectordb/README.md`](pgvectordb/README.md) fájlban találhatók.

### 2. Next.js Alkalmazás Telepítése

Navigálj az `agent` könyvtárba és telepítsd a függőségeket:

```bash
cd agent
npm install
```

### 3. Python Script Telepítése

A Python script-hez szükséges könyvtárak telepítése:

```bash
pip install unstructured
pip install requests
```

------------

## Konfigurálás

A Python script konfigurálása a [`document_processor/config.json`](document_processor/config.json) fájlban történik. 
Ehhez a Chunking Stratégia fejezetet nyújt információt.

Az agent app konfigurálása az [`agent/.env.local`](agent/.env.local) fájlban történik.

------------

## Használat

### 1. Next.js Szerver Indítása

**Fejlesztői mód (Development):**

```bash
cd agent
npm run dev
```

A szerver elindul a **http://localhost:3000** címen.

**Produkciós build és indítás:**

```bash
cd agent
npm run build
npm start
```

### 2. Dokumentumok Feldolgozása

A Python script futtatása egy vagy több dokumentummal:

**Szintaxis:**

```bash
python document_processor/process_document.py <file_path> [<file_path2> ...]
```

#### Script Működése

1. **Betölti a konfigurációt** a `config.json` fájlból.
2. **Beolvassa a dokumentumokat**.
3. **Darabokra vágja** a config-ban megadott stratégia szerint.
4. **Feltölti az API-ra** a konfigurált endpoint-ra.

------------

## Assistant Config Dokumentáció

A projektben található egy [`assistant_config_docs`](assistant_config_docs) mappa, amely az AI asszisztens konfigurációs dokumentációját tartalmazza.

### System Prompt

A mappában megtalálható a [`system_prompt.md`](assistant_config_docs/system_prompt.md) fájl, amely az asszisztens rendszer promptját tartalmazza. Ez a fájl határozza meg az asszisztens viselkedését és válaszadási stílusát.

### További dokumentumok

A [`assistant_config_docs`](assistant_config_docs) mappában további konfigurációs fájlok is találhatók:
- [`policy_matrix.md`](assistant_config_docs/policy_matrix.md) - Szabályzati mátrix
- [`recipe_assistant_concept.md`](assistant_config_docs/recipe_assistant_concept.md) - Recept asszisztens koncepció

------------

## Chunking Stratégia

A dokumentumok feldolgozása során a rendszer különböző stratégiákat használhat a szöveg darabokra vágására (chunking). A stratégia a [`document_processor/config.json`](document_processor/config.json) fájlban konfigurálható.

### Alapértelmezett Stratégia: `bytitle`

A **`bytitle`** stratégia az alapértelmezett és tapasztalatom szerint a leghatékonyabb választás a receptek feldolgozásához. Ennek oka a receptek strukturált felépítése:

- A receptek markdown formátumban címsorokat (title elemeket) használnak a különböző szekciók elkülönítésére
- Minden recept általában hasonló struktúrát követ: cím, hozzávalók, elkészítés lépései, stb.
- A `bytitle` stratégia ezeket a természetes szakaszhatárokat használja a daraboláshoz

### Elérhető Stratégiák

A config fájlban az alábbi stratégiák közül választhatsz:

- **`alltext`** - Az összes elemet egyetlen chunk-ba kombinálja (kis dokumentumokhoz)
- **`bytitle`** - Címsor elemek mentén hoz létre chunk-okat (ajánlott receptekhez)
- **`characters50`** - Karakterszám alapú darabolás (max_characters=100, new_after_n_chars=50, overlap=10)

------------

## Agent API Endpoint-ok

A Next.js alkalmazás két fő API endpoint-ot biztosít a dokumentumok kezelésére és a chat funkcionalitásra.

### 1. Chat API - `/api/chat`

Ez az endpoint szolgál az AI asszisztens chat funkcionalitásához. A rendszer OpenAI GPT-4o modellt használ, és egy `recipe` tool-lal rendelkezik, amely a pgvector adatbázisban keres.

#### HTTP Metódus
```
POST /api/chat
```

#### Request Body
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Mit főzzek ma vacsorára?"
    }
  ]
}
```

#### Válasz
Az endpoint streamelt text választ ad vissza (Server-Sent Events formátumban). A válasz tartalmazza:
- Az AI generált szöveges választ
- Tool hívások eredményeit (pl. recipe keresés)
- Relevans recepteket a pgvector adatbázisból

#### Példa Használat (cURL)
```bash
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hogyan készítsek pad thai-t?"}
    ]
  }'
```

#### Funkciók
- **Recipe Tool**: Automatikusan keresést végez a pgvector adatbázisban
- **System Prompt**: Betölti a [`assistant_config_docs/system_prompt.md`](assistant_config_docs/system_prompt.md) fájlt
- **Multi-step Tool Calling**: Maximum 5 lépésben képes tool-okat hívni
- **Full Recipe Reconstruction**: Ha egy chunk találat van, az összes kapcsolódó chunk-ot lekérdezi (group_id alapján)


### 2. Chunks API - `/api/chunks`

Ez az endpoint szolgál a dokumentum chunk-ok kezelésére (létrehozás és lekérdezés).

#### 2.1. Chunk Létrehozása

**HTTP Metódus:**
```
POST /api/chunks
```

**Request Body:**
```json
{
  "chunk_id": "recipe_001_chunk_1",
  "content": "# Pad Thai\n\nPad Thai is a popular Thai stir-fried noodle dish...",
  "metadata": {
    "source": "pad-thai.md",
    "group_id": "recipe_001",
    "chunk_index": 0,
    "total_chunks": 3
  }
}
```

**Válasz (201 Created):**
```json
{
  "success": true,
  "message": "Chunk received and embedded successfully",
  "chunk_id": "recipe_001_chunk_1",
  "embedding_dimensions": 1536
}
```

**Példa Használat (cURL):**
```bash
curl -X POST http://localhost:3000/api/chunks \
  -H "Content-Type: application/json" \
  -d '{
    "chunk_id": "test_chunk_1",
    "content": "Ez egy teszt recept tartalma",
    "metadata": {"source": "test.md"}
  }'
```

**Funkciók:**
- Automatikus embedding generálás (OpenAI text-embedding-3-small)
- Tárolás PGVector adatbázisban
- Validáció (chunk_id és content kötelező)


#### 2.2. Chunk-ok Lekérdezése

**HTTP Metódus:**
```
GET /api/chunks
```

**Query Paraméterek:**

| Paraméter | Típus | Alapértelmezett | Leírás |
|-----------|-------|----------------|--------|
| `chunk_id` | string | - | Egy specifikus chunk lekérdezése ID alapján |
| `search` | string | - | Szemantikus keresés hasonló chunk-okra |
| `limit` | number | 100 | Visszaadott chunk-ok maximális száma |
| `offset` | number | 0 | Lapozáshoz használt offset |

**Használati Esetek:**

##### A) Specifikus chunk lekérdezése
```bash
curl "http://localhost:3000/api/chunks?chunk_id=recipe_001_chunk_1"
```

**Válasz:**
```json
{
  "chunk": {
    "id": 1,
    "chunk_id": "recipe_001_chunk_1",
    "content": "# Pad Thai\n\n...",
    "metadata": {"source": "pad-thai.md"},
    "created_at": "2026-01-22T12:00:00Z"
  }
}
```

##### B) Szemantikus keresés
```bash
curl "http://localhost:3000/api/chunks?search=thai+noodles&limit=5"
```

**Válasz:**
```json
{
  "search_query": "thai noodles",
  "results": 3,
  "chunks": [
    {
      "chunk_id": "recipe_001_chunk_1",
      "content": "...",
      "metadata": {"source": "pad-thai.md"},
      "similarity": 0.89
    },
    ...
  ]
}
```

##### C) Összes chunk lekérdezése (lapozással)
```bash
curl "http://localhost:3000/api/chunks?limit=50&offset=0"
```

**Válasz:**
```json
{
  "total_chunks": 150,
  "returned_chunks": 50,
  "limit": 50,
  "offset": 0,
  "chunks": [...]
}
```

### Hibakezelés

Mindkét endpoint szabványos HTTP státuszkódokat használ:

- **200 OK** - Sikeres GET kérés
- **201 Created** - Sikeres POST kérés (chunk létrehozva)
- **400 Bad Request** - Hiányzó vagy érvénytelen paraméterek
- **404 Not Found** - A keresett chunk nem található
- **500 Internal Server Error** - Szerver oldali hiba

**Példa hibaüzenet:**
```json
{
  "error": "Missing required fields: chunk_id and content"
}
```

------------

## Teszt eredmények

### Kérdés: Milyen édességet tudok csinálni csokival?
Eredmény: 
Nem talált csokis édességet, mert nincs az adatbázisban. - Ez jó
Javasolt hasonlót az adatbázisban: Samosa Pie - Ez jó
Javasolt olyan csokis édességeket ami nincs az adatbázisban, de nem adott róluk receptet. - Ez jó

### Kérdés: Mit főzhetek, ha van otthon csirkemellfilém?
Eredmény: 
Több találat is volt az adatbázisban. A legrelevánsabbnak kiértékelt receptet leírta. A többi találatot felsorolta. - Ez jó

### Van valami gyors vacsora ötleted?
Eredmény: Nem kérdezi meg mi a gyors nekem. Van 30 - 45 perces találat is. Nem szerepel olyan étel, amirôl nincs idô információ.
Javítás: Metainformációban idô becslést lehetne csinálni a lépesek és hozzávalók száma alapján. Ez a 2. heti feladatban benne volt. Most ebbôl a fejlesztésbôl kimaradt.

### Hogyan készítsek carbonarát?
Eredmény: Nincs az adatbáziban recept, ezért kiírta, hogy nem talál. - Ez jó.
NEM javasolt olyan carbonara receptet ami nincs az adatbázisban. A system prompt kifejezett kérése ellenére sem. - Ez rossz
Javítás: A system prompt-ban nyomatékosítani kell ezt az igényt.

### Milyen vegetáriánus főételeket ajánlasz?
Eredmény: Adott több releváns receptet.
Javítás: Túl álltalános a kérés, túl sok a releváns találat, vissza kérdezéssel lehetne szûkíteni a kört.
Ha kérem hogy írjon másokat: Más nincs?
Eredmény: Ugyan azokat ismétli. Ennek utána kell nézni miért.