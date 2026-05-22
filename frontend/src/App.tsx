import { useState } from 'react';
import FileUpload from './components/FileUpload';
import TaskInput from './components/TaskInput';
import AgentSteps from './components/AgentSteps';
import ResultPanel from './components/ResultPanel';
import { runAgent } from './api/agentApi';
import type { AgentRunResponse } from './types/agent';

export default function App() {
  const [filePath, setFilePath] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AgentRunResponse | null>(null);
  const [error, setError] = useState('');

  const handleUploaded = (path: string) => {
    setFilePath(path);
  };

  const handleRun = async (task: string) => {
    setLoading(true);
    setError('');
    try {
      const res = await runAgent({
        session_id: sessionId,
        task,
        file_path: filePath,
      });
      setSessionId(res.session_id);
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : '运行失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <header>
        <h1>Excel Agent Demo</h1>
      </header>

      <main>
        <FileUpload onUploaded={handleUploaded} />
        <TaskInput filePath={filePath} loading={loading} onRun={handleRun} />

        {error && <div className="card"><p className="error">{error}</p></div>}

        {result && (
          <>
            <AgentSteps steps={result.steps} />
            <ResultPanel result={result} />
          </>
        )}
      </main>
    </div>
  );
}