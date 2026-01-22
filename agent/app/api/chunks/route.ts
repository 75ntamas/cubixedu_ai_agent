import { NextRequest, NextResponse } from 'next/server';
import { generateEmbedding, prepareTextForEmbedding } from '@/lib/ai/embeddings';
import {
  insertChunkWithEmbedding,
  getAllChunks,
  getChunkById,
  getChunkCount,
  searchSimilarChunks
} from '@/lib/db/pgvector';

// Force Node.js runtime (required for pg module)
export const runtime = 'nodejs';

interface ChunkData {
  chunk_id: string;
  content: string;
  metadata: {
    source: string;
    group_id: string;
    chunk_index: number;
    total_chunks: number;
    [key: string]: any;
  };
}

/**
 * POST /api/chunks
 * Create a new chunk with embedding and store it in the database
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Validate the incoming data
    if (!body.chunk_id || !body.content) {
      return NextResponse.json(
        { error: 'Missing required fields: chunk_id and content' },
        { status: 400 }
      );
    }

    const chunkData: ChunkData = {
      chunk_id: body.chunk_id,
      content: body.content,
      metadata: body.metadata || {}
    };

    console.log(`Processing chunk: ${chunkData.chunk_id}`);

    // Prepare text for embedding
    const preparedText = prepareTextForEmbedding(chunkData.content);

    // Generate embedding using OpenAI
    console.log(`Generating embedding for chunk: ${chunkData.chunk_id}`);
    const embedding = await generateEmbedding(preparedText);

    // Store chunk with embedding in database
    console.log(`Storing chunk in database: ${chunkData.chunk_id}`);
    const savedChunk = await insertChunkWithEmbedding({
      chunk_id: chunkData.chunk_id,
      content: chunkData.content,
      embedding: embedding,
      metadata: chunkData.metadata
    });

    console.log(`Successfully stored chunk: ${chunkData.chunk_id}`);
    
    return NextResponse.json(
      {
        success: true,
        message: 'Chunk received and embedded successfully',
        chunk_id: savedChunk.chunk_id,
        embedding_dimensions: embedding.length
      },
      { status: 201 }
    );
  } catch (error) {
    console.error('Error processing chunk:', error);
    return NextResponse.json(
      { error: `Internal server error: ${error instanceof Error ? error.message : 'Unknown error'}` },
      { status: 500 }
    );
  }
}

/**
 * GET /api/chunks
 * Retrieve chunks from the database
 * Query params:
 * - limit: number of chunks to retrieve (default: 100)
 * - offset: offset for pagination (default: 0)
 * - chunk_id: retrieve a specific chunk by ID
 * - search: text to search for similar chunks
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const chunkId = searchParams.get('chunk_id');
    const searchText = searchParams.get('search');
    const limit = parseInt(searchParams.get('limit') || '100');
    const offset = parseInt(searchParams.get('offset') || '0');

    // If chunk_id is provided, return that specific chunk
    if (chunkId) {
      const chunk = await getChunkById(chunkId);
      if (!chunk) {
        return NextResponse.json(
          { error: 'Chunk not found' },
          { status: 404 }
        );
      }
      return NextResponse.json({ chunk }, { status: 200 });
    }

    // If search text is provided, perform similarity search
    if (searchText) {
      const preparedText = prepareTextForEmbedding(searchText);
      const searchEmbedding = await generateEmbedding(preparedText);
      const similarChunks = await searchSimilarChunks(searchEmbedding, limit);
      
      return NextResponse.json(
        {
          search_query: searchText,
          results: similarChunks.length,
          chunks: similarChunks
        },
        { status: 200 }
      );
    }

    // Otherwise, return all chunks with pagination
    const chunks = await getAllChunks(limit, offset);
    const totalCount = await getChunkCount();

    return NextResponse.json(
      {
        total_chunks: totalCount,
        returned_chunks: chunks.length,
        limit,
        offset,
        chunks: chunks
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Error retrieving chunks:', error);
    return NextResponse.json(
      { error: `Internal server error: ${error instanceof Error ? error.message : 'Unknown error'}` },
      { status: 500 }
    );
  }
}
