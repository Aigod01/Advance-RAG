import React, { useEffect, useState } from 'react';
import {
  FileText,
  Upload,
  RefreshCw,
  CheckCircle2,
  File,
  Layers,
  HardDrive
} from 'lucide-react';
import { DocumentInfo } from '../types';
import { listDocuments, uploadDocument } from '../api/client';

export const DocumentUpload: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const data = await listDocuments();
      setDocuments(data);
    } catch (e) {
      console.error('Failed to load documents', e);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    setUploadMessage(null);
    try {
      const res = await uploadDocument(selectedFile);
      setUploadMessage(`Successfully indexed ${res.filename} (${res.chunks} chunks)`);
      setSelectedFile(null);
      fetchDocs();
    } catch (err: any) {
      setUploadMessage(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto py-2">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2.5">
            <FileText className="w-6 h-6 text-emerald-400" />
            <span>Corporate Knowledge Document Corpus</span>
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Section-aware parsed internal PDF, Markdown, and TXT files indexed in Qdrant Vector Store and Lexical BM25.
          </p>
        </div>
        <button
          onClick={fetchDocs}
          disabled={loading}
          className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium border border-slate-700 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Corpus</span>
        </button>
      </div>

      {/* Upload Box */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl">
        <h3 className="text-sm font-semibold text-slate-200 mb-3 flex items-center space-x-2">
          <Upload className="w-4 h-4 text-emerald-400" />
          <span>Upload & Ingest New Document</span>
        </h3>

        <form onSubmit={handleFileUpload} className="flex flex-col sm:flex-row gap-3 items-center">
          <input
            type="file"
            accept=".pdf,.md,.txt,.docx,.doc"
            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
            className="block w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-emerald-600 file:text-white hover:file:bg-emerald-500 cursor-pointer bg-slate-950 p-2 rounded-xl border border-slate-800"
          />
          <button
            type="submit"
            disabled={!selectedFile || uploading}
            className="w-full sm:w-auto px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-emerald-600/30 transition disabled:opacity-50 whitespace-nowrap"
          >
            {uploading ? 'Chunking & Indexing...' : 'Index Document'}
          </button>
        </form>

        {uploadMessage && (
          <div className="mt-3 p-3 rounded-xl bg-slate-950 border border-emerald-500/30 text-xs text-emerald-400 flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
            <span>{uploadMessage}</span>
          </div>
        )}
      </div>

      {/* Document Catalog Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl">
        <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <Layers className="w-5 h-5 text-blue-400" />
            <h3 className="font-semibold text-sm text-slate-200">
              Active Ingested Documents
            </h3>
          </div>
          <span className="text-xs font-mono text-slate-400">
            Total: {documents.length} files
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 font-mono uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-3 px-3">Filename</th>
                <th className="py-3 px-3">Title</th>
                <th className="py-3 px-3">Document ID</th>
                <th className="py-3 px-3">Chunks</th>
                <th className="py-3 px-3">Characters</th>
                <th className="py-3 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {documents.map((doc, idx) => (
                <tr key={doc.document_id || idx} className="hover:bg-slate-800/30 transition">
                  <td className="py-3 px-3 font-mono font-medium text-emerald-400 flex items-center space-x-2">
                    <File className="w-3.5 h-3.5 text-slate-500" />
                    <span>{doc.filename}</span>
                  </td>
                  <td className="py-3 px-3 text-slate-300">
                    {doc.title}
                  </td>
                  <td className="py-3 px-3 font-mono text-[11px] text-slate-500">
                    {doc.document_id}
                  </td>
                  <td className="py-3 px-3 font-mono text-purple-300 font-bold">
                    {doc.chunks}
                  </td>
                  <td className="py-3 px-3 font-mono text-slate-400">
                    {doc.char_count?.toLocaleString()}
                  </td>
                  <td className="py-3 px-3">
                    <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-semibold">
                      Indexed
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
