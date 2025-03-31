import { Redis } from 'ioredis';
import { VectorStore } from '../vector/VectorStore';
import { Agent } from './AgentRegistry';

interface MemoryEntry {
  id: string;
  content: string;
  type: 'conversation' | 'code' | 'decision' | 'context';
  metadata: {
    timestamp: number;
    agentId: string;
    projectId: string;
    tags: string[];
    importance: 'low' | 'medium' | 'high';
    relatedEntries: string[];
  };
  embedding?: number[];
}

interface MemoryQuery {
  projectId: string;
  type?: MemoryEntry['type'];
  tags?: string[];
  startTime?: number;
  endTime?: number;
  limit?: number;
  importance?: MemoryEntry['metadata']['importance'];
}

export class AgentMemoryService {
  private redis: Redis;
  private vectorStore: VectorStore;
  private readonly MEMORY_PREFIX = 'agent:memory:';
  private readonly CONTEXT_PREFIX = 'agent:context:';
  private readonly MAX_CONTEXT_SIZE = 1000;

  constructor(redisUrl: string, vectorStoreUrl: string) {
    this.redis = new Redis(redisUrl);
    this.vectorStore = new VectorStore(vectorStoreUrl);
  }

  public async storeMemory(entry: MemoryEntry): Promise<void> {
    // Store in Redis for quick access
    const key = `${this.MEMORY_PREFIX}${entry.id}`;
    await this.redis.hset(key, {
      content: entry.content,
      type: entry.type,
      metadata: JSON.stringify(entry.metadata),
      embedding: entry.embedding ? JSON.stringify(entry.embedding) : null
    });

    // Store in vector store for semantic search
    if (entry.embedding) {
      await this.vectorStore.add(entry.id, entry.embedding, {
        content: entry.content,
        type: entry.type,
        metadata: entry.metadata
      });
    }

    // Update context for the agent
    await this.updateAgentContext(entry.metadata.agentId, entry);
  }

  public async retrieveMemory(query: MemoryQuery): Promise<MemoryEntry[]> {
    const keys = await this.redis.keys(`${this.MEMORY_PREFIX}*`);
    const memories: MemoryEntry[] = [];

    for (const key of keys) {
      const data = await this.redis.hgetall(key);
      if (!data || Object.keys(data).length === 0) continue;

      const metadata = JSON.parse(data.metadata);
      if (this.matchesQuery(metadata, query)) {
        memories.push({
          id: key.replace(this.MEMORY_PREFIX, ''),
          content: data.content,
          type: data.type as MemoryEntry['type'],
          metadata,
          embedding: data.embedding ? JSON.parse(data.embedding) : undefined
        });
      }
    }

    return memories.sort((a, b) => b.metadata.timestamp - a.metadata.timestamp)
      .slice(0, query.limit || 10);
  }

  public async searchSimilarMemories(
    query: string,
    projectId: string,
    limit: number = 5
  ): Promise<MemoryEntry[]> {
    const queryEmbedding = await this.vectorStore.getEmbedding(query);
    const results = await this.vectorStore.search(queryEmbedding, {
      filter: { projectId },
      limit
    });

    return Promise.all(
      results.map(async (result) => {
        const key = `${this.MEMORY_PREFIX}${result.id}`;
        const data = await this.redis.hgetall(key);
        return {
          id: result.id,
          content: data.content,
          type: data.type as MemoryEntry['type'],
          metadata: JSON.parse(data.metadata),
          embedding: data.embedding ? JSON.parse(data.embedding) : undefined
        };
      })
    );
  }

  public async getAgentContext(agentId: string): Promise<MemoryEntry[]> {
    const contextKey = `${this.CONTEXT_PREFIX}${agentId}`;
    const contextIds = await this.redis.lrange(contextKey, 0, -1);
    
    return Promise.all(
      contextIds.map(async (id) => {
        const key = `${this.MEMORY_PREFIX}${id}`;
        const data = await this.redis.hgetall(key);
        return {
          id,
          content: data.content,
          type: data.type as MemoryEntry['type'],
          metadata: JSON.parse(data.metadata),
          embedding: data.embedding ? JSON.parse(data.embedding) : undefined
        };
      })
    );
  }

  private async updateAgentContext(agentId: string, entry: MemoryEntry): Promise<void> {
    const contextKey = `${this.CONTEXT_PREFIX}${agentId}`;
    
    // Add new entry to the beginning of the list
    await this.redis.lpush(contextKey, entry.id);
    
    // Trim the list to maintain maximum size
    await this.redis.ltrim(contextKey, 0, this.MAX_CONTEXT_SIZE - 1);
  }

  private matchesQuery(metadata: MemoryEntry['metadata'], query: MemoryQuery): boolean {
    if (metadata.projectId !== query.projectId) return false;
    if (query.type && metadata.type !== query.type) return false;
    if (query.tags && !query.tags.every(tag => metadata.tags.includes(tag))) return false;
    if (query.startTime && metadata.timestamp < query.startTime) return false;
    if (query.endTime && metadata.timestamp > query.endTime) return false;
    if (query.importance && metadata.importance !== query.importance) return false;
    return true;
  }

  public async summarizeContext(agentId: string): Promise<string> {
    const context = await this.getAgentContext(agentId);
    const importantEntries = context
      .filter(entry => entry.metadata.importance === 'high')
      .sort((a, b) => b.metadata.timestamp - a.metadata.timestamp)
      .slice(0, 5);

    return importantEntries
      .map(entry => `${entry.type.toUpperCase()}: ${entry.content}`)
      .join('\n');
  }

  public async clearAgentContext(agentId: string): Promise<void> {
    const contextKey = `${this.CONTEXT_PREFIX}${agentId}`;
    await this.redis.del(contextKey);
  }

  public async deleteMemory(entryId: string): Promise<void> {
    const key = `${this.MEMORY_PREFIX}${entryId}`;
    await this.redis.del(key);
    await this.vectorStore.delete(entryId);
  }
} 