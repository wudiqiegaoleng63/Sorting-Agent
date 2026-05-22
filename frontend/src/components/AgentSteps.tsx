import type { AgentStep } from '../types/agent';

interface Props {
  steps: AgentStep[];
}

const TYPE_LABELS: Record<string, string> = {
  input: '📥',
  tool_selection: '🔧',
  tool_result: '📋',
  final: '✅',
};

export default function AgentSteps({ steps }: Props) {
  if (!steps.length) {
    return <div className="card"><p className="hint">暂无决策过程</p></div>;
  }

  return (
    <div className="card">
      <h3>Agent 决策过程</h3>
      <div className="steps">
        {steps.map((step, i) => (
          <div key={i} className={`step step-${step.type}`}>
            <div className="step-header">
              <span className="step-icon">{TYPE_LABELS[step.type] || '•'}</span>
              <span className="step-title">{step.title}</span>
              {step.tool_name && (
                <span className="step-tool">{step.tool_name}</span>
              )}
            </div>
            {step.content && (
              <div className="step-content">{step.content}</div>
            )}
            {step.arguments && Object.keys(step.arguments).length > 0 && (
              <pre className="step-args">{JSON.stringify(step.arguments, null, 2)}</pre>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}