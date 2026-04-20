'use client';

import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Upload, X } from 'lucide-react';

interface DocumentUploadProps {
  onUploadComplete?: () => void;
}

interface FileData {
  id: string;
  name: string;
  size: number;
  type: string;
}

interface Stats {
  total_vectors: number;
  dimension: number;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadComplete }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [documents, setDocuments] = useState<FileData[]>([]);
  const [isIndexing, setIsIndexing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [isMounted, setIsMounted] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Ensure component is mounted before rendering portal
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Dynamically import pdf.js to avoid DOMMatrix build-time errors
  const pdfjsLoader = async (file: File): Promise<string> => {
    try {
      const { getDocument } = await import('pdfjs-dist');
      const pdfjs = await import('pdfjs-dist');
      pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js`;

      const arrayBuffer = await file.arrayBuffer();
      const pdf = await getDocument({ data: arrayBuffer }).promise;
      let fullText = '';

      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();
        const pageText = textContent.items.map((item: any) => item.str).join(' ');
        fullText += pageText + ' ';
      }
      return fullText;
    } catch (error) {
      console.error('Error extracting PDF:', error);
      throw new Error('Failed to extract PDF text');
    }
  };

  const extractPdfText = async (file: File): Promise<string> => {
    try {
      return await pdfjsLoader(file);
    } catch (error) {
      console.error('PDF extraction error:', error);
      throw error;
    }
  };

  const handleFileUpload = async (files: FileList) => {
    try {
      setError('');
      const newDocuments: FileData[] = [];
      let processed = 0;

      for (let i = 0; i < files.length; i++) {
        const file = files[i];

        const supportedTypes = ['.txt', '.md', '.pdf'];
        const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();

        if (!supportedTypes.includes(fileExt)) {
          console.warn(`Skipped unsupported file: ${file.name}`);
          continue;
        }

        newDocuments.push({
          id: `doc-${Date.now()}-${i}`,
          name: file.name,
          size: file.size,
          type: file.type || fileExt
        });

        processed++;
        setUploadProgress((processed / files.length) * 100);
      }

      if (newDocuments.length === 0) {
        setError('No supported files found. Supported formats: .txt, .md, .pdf');
        return;
      }

      setDocuments([...documents, ...newDocuments]);
      setSuccess(`${newDocuments.length} file(s) selected`);
      setUploadProgress(0);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'File upload failed';
      setError(message);
      setUploadProgress(0);
    }
  };

  const handleIndexDocuments = async () => {
    if (documents.length === 0) {
      setError('No documents to index');
      return;
    }

    try {
      setIsIndexing(true);
      setError('');
      setSuccess('');

      const fileInput = fileInputRef.current;
      if (!fileInput?.files) {
        setError('No files available');
        setIsIndexing(false);
        return;
      }

      const documentsArray = [];
      let filesAdded = 0;

      for (const doc of documents) {
        for (let i = 0; i < fileInput.files.length; i++) {
          const file = fileInput.files[i];
          if (file.name === doc.name) {
            let content: string;

            if (doc.type === 'pdf' || file.name.endsWith('.pdf')) {
              content = await extractPdfText(file);
            } else {
              content = await file.text();
            }

            documentsArray.push({
              content: content,
              metadata: {
                filename: file.name,
                content_type: file.type || 'text/plain'
              }
            });
            filesAdded++;
            break;
          }
        }
      }

      if (filesAdded === 0) {
        setError('Could not process files');
        setIsIndexing(false);
        return;
      }

      const response = await fetch('http://localhost:8001/api/rag/index', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ documents: documentsArray })
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const result = await response.json();
      setSuccess(`✅ Indexed ${result.indexed_count} document(s). Total vectors: ${result.total_vectors}`);
      setStats({
        total_vectors: result.total_vectors,
        dimension: result.dimension || 768
      });

      setDocuments([]);
      setUploadProgress(0);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      onUploadComplete?.();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Indexing failed';
      setError(message);
      console.error('Indexing error:', err);
    } finally {
      setIsIndexing(false);
    }
  };

  const removeDocument = (id: string) => {
    setDocuments(documents.filter(doc => doc.id !== id));
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const modalContent = (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={() => setIsOpen(false)}
      />

      {/* Modal */}
      <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
        <div
          className="w-full max-w-md bg-gray-900 rounded-lg shadow-2xl border border-gray-700"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex justify-between items-center p-6 border-b border-gray-700">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <Upload size={18} />
              Upload Documents
            </h3>
            <button
              onClick={() => setIsOpen(false)}
              className="text-gray-400 hover:text-white transition"
            >
              <X size={20} />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 max-h-96 overflow-y-auto space-y-4">
            {/* Current Index Status */}
            {stats && (
              <div className="bg-gray-800 rounded p-3 text-sm text-gray-300 border border-gray-700">
                <div className="flex justify-between mb-2">
                  <span>📚 Documents Indexed:</span>
                  <span className="font-semibold text-white">{stats.total_vectors}</span>
                </div>
                <div className="flex justify-between">
                  <span>📏 Vector Dimension:</span>
                  <span className="font-semibold text-white">{stats.dimension}D</span>
                </div>
              </div>
            )}

            {/* Error Messages */}
            {error && (
              <div className="p-3 bg-red-900 border border-red-700 rounded text-red-200 text-sm">
                ❌ {error}
              </div>
            )}

            {/* Success Messages */}
            {success && (
              <div className="p-3 bg-green-900 border border-green-700 rounded text-green-200 text-sm">
                {success}
              </div>
            )}

            {/* File Input */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Select Documents
              </label>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".txt,.md,.pdf"
                onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
                className="w-full text-xs text-gray-400 file:mr-2 file:py-2 file:px-3 file:rounded file:border-0 file:text-xs file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 hover:file:cursor-pointer"
              />
              <p className="text-xs text-gray-400 mt-1">📄 Supported: .txt, .md, .pdf</p>
            </div>

            {/* Upload Progress */}
            {uploadProgress > 0 && (
              <div>
                <div className="flex justify-between text-xs text-gray-400 mb-2">
                  <span>Progress</span>
                  <span>{Math.round(uploadProgress)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Documents List */}
            {documents.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Selected Documents ({documents.length})
                </label>
                <div className="space-y-2">
                  {documents.map((doc) => (
                    <div
                      key={doc.id}
                      className="flex items-center justify-between p-3 bg-gray-800 rounded text-sm border border-gray-700"
                    >
                      <div className="flex-1 min-w-0">
                        <p className="text-gray-200 truncate font-medium">{doc.name}</p>
                        <p className="text-gray-500 text-xs">{formatFileSize(doc.size)}</p>
                      </div>
                      <button
                        onClick={() => removeDocument(doc.id)}
                        className="ml-2 text-gray-400 hover:text-red-400 transition"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Footer with Buttons */}
          <div className="bg-gray-800 border-t border-gray-700 p-6 flex gap-2">
            <button
              onClick={handleIndexDocuments}
              disabled={documents.length === 0 || isIndexing}
              className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-semibold py-2 px-4 rounded transition disabled:cursor-not-allowed"
            >
              {isIndexing ? '⏳ Indexing...' : '🚀 Index Documents'}
            </button>
            <button
              onClick={() => setIsOpen(false)}
              disabled={isIndexing}
              className="flex-1 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-600 text-white font-semibold py-2 px-4 rounded transition disabled:cursor-not-allowed"
            >
              Close
            </button>
          </div>

          {/* Helper Text */}
          <div className="bg-gray-800 border-t border-gray-700 p-4 text-center">
            <p className="text-xs text-gray-400">
              💡 After indexing, use keywords like "according to" or "based on" to search documents
            </p>
          </div>
        </div>
      </div>
    </>
  );

  return (
    <>
      {/* Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-semibold rounded-lg flex items-center gap-2 transition-colors shadow-lg hover:shadow-xl"
      >
        <Upload size={18} />
        📤 Upload Docs
      </button>

      {/* Portal - Render modal at document root */}
      {isMounted && isOpen && createPortal(modalContent, document.body)}
    </>
  );
};

export default DocumentUpload;
