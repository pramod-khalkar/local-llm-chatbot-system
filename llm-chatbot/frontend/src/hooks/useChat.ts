'use client';

import { useState, useCallback } from 'react';
import { chatService, ChatMessage, ChatSession } from '@/services/api';

export const useChat = () => {
  const [session, setSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createSession = useCallback(async (title?: string) => {
    try {
      setLoading(true);
      const newSession = await chatService.createSession(title);
      setSession(newSession);
      setMessages([]);
      setError(null);
      return newSession;
    } catch (err: any) {
      setError(err.message);
      console.error('Error creating session:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadSession = useCallback(async (sessionId: string) => {
    try {
      setLoading(true);
      const loadedSession = await chatService.getSession(sessionId);
      setSession(loadedSession);
      setMessages(loadedSession.messages);
      setError(null);
      return loadedSession;
    } catch (err: any) {
      setError(err.message);
      console.error('Error loading session:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const sendMessage = useCallback(async (message: string) => {
    if (!session) {
      setError('No active session');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Add user message optimistically
      const userMsg: ChatMessage = {
        id: Date.now(),
        content: message,
        sender: 'user',
        message_type: 'text',
        session_id: session.id,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);

      // Get AI response
      const response = await chatService.sendMessage(session.id, message);

      // Add assistant message
      const assistantMsg: ChatMessage = {
        id: response.message_id,
        content: response.response,
        sender: 'assistant',
        message_type: 'text',
        session_id: session.id,
        created_at: new Date().toISOString(),
        metadata: {
          sources: response.sources,
          tool_calls: response.tool_calls,
        },
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setError(err.message);
      console.error('Error sending message:', err);
    } finally {
      setLoading(false);
    }
  }, [session]);

  return {
    session,
    messages,
    loading,
    error,
    createSession,
    loadSession,
    sendMessage,
  };
};
