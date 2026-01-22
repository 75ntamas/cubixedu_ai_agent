# PGVector Docker Setup

Lokális pgvector PostgreSQL adatbázis Docker-rel.

## Előfeltételek

⚠️ **Docker Desktop-nak futnia kell** a konténer indítása előtt!

### Docker Desktop indítása command line-ból (Windows)

**Command Prompt (CMD):**
```cmd
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

**PowerShell:**
```powershell
Start-Process -FilePath "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

Várj pár másodpercet, amíg elindul, majd ellenőrizd:
```bash
docker info
```

## Indítás

```bash
cd pgvectordb
docker-compose up -d
```

## Extension engedélyezése

A `pgvector` extension automatikusan engedélyezésre kerül az [`init.sql`](init.sql) fájl segítségével az adatbázis első indításakor.

Ha manuálisan szeretnéd ellenőrizni vagy engedélyezni:
```bash
docker exec -it pgvector psql -U user -d vectordb
```

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## Kapcsolódási adatok

- **Host:** localhost
- **Port:** 5432
- **Database:** vectordb
- **User:** user
- **Password:** password123

## Node.js példa

```typescript
import { Pool } from 'pg';

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'vectordb',
  user: 'user',
  password: 'password123',
});
```

## Hasznos parancsok

```bash
# Csak leállítás (konténerek megmaradnak)
docker-compose stop

# Leállítás és konténerek eltávolítása (adatok megmaradnak)
docker-compose down

# Leállítás, konténerek eltávolítása ÉS adatok törlése
docker-compose down -v

# Logok megtekintése
docker-compose logs -f

# Status ellenőrzése
docker-compose ps
```
