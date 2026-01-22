import { Pool, PoolClient } from 'pg';

// Database connection configuration
const pool = new Pool({
  user: process.env.PGVECTOR_USER || 'user',
  host: process.env.PGVECTOR_HOST || 'localhost',
  database: process.env.PGVECTOR_DB || 'vectordb',
  password: process.env.PGVECTOR_PASSWORD || 'password123',
  port: parseInt(process.env.PGVECTOR_PORT || '5432'),
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Test the connection
pool.on('connect', () => {
  console.log('Connected to pgvector database');
});

pool.on('error', (err) => {
  console.error('Unexpected error on idle client', err);
});

export interface ChunkWithEmbedding {
  chunk_id: string;
  content: string;
  embedding: number[];
  metadata?: Record<string, any>;
}

export interface ChunkRecord {
  id: number;
  chunk_id: string;
  content: string;
  embedding: number[];
  metadata: Record<string, any>;
  created_at: Date;
}

/**
 * Insert a chunk with its embedding into the database
 */
export async function insertChunkWithEmbedding(
  chunkData: ChunkWithEmbedding
): Promise<ChunkRecord> {
  const client = await pool.connect();
  try {
    const query = `
      INSERT INTO chunks (chunk_id, content, embedding, metadata)
      VALUES ($1, $2, $3, $4)
      ON CONFLICT (chunk_id) 
      DO UPDATE SET 
        content = EXCLUDED.content,
        embedding = EXCLUDED.embedding,
        metadata = EXCLUDED.metadata,
        created_at = CURRENT_TIMESTAMP
      RETURNING *;
    `;

    const values = [
      chunkData.chunk_id,
      chunkData.content,
      JSON.stringify(chunkData.embedding),
      JSON.stringify(chunkData.metadata || {}),
    ];

    const result = await client.query(query, values);
    return result.rows[0];
  } finally {
    client.release();
  }
}

/**
 * Search for similar chunks using cosine similarity
 */
export async function searchSimilarChunks(
  queryEmbedding: number[],
  limit: number = 5,
  threshold: number = 0.7
): Promise<Array<ChunkRecord & { similarity: number }>> {
  const client = await pool.connect();
  try {
    const query = `
      SELECT 
        *,
        1 - (embedding <=> $1::vector) as similarity
      FROM chunks
      WHERE 1 - (embedding <=> $1::vector) > $2
      ORDER BY embedding <=> $1::vector
      LIMIT $3;
    `;

    const values = [
      JSON.stringify(queryEmbedding),
      threshold,
      limit,
    ];

    const result = await client.query(query, values);
    return result.rows;
  } finally {
    client.release();
  }
}

/**
 * Get a chunk by its ID
 */
export async function getChunkById(chunkId: string): Promise<ChunkRecord | null> {
  const client = await pool.connect();
  try {
    const query = 'SELECT * FROM chunks WHERE chunk_id = $1';
    const result = await client.query(query, [chunkId]);
    return result.rows[0] || null;
  } finally {
    client.release();
  }
}

/**
 * Get all chunks
 */
export async function getAllChunks(limit: number = 100, offset: number = 0): Promise<ChunkRecord[]> {
  const client = await pool.connect();
  try {
    const query = 'SELECT * FROM chunks ORDER BY created_at DESC LIMIT $1 OFFSET $2';
    const result = await client.query(query, [limit, offset]);
    return result.rows;
  } finally {
    client.release();
  }
}

/**
 * Delete a chunk by its ID
 */
export async function deleteChunk(chunkId: string): Promise<boolean> {
  const client = await pool.connect();
  try {
    const query = 'DELETE FROM chunks WHERE chunk_id = $1';
    const result = await client.query(query, [chunkId]);
    return result.rowCount !== null && result.rowCount > 0;
  } finally {
    client.release();
  }
}

/**
 * Get all chunks belonging to the same group (same recipe/document)
 * Ordered by chunk_index for proper reconstruction
 */
export async function getChunksByGroupId(groupId: string): Promise<ChunkRecord[]> {
  const client = await pool.connect();
  try {
    const query = `
      SELECT * FROM chunks
      WHERE metadata->>'group_id' = $1
      ORDER BY CAST(metadata->>'chunk_index' AS INTEGER) ASC
    `;
    const result = await client.query(query, [groupId]);
    return result.rows;
  } finally {
    client.release();
  }
}

/**
 * Get total count of chunks
 */
export async function getChunkCount(): Promise<number> {
  const client = await pool.connect();
  try {
    const query = 'SELECT COUNT(*) as count FROM chunks';
    const result = await client.query(query);
    return parseInt(result.rows[0].count);
  } finally {
    client.release();
  }
}

/**
 * Close the database connection pool
 */
export async function closePool(): Promise<void> {
  await pool.end();
}

export default pool;
