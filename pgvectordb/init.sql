-- Automatikusan engedélyezi a pgvector extension-t az adatbázis indulásakor
CREATE EXTENSION IF NOT EXISTS vector;

-- Tábla létrehozása a chunk-okhoz és embedding-ekhez
CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    chunk_id VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536), -- OpenAI text-embedding-ada-002 modell 1536 dimenziós
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index létrehozása a gyorsabb kereséshez
CREATE INDEX IF NOT EXISTS chunks_embedding_idx ON chunks USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS chunks_chunk_id_idx ON chunks(chunk_id);
CREATE INDEX IF NOT EXISTS chunks_metadata_idx ON chunks USING GIN(metadata);
