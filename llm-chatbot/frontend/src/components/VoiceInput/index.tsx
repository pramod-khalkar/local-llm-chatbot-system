'use client';

import React from 'react';
import { useVoice, useTextToSpeech } from '@/hooks/useVoice';
import { Mic, MicOff, Volume2, VolumeX } from 'lucide-react';

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  disabled: boolean;
}

export const VoiceInput: React.FC<VoiceInputProps> = ({ onTranscript, disabled }) => {
  const {
    isListening,
    transcript,
    startListening,
    stopListening,
    resetTranscript,
  } = useVoice();

  const { isSpeaking, speak, stop: stopSpeaking } = useTextToSpeech();

  const handleSendVoice = () => {
    if (transcript.trim()) {
      onTranscript(transcript.trim());
      resetTranscript();
    }
  };

  return (
    <div className="flex gap-2 flex-wrap items-center">
      <button
        onClick={isListening ? stopListening : startListening}
        disabled={disabled}
        className={`p-2 rounded-full transition-all ${
          isListening
            ? 'bg-red-500 hover:bg-red-600'
            : 'bg-purple-500 hover:bg-purple-600'
        } text-white disabled:opacity-50 disabled:cursor-not-allowed`}
        title={isListening ? 'Stop listening' : 'Start listening'}
      >
        {isListening ? <MicOff size={20} /> : <Mic size={20} />}
      </button>

      {transcript && (
        <div className="flex-1 bg-white bg-opacity-10 rounded px-3 py-2 text-white text-sm">
          {transcript}
        </div>
      )}

      {transcript && (
        <button
          onClick={handleSendVoice}
          disabled={disabled}
          className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded transition-all disabled:opacity-50"
        >
          Send
        </button>
      )}
    </div>
  );
};
