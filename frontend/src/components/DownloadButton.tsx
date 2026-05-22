import type { OutputFile } from '../types/agent';
import { getDownloadUrl } from '../api/agentApi';

interface Props {
  file: OutputFile;
}

export default function DownloadButton({ file }: Props) {
  const url = getDownloadUrl(file.download_url);

  return (
    <div className="download-row">
      <a href={url} download={file.filename} className="btn-download">
        📥 下载结果文件: {file.filename}
      </a>
    </div>
  );
}
