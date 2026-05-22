import { useState } from 'react';
import ChatLayout from './components/ChatLayout';
import Sidebar from './components/Sidebar';
import ChatMessages from './components/ChatMessages';
import ChatInput from './components/ChatInput';
import { runAgent } from './api/agentApi';
import { genId } from './utils/id';
import type { ChatMessage, UploadedFile, AgentStep } from './types/agent';

const PENDING_STEPS: AgentStep[] = [
  { type: 'analysis', title: '正在分析任务', content: 'Agent 正在理解你的需求', status: 'running' },
  { type: 'tool_selection', title: '正在选择工具', content: 'Agent 将根据 MCP 工具描述选择合适的 Excel 工具', status: 'pending' },
  { type: 'tool_execution', title: '正在执行工具', content: '等待工具调用结果', status: 'pending' },
  { type: 'final', title: '正在生成回复', content: '整理最终回答', status: 'pending' },
];

function fallbackSteps(task: string, answer: string): AgentStep[] {
  return [
    { type: 'input', title: '任务提交', content: task, status: 'success' },
    { type: 'final', title: 'Agent 执行完成', content: answer, status: 'success' },
  ];
}

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSend = async (task: string) => {
    // 1. Add user message
    const userMsg: ChatMessage = {
      id: genId(),
      role: 'user',
      content: task,
      file: uploadedFile ? { filename: uploadedFile.filename, file_path: uploadedFile.file_path } : null,
      createdAt: new Date().toISOString(),
    };

    // 2. Add placeholder assistant message
    const assistantId = genId();
    const assistantMsg: ChatMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      steps: PENDING_STEPS,
      loading: true,
      createdAt: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setLoading(true);

    try {
      const res = await runAgent({
        session_id: sessionId,
        task,
        file_path: uploadedFile?.file_path || null,
      });

      // Update session
      setSessionId(res.session_id);

      // Use backend steps or fallback
      const steps = res.steps && res.steps.length > 0
        ? res.steps.map((s) => ({ ...s, status: s.status || 'success' as const }))
        : fallbackSteps(task, res.answer);

      // Replace assistant message with real data
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? {
                ...m,
                content: res.answer,
                steps,
                outputFile: res.output_file || null,
                loading: false,
              }
            : m
        )
      );
    } catch (err) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? {
                ...m,
                loading: false,
                error: err instanceof Error ? err.message : '运行失败',
                steps: [],
              }
            : m
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setSessionId(null);
    setUploadedFile(null);
  };

  return (
    <ChatLayout
      sidebar={
        <Sidebar
          sessionId={sessionId}
          uploadedFilename={uploadedFile?.filename || null}
          onNewChat={handleNewChat}
        />
      }
    >
      <div className="chat-header">
        <span className="chat-header-title">Excel Agent</span>
      </div>
      <ChatMessages messages={messages} />
      <ChatInput
        loading={loading}
        uploadedFile={uploadedFile}
        onFileUploaded={setUploadedFile}
        onFileCleared={() => setUploadedFile(null)}
        onSend={handleSend}
      />
    </ChatLayout>
  );
}
