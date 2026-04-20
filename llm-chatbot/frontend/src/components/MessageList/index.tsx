'use client';

import React, { useEffect, useRef, useState } from 'react';
import { ChatMessage } from '@/services/api';
import { ChevronDown, ChevronUp, BookOpen } from 'lucide-react';

interface MessageListProps {
  messages: ChatMessage[];
  loading: boolean;
}

interface ExpandedMessages {
  [key: number]: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({ messages, loading }) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [expanded, setExpanded] = useState<ExpandedMessages>({});

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const toggleExpanded = (msgId: number) => {
    setExpanded((prev) => ({
      ...prev,
      [msgId]: !prev[msgId],
    }));
  };

  return (
    <div
      ref={scrollRef}
      className="flex-1 overflow-y-auto p-4 space-y-4 bg-white bg-opacity-5"
    >
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-full text-white text-center">
          <div>
            <p className="text-2xl font-bold mb-2">👋 Welcome to LLM Chatbot</p>
            <p className="text-sm opacity-80">
              Start a conversation. You can chat, use voice, or upload documents for RAG search.
            </p>
            <p className="text-xs opacity-60 mt-4">
              💡 After uploading documents, use keywords like "according to" or "based on" to search them
            </p>
          </div>
        </div>
      ) : (
        messages.map((msg) => {
          const hasSources = msg.metadata?.sources && msg.metadata.sources.length > 0;
          const isExpanded = expanded[msg.id];

          return (
            <div
              key={msg.id}
              className={`chat-message-fade flex ${
                msg.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-md rounded-lg overflow-hidden ${
                  msg.sender === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-800 text-gray-100 border border-gray-600'
                }`}
              >
                {/* Message Content */}
                <div className="px-4 py-3">
                  <p className="text-sm leading-relaxed">{msg.content}</p>
                </div>

                {/* Sources Section */}
                {hasSources && (
                  <div className="bg-black bg-opacity-20 border-t border-gray-600">
                    <button
                      onClick={() => toggleExpanded(msg.id)}
                      className="w-full px-4 py-2 flex items-center justify-between text-xs font-semibold hover:bg-black hover:bg-opacity-10 transition"
                    >
                      <span className="flex items-center gap-1.5">
                        <BookOpen size={14} />
                        📚 Sources ({msg.metadata?.sources?.length || 0})
                      </span>
                      {isExpanded ? (
                        <ChevronUp size={14} />
                      ) : (
                        <ChevronDown size={14} />
                      )}
                    </button>

                    {/* Expanded Sources */}
                    {isExpanded && (
                      <div className="px-4 py-2 space-y-1.5 bg-black bg-opacity-10">
                        {msg.metadata?.sources?.map((source: string, idx: number) => (
                          <div
                            key={idx}
                            className="text-xs bg-gray-900 bg-opacity-50 p-2 rounded border border-gray-600 line-clamp-3 hover:line-clamp-none transition"
                          >
                            <p className="text-gray-300 leading-relaxed">{source}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })
      )}

      {loading && (
        <div className="flex justify-start">
          <div className="bg-gray-800 text-gray-300 rounded-lg px-4 py-2 border border-gray-600">
            <div className="flex space-x-2">
              <div className="w-2 h-2 bg-blue-400 rounded-full spinner"></div>
              <div
                className="w-2 h-2 bg-blue-400 rounded-full spinner"
                style={{ animationDelay: '0.1s' }}
              ></div>
              <div
                className="w-2 h-2 bg-blue-400 rounded-full spinner"
                style={{ animationDelay: '0.2s' }}
              ></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
