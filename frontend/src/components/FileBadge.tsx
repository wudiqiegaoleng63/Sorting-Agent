interface Props {
  filename: string;
  onClear: () => void;
}

export default function FileBadge({ filename, onClear }: Props) {
  return (
    <div className="file-badge">
      <span className="file-badge-name">📎 {filename}</span>
      <button className="file-badge-clear" onClick={onClear} title="移除文件">
        ✕
      </button>
    </div>
  );
}
