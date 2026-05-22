import { useState, useRef, type KeyboardEvent } from 'react';
import type { UploadedFile } from '../types/agent';
import { uploadExcel } from '../api/agentApi';
import FileBadge from './FileBadge';

interface Props {
  loading: boolean;
  uploadedFile: UploadedFile | null;
  onFileUploaded: (file: UploadedFile) => void;
  onFileCleared: () => void;
  onSend: (task: string) => void;
}

export default function ChatInput({ loading, uploadedFile, onFileUploaded, onFileCleared, onSend }: Props) {
  const [text, setText] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls') && !file.name.endsWith('.csv')) {
      setUploadError('仅支持 .xlsx / .xls / .csv 文件');
      return;
    }

    setUploading(true);
    setUploadError('');
    try {
      const res = await uploadExcel(file);
      onFileUploaded({
        file_id: res.file_id,
        filename: res.filename,
        file_path: res.file_path,
        download_url: res.download_url,
      });
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : '上传失败');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;
    onSend(trimmed);
    setText('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-input-wrapper">
      {uploadedFile && <FileBadge filename={uploadedFile.filename} onClear={onFileCleared} />}
      {uploadError && <div className="upload-error">{uploadError}</div>}
      <div className="input-row">
        <button
          className="btn-attach"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading || loading}
          title="上传 Excel 文件"
        >
          {uploading ? '⏳' : '📎'}
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".xlsx,.xls,.csv"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <textarea
          className="chat-textarea"
          rows={1}
          placeholder="输入任务，例如：帮我查看这个 Excel 有哪些 sheet..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button
          className="btn-send"
          onClick={handleSend}
          disabled={!text.trim() || loading}
        >
          {loading ? '...' : '➤'}
        </button>
      </div>
    </div>
  );
}
