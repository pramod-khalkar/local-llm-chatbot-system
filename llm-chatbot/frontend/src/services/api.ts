import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // 300 seconds for LLM response
});

export interface ChatMessage {
  id: number;
  content: string;
  sender: 'user' | 'assistant';
  message_type: string;
  session_id: string;
  created_at: string;
  metadata?: Record<string, any>;
}

export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

export const chatService = {
  // Create a new chat session
  async createSession(title: string = 'New Chat'): Promise<ChatSession> {
    const response = await apiClient.post('/chat/sessions', null, {
      params: { title },
    });
    return response.data;
  },

  // Get a chat session
  async getSession(sessionId: string): Promise<ChatSession> {
    const response = await apiClient.get(`/chat/sessions/${sessionId}`);
    return response.data;
  },

  // Send a message
  async sendMessage(
    sessionId: string,
    message: string,
    useRag: boolean = true,
    useTools: boolean = true
  ): Promise<any> {
    const response = await apiClient.post('/chat/message', {
      message,
      session_id: sessionId,
      use_rag: useRag,
      use_tools: useTools,
    });
    return response.data;
  },

  // Get session messages
  async getMessages(sessionId: string, skip: number = 0, limit: number = 50): Promise<ChatMessage[]> {
    const response = await apiClient.get(`/chat/sessions/${sessionId}/messages`, {
      params: { skip, limit },
    });
    return response.data;
  },
};

export const speechService = {
  // Convert speech to text
  async speechToText(audioFile: File): Promise<string> {
    const formData = new FormData();
    formData.append('file', audioFile);
    const response = await apiClient.post('/speech/to-text', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data.text;
  },

  // Convert text to speech
  async textToSpeech(text: string, voice: string = 'default'): Promise<string> {
    const response = await apiClient.post('/speech/to-speech', {
      text,
      voice,
    });
    return response.data.audio_url;
  },
};

export const ragService = {
  // Search documents
  async search(query: string, topK: number = 5, threshold: number = 0.0): Promise<any> {
    const ragApiUrl = process.env.NEXT_PUBLIC_RAG_API_URL || 'http://localhost:8001/api';
    const response = await axios.post(`${ragApiUrl}/rag/search`, {
      query,
      top_k: topK,
      threshold,
    }, { timeout: 120000 });
    return response.data;
  },

  // Index documents
  async indexDocuments(documents: any[]): Promise<any> {
    const ragApiUrl = process.env.NEXT_PUBLIC_RAG_API_URL || 'http://localhost:8001/api';
    const response = await axios.post(`${ragApiUrl}/rag/index`, {
      documents,
    }, { timeout: 300000 });
    return response.data;
  },

  // Get RAG stats
  async getStats(): Promise<any> {
    const ragApiUrl = process.env.NEXT_PUBLIC_RAG_API_URL || 'http://localhost:8001/api';
    const response = await axios.get(`${ragApiUrl}/stats`, { timeout: 30000 });
    return response.data;
  },
};

export const configService = {
  // Get application configuration
  async getConfig(): Promise<{ model_name: string; environment: string; version: string }> {
    const response = await apiClient.get('/config');
    return response.data;
  },
};

export default apiClient;
