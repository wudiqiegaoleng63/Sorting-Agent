import { useState, useRef } from 'react';
import { uploadExcel } from '../api/agentApi';

interface Props {
  onUploaded: (filePath: string, filename: string) => void;
}

export default function FileUpload({ onUploaded }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadedName, setUploadedName] = useState('');
  const [error, setError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError('');
    try {
      const res = await uploadExcel(file);
      setUploadedName(res.filename);
      onUploaded(res.path, res.filename);
    } catch (e) {
      setError(e instanceof Error ? e.message : '上传失败');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card">
      <h3>上传 Excel 文件</h3>
      <div className="upload-row">
        <input
          ref={inputRef}
          type="file"
          accept=".xlsx,.xls,.csv"
          onChange={(e) => {
            setFile(e.target.files?.[0] || null);
            setUploadedName('');
            setError('');
          }}
        />
        <button onClick={handleUpload} disabled={!file || uploading}>
          {uploading ? '上传中...' : '上传文件'}
        </button>
      </div>
      {uploadedName && <p className="success">已上传: {uploadedName}</p>}
      {error && <p className="error">{error}</p>}
    </div>
  );
}
