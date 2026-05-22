import type { AgentStep } from '../types/agent';

interface Props {
  step: AgentStep;
}

const STATUS_CLASS: Record<string, string> = {
  pending: 'step-pending',
  running: 'step-running',
  success: 'step-success',
  error: 'step-error',
};

export default function AgentStepCard({ step }: Props) {
  const cls = STATUS_CLASS[step.status || 'success'] || '';

  return (
    <div className={`agent-step ${cls}`}>
      <div className="step-header">
        <span className="step-title">{step.title}</span>
        {step.status === 'running' && <span className="step-running-badge">执行中...</span>}
        {step.tool_name && <span className="step-tool-badge">{step.tool_name}</span>}
      </div>
      {step.content && <div className="step-content">{step.content}</div>}
      {step.arguments && Object.keys(step.arguments).length > 0 && (
        <pre className="step-args"><code>{JSON.stringify(step.arguments, null, 2)}</code></pre>
      )}
    </div>
  );
}