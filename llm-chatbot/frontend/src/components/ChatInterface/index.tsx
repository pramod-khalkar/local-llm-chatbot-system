'use client';

import React, { useEffect, useState } from 'react';
import { MessageList } from '@/components/MessageList';
import { VoiceInput } from '@/components/VoiceInput';
import DocumentUpload from '@/components/DocumentUpload';
import { useChat } from '@/hooks/useChat';
import { Send } from 'lucide-react';

export const ChatInterface: React.FC = () => {
  const [inputValue, setInputValue] = useState('');
  const [useRag, setUseRag] = useState(true);
  const [useTools, setUseTools] = useState(true);
  const [uploadNotification, setUploadNotification] = useState('');
  
  const { session, messages, loading, error, createSession, sendMessage } = useChat();

  useEffect(() => {
    // Create initial session
    createSession('LLM Chatbot Session');
  }, [createSession]);

  const handleSendMessage = async (text?: string) => {
    const messageText = text || inputValue.trim();
    if (!messageText || loading) return;

    await sendMessage(messageText);
    setInputValue('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleUploadComplete = () => {
    setUploadNotification('✅ Documents uploaded successfully! Use "according to" or "based on" keywords in your questions to search them.');
    setTimeout(() => setUploadNotification(''), 5000);
  };

  return (
    <div className="flex flex-col h-screen max-h-screen bg-gradient-to-br from-purple-600 to-blue-600">
      {/* Header */}
      <div className="bg-black bg-opacity-30 backdrop-blur px-6 py-4 border-b border-white border-opacity-10 flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-white">🤖 LLM Chatbot</h1>
          <p className="text-sm text-gray-200">
            Powered by Llama 3.1 • RAG Enabled • Tool Integration
          </p>
        </div>
        <DocumentUpload onUploadComplete={handleUploadComplete} />
      </div>

      {/* Upload Notification */}
      {uploadNotification && (
        <div className="bg-green-500 bg-opacity-90 text-white px-4 py-2 text-sm">
          {uploadNotification}
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-500 bg-opacity-90 text-white px-4 py-2 text-sm">
          ⚠️ {error}
        </div>
      )}

      {/* Message List */}
      <MessageList messages={messages} loading={loading} />

      {/* Input Area */}
      <div className="bg-black bg-opacity-50 backdrop-blur border-t border-white border-opacity-10 p-4 space-y-3">
        {/* Options */}
        <div className="flex gap-4 text-xs text-gray-200">
          <label className="flex items-center gap-2 cursor-pointer hover:text-white transition">
            <input
              type="checkbox"
              checked={useRag}
              onChange={(e) => setUseRag(e.target.checked)}
              disabled={loading}
              className="w-4 h-4 cursor-pointer"
            />
            📚 Use RAG
          </label>
          <label className="flex items-center gap-2 cursor-pointer hover:text-white transition">
            <input
              type="checkbox"
              checked={useTools}
              onChange={(e) => setUseTools(e.target.checked)}
              disabled={loading}
              className="w-4 h-4 cursor-pointer"
            />
            🛠️ Use Tools
          </label>
        </div>

        {/* Voice Input */}
        <VoiceInput onTranscript={handleSendMessage} disabled={loading} />

        {/* Text Input */}
        <div className="flex gap-2">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message... (Shift+Enter for new line)"
            disabled={loading || !session}
            rows={2}
            className="flex-1 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg px-4 py-2 text-white placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
          <button
            onClick={() => handleSendMessage()}
            disabled={loading || !inputValue.trim() || !session}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-semibold"
          >
            <Send size={20} />
            Send
          </button>
        </div>

        <p className="text-xs text-gray-400 text-center">
          💡 Tip: Use voice input for hands-free interaction or upload documents for RAG search
        </p>
      </div>
    </div>
  );
};
