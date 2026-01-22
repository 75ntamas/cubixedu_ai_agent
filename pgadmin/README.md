# pgAdmin Docker Setup

Vizuális kezelőfelület a pgvector PostgreSQL adatbázis kezeléséhez.

## Előfeltételek

⚠️ **A pgvectordb konténernek futnia kell!** Először indítsd el azt.

## Indítás

```bash
cd pgadmin
docker-compose up -d
```

## Hozzáférés

Nyisd meg a böngészőben: **http://localhost:5050**

### Bejelentkezési adatok:
- **Email:** admin@admin.com
- **Jelszó:** admin

## Adatbázis kapcsolat

Az adatbázis kapcsolat automatikusan be van állítva a [`servers.json`](servers.json) fájl alapján:

- **Host:** host.docker.internal (ez a Docker host gépet jelenti)
- **Port:** 5432
- **Database:** vectordb
- **Username:** user
- **Password:** password123 (ezt manuálisan kell megadni az első csatlakozáskor)

### Első csatlakozás:
1. Nyisd meg: http://localhost:5050
2. Jelentkezz be: admin@admin.com / admin
3. A bal oldali menüben látni fogod a "PGVector Database" szervert
4. Kattints rá → Kéri a jelszót
5. Add meg: **password123**
6. ✅ Opcionálisan pipáld be a "Save password" opciót

## Hasznos műveletek pgAdmin-ban

### Táblák megtekintése:
1. Bontsd ki: Servers → PGVector Database → Databases → vectordb → Schemas → public → Tables
2. Jobb klikk a `chunks` táblára → View/Edit Data → All Rows

### SQL lekérdezés futtatása:
1. Jobb klikk a `vectordb` adatbázison → Query Tool
2. Írd be a lekérdezést, például:
```sql
SELECT id, chunk_id, content, metadata, created_at FROM chunks LIMIT 10;
```
3. Nyomd meg az F5-öt vagy kattints a ▶ gombra

## Leállítás

```bash
# Leállítás (konténer megmarad)
docker-compose stop

# Leállítás és konténer eltávolítása (adatok megmaradnak)
docker-compose down

# Leállítás, konténer eltávolítása ÉS adatok törlése
docker-compose down -v
```

## Kapcsolódó fájlok

- [`docker-compose.yml`](docker-compose.yml) - pgAdmin konténer konfiguráció
- [`servers.json`](servers.json) - Előre beállított adatbázis kapcsolat
- [`../pgvectordb/docker-compose.yml`](../pgvectordb/docker-compose.yml) - PostgreSQL adatbázis konfiguráció
