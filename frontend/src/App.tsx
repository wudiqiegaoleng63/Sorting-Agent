import { useState, useRef, useCallback } from 'react';
import ChatLayout from './components/ChatLayout';
import Sidebar from './components/Sidebar';
import ChatMessages from './components/ChatMessages';
import ChatInput from './components/ChatInput';
import { runAgent } from './api/agentApi';
import { genId } from './utils/id';
import { createFakeSteps, advanceFakeSteps, markLastStepError, fallbackSteps } from './utils/fakeSteps';
import type { ChatMessage, UploadedFile } from './types/agent';

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);
  const [loading, setLoading] = useState(false);
  const timerRef = useRef<number | null>(null);

  const clearTimer = useCallback(() => {
    if (timerRef.current !== null) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const handleSend = async (task: string) => {
    // 1. Add user message
    const userMsg: ChatMessage = {
      id: genId(),
      role: 'user',
      content: task,
      file: uploadedFile ? { filename: uploadedFile.filename, file_path: uploadedFile.file_path } : null,
      createdAt: new Date().toISOString(),
    };

    // 2. Add empty assistant message (steps will be added by timer)
    const assistantId = genId();
    const assistantMsg: ChatMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      steps: [],
      loading: true,
      createdAt: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setLoading(true);

    // 3. Start fake step timer
    const fakeSteps = createFakeSteps();
    let currentIndex = 0;

    timerRef.current = window.setInterval(() => {
      setMessages((prev) =>
        prev.map((m) => {
          if (m.id !== assistantId) return m;
          if (currentIndex >= fakeSteps.length) return m;
          const updatedSteps = advanceFakeSteps(m.steps || [], fakeSteps, currentIndex);
          currentIndex += 1;
          return { ...m, steps: updatedSteps };
        })
      );

      if (currentIndex >= fakeSteps.length) {
        clearTimer();
      }
    }, 800);

    // 4. Call backend
    try {
      const res = await runAgent({
        session_id: sessionId,
        task,
        file_path: uploadedFile?.file_path || null,
      });

      clearTimer();
      setSessionId(res.session_id);

      const realSteps = res.steps && res.steps.length > 0
        ? res.steps.map((s) => ({ ...s, status: s.status || 'success' as const }))
        : fallbackSteps(task, res.answer);

      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? {
                ...m,
                content: res.answer,
                steps: realSteps,
                outputFile: res.output_file || null,
                loading: false,
              }
            : m
        )
      );
    } catch (err) {
      clearTimer();
      const errMsg = err instanceof Error ? err.message : '运行失败';

      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? {
                ...m,
                loading: false,
                error: errMsg,
                steps: markLastStepError(m.steps || [], errMsg),
              }
            : m
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    clearTimer();
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
