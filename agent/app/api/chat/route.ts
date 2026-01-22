import { openai } from '@ai-sdk/openai';
import { stepCountIs, streamText, tool } from 'ai';
import { z } from 'zod';
import { readFile } from 'fs/promises';
import { join } from 'path';
import { generateEmbedding, prepareTextForEmbedding } from '@/lib/ai/embeddings';
import { searchSimilarChunks, getChunksByGroupId } from '@/lib/db/pgvector';

// Force Node.js runtime (required for pg module)
export const runtime = 'nodejs';

// Define the recipe tool schema with Zod
const recipeToolSchema = z.object({
  query: z.string().describe('The user query about a recipe, ingredient, technique, or dish.'),
  category: z
    .string()
    .optional()
    .describe('Optional category filter (e.g., main dish, dessert, appetizer).'),
});

type RecipeToolInput = z.infer<typeof recipeToolSchema>;
type RecipeToolResult = {
  success: boolean;
  message: string;
  recipes: Array<{
    content: string;
    metadata: Record<string, any>;
    similarity: number;
    source: string;
    fullRecipe?: string;
  }>;
  query: string;
  category: string | null;
};

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();
    
    console.log('[Chat API] Received messages:', JSON.stringify(messages, null, 2));

    // Load system prompt from markdown file
    let systemPrompt: string;
    try {
      // Path relative to agent directory (go up one level to workspace root, then into assistant_config_docs)
      const systemPromptPath = join(process.cwd(), '..', 'assistant_config_docs', 'system_prompt.md');
      const systemPromptContent = await readFile(systemPromptPath, 'utf-8');
      // Keep the markdown content as-is (headers and all) - the LLM can handle it
      systemPrompt = systemPromptContent;
    } catch (error) {
      console.warn('[Chat API] Failed to load system_prompt.md, using fallback:', error);
      // Fallback to inline prompt if file read fails
      systemPrompt = `You are a helpful recipe assistant. When users ask about recipes, ingredients, substitutions, \
      or cooking instructions, use the recipe tool to search the recipe database (pgvector). \
      \
      After receiving recipe results:
      1. Analyze the recipes provided \
      2. Present the information in a clear, organized way \
      3. Include relevant details like ingredients, instructions, and cooking tips \
      4. If multiple recipes are found, summarize the options \
      5. Be conversational and helpful \
      \
      If no recipes are found, suggest alternative search terms or related recipes the user might be interested in.`;
    }

    // Stream the response from OpenAI with tool definitions
    const result = streamText({
      model: openai('gpt-4o'),
      messages,
      onFinish: ({ text, toolCalls, toolResults, finishReason, usage }) => {
        console.log('[Chat API] Stream finished');
        console.log('[Chat API] Final text:', text);
        console.log('[Chat API] Tool calls:', toolCalls?.length || 0);
        console.log('[Chat API] Tool results:', toolResults?.length || 0);
        console.log('[Chat API] Finish reason:', finishReason);
        console.log('[Chat API] Usage:', usage);
      },
      tools: {
        recipe: tool<RecipeToolInput, RecipeToolResult>({
          description:
            'Search the recipe knowledge base (pgvector) for relevant recipe content. Use this tool when the user \
            asks about recipes, ingredients, cooking instructions, substitutions, or food-related questions that \
            require the stored recipe data.',
          inputSchema: recipeToolSchema,
          execute: async ({ query, category }: RecipeToolInput): Promise<RecipeToolResult> => {
            const categoryNormalized = category ?? null;
            console.log(`[Recipe Tool] Searching for: "${query}", category: ${categoryNormalized || 'any'}`);

            try {
              // Generate embedding for the user query
              const prepared = prepareTextForEmbedding(query);
              const queryNormalized = prepared || query || '';

              if (!prepared) {
                return {
                  success: false,
                  message: 'Your query was empty after cleaning. Please provide recipe details.',
                  recipes: [],
                  query: queryNormalized,
                  category: categoryNormalized,
                };
              }

              const queryEmbedding = await generateEmbedding(prepared);

              // Search for similar recipes in pgvector database
              const similarChunks = await searchSimilarChunks(
                queryEmbedding,
                5, // limit to top 5 results
                0.7 // similarity threshold
              );

              console.log(`[Recipe Tool] Found ${similarChunks.length} similar recipes`);

              if (similarChunks.length === 0) {
                return {
                  success: false,
                  message: 'No recipes found matching your query. Please try different keywords.',
                  recipes: [],
                  query: queryNormalized,
                  category: categoryNormalized,
                };
              }

              // Format the results for the LLM and fetch full recipes
              const recipes = await Promise.all(similarChunks.map(async (chunk) => {
                let fullRecipe: string | undefined;
                
                // If the chunk has a group_id, fetch all chunks from the same group
                if (chunk.metadata?.group_id) {
                  try {
                    const groupChunks = await getChunksByGroupId(chunk.metadata.group_id);
                    
                    // Reconstruct the full recipe by concatenating all chunks in order
                    fullRecipe = groupChunks.map(c => c.content).join('\n\n');
                    
                    console.log(`[Recipe Tool] Reconstructed full recipe for group ${chunk.metadata.group_id}: ${groupChunks.length} chunks`);
                  } catch (error) {
                    console.error(`[Recipe Tool] Error fetching full recipe for group ${chunk.metadata.group_id}:`, error);
                  }
                }
                
                return {
                  content: chunk.content,
                  metadata: chunk.metadata,
                  similarity: chunk.similarity,
                  source: chunk.metadata?.source || 'Unknown',
                  fullRecipe,
                };
              }));

              const result = {
                success: true,
                message: `Found ${recipes.length} relevant recipe(s)`,
                recipes,
                query: queryNormalized,
                category: categoryNormalized,
              };
              
              console.log('[Recipe Tool] Returning result:', JSON.stringify(result, null, 2));
              return result;
            } catch (error) {
              console.error('[Recipe Tool] Error:', error);
              return {
                success: false,
                message: 'Error searching recipes: ' + (error instanceof Error ? error.message : 'Unknown error'),
                recipes: [],
                query: query || '',
                category: categoryNormalized,
              };
            }
          },
        }),
      },
      // Allow multi-step tool calling: model -> tool -> model (and repeats if needed).
      stopWhen: stepCountIs(5),
      system: systemPrompt,
    });

    console.log('[Chat API] Starting stream...');
    
    // Return the text stream response
    return result.toTextStreamResponse();
  } catch (error) {
    console.error('[Chat API] Error:', error);
    return new Response(
      JSON.stringify({
        error: error instanceof Error ? error.message : 'Internal server error',
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
}
