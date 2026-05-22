import type { AgentRunResponse } from '../types/agent';

interface Props {
  result: AgentRunResponse | null;
}

export default function ResultPanel({ result }: Props) {
  if (!result) return null;

  const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

  return (
    <div className="card">
      <h3>最终结果</h3>
      <div className="result-answer">{result.answer}</div>

      {result.output_file && result.output_file.download_url && (
        <div className="result-download">
          <a
            href={`${BASE_URL}${result.output_file.download_url}`}
            download={result.output_file.filename}
            className="download-btn"
          >
            下载结果文件: {result.output_file.filename}
          </a>
        </div>
      )}

      <div className="result-meta">
        <span>Session: {result.session_id}</span>
        <span>历史消息: {result.history_count}</span>
      </div>
    </div>
  );
}