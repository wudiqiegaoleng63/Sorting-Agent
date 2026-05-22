import { useState } from 'react';

interface Props {
  filePath: string | null;
  loading: boolean;
  onRun: (task: string) => void;
}

export default function TaskInput({ filePath, loading, onRun }: Props) {
  const [task, setTask] = useState('');

  const handleSubmit = () => {
    if (!task.trim()) return;
    onRun(task.trim());
  };

  return (
    <div className="card">
      <h3>任务描述</h3>
      <textarea
        rows={3}
        placeholder="例如：帮我查看这个 Excel 有哪些 sheet"
        value={task}
        onChange={(e) => setTask(e.target.value)}
        disabled={loading}
      />
      {!filePath && (
        <p className="hint">请先上传 Excel 文件</p>
      )}
      <button
        onClick={handleSubmit}
        disabled={!task.trim() || loading || !filePath}
      >
        {loading ? 'Agent 运行中...' : '运行 Agent'}
      </button>
    </div>
  );
}