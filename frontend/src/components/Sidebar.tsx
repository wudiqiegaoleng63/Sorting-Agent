interface Props {
  sessionId: string | null;
  uploadedFilename: string | null;
  onNewChat: () => void;
}

export default function Sidebar({ sessionId, uploadedFilename, onNewChat }: Props) {
  return (
    <div className="sidebar-inner">
      <div className="sidebar-brand">Excel Agent</div>

      <button className="btn-new-chat" onClick={onNewChat}>
        + 新对话
      </button>

      <div className="sidebar-info">
        {sessionId && (
          <div className="sidebar-item">
            <span className="sidebar-label">Session</span>
            <span className="sidebar-value" title={sessionId}>
              {sessionId.length > 16 ? sessionId.slice(0, 16) + '...' : sessionId}
            </span>
          </div>
        )}
        {uploadedFilename && (
          <div className="sidebar-item">
            <span className="sidebar-label">文件</span>
            <span className="sidebar-value">{uploadedFilename}</span>
          </div>
        )}
      </div>

      <div className="sidebar-desc">
        上传 Excel，用自然语言完成读取、清洗、排序、统计和导出。
      </div>
    </div>
  );
}
