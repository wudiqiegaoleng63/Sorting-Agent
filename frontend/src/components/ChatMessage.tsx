import type { ChatMessage as ChatMessageType } from '../types/agent';
import AgentStepCard from './AgentStepCard';
import DownloadButton from './DownloadButton';

interface Props {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: Props) {
  const isUser = message.role === 'user';

  return (
    <div className={`msg-row ${isUser ? 'msg-user' : 'msg-assistant'}`}>
      <div className="msg-avatar">{isUser ? '👤' : '🤖'}</div>
      <div className="msg-bubble">
        {/* User message */}
        {isUser && (
          <>
            <div className="msg-text">{message.content}</div>
            {message.file && (
              <div className="msg-file">📎 {message.file.filename}</div>
            )}
          </>
        )}

        {/* Assistant message */}
        {!isUser && (
          <>
            {message.steps && message.steps.length > 0 && (
              <div className="msg-steps">
                <div className="steps-title">执行过程</div>
                {message.steps.map((step, i) => (
                  <AgentStepCard key={i} step={step} />
                ))}
              </div>
            )}

            {message.loading && message.steps && message.steps.length > 0 && (
              <div className="msg-loading-hint">Agent 仍在处理，请稍候...</div>
            )}

            {message.error && (
              <div className="msg-error">{message.error}</div>
            )}

            {!message.loading && message.content && (
              <div className="msg-text">{message.content}</div>
            )}

            {message.outputFile && (
              <DownloadButton file={message.outputFile} />
            )}
          </>
        )}
      </div>
    </div>
  );
}