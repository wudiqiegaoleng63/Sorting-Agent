import type { AgentStep } from '../types/agent';

const FAKE_STEPS: AgentStep[] = [
  { type: 'analysis', title: '正在分析任务', content: 'Agent 正在理解你的自然语言需求。', status: 'running' },
  { type: 'context', title: '正在检查文件上下文', content: 'Agent 正在确认当前上传的 Excel 文件路径和会话信息。', status: 'pending' },
  { type: 'tool_selection', title: '正在选择 MCP 工具', content: 'Agent 将根据 MCP 工具描述和参数结构选择合适的 Excel 工具。', status: 'pending' },
  { type: 'tool_call', title: '正在执行工具调用', content: 'Agent 正在通过 MCP 调用 Excel 工具处理文件。', status: 'pending' },
  { type: 'tool_result', title: '正在整理工具结果', content: 'Agent 正在整理工具返回的数据和结果文件信息。', status: 'pending' },
  { type: 'final', title: '正在生成最终回复', content: 'Agent 正在生成简洁的中文回答。', status: 'pending' },
];

export function createFakeSteps(): AgentStep[] {
  return FAKE_STEPS.map((s) => ({ ...s }));
}

/** Advance fake steps: mark previous running → success, append next step as running */
export function advanceFakeSteps(currentSteps: AgentStep[], fakeSteps: AgentStep[], index: number): AgentStep[] {
  if (index >= fakeSteps.length) return currentSteps;

  const updated = currentSteps.map((s) =>
    s.status === 'running' ? { ...s, status: 'success' as const } : s
  );

  return [...updated, { ...fakeSteps[index], status: 'running' }];
}

/** Mark all running/pending steps as success */
export function markStepsFinished(steps: AgentStep[]): AgentStep[] {
  return steps.map((s) =>
    s.status === 'running' || s.status === 'pending' ? { ...s, status: 'success' as const } : s
  );
}

/** Mark the last running step as error */
export function markLastStepError(steps: AgentStep[], errorMessage: string): AgentStep[] {
  if (steps.length === 0) {
    return [{ type: 'error', title: '执行失败', content: errorMessage, status: 'error' as const }];
  }

  const result = [...steps];
  for (let i = result.length - 1; i >= 0; i--) {
    if (result[i].status === 'running') {
      result[i] = { ...result[i], status: 'error', content: errorMessage };
      break;
    }
  }
  return result;
}

/** Fallback steps when backend returns no steps */
export function fallbackSteps(task: string, answer: string): AgentStep[] {
  return [
    { type: 'input', title: '任务提交', content: task, status: 'success' as const },
    { type: 'final', title: 'Agent 执行完成', content: answer, status: 'success' as const },
  ];
}
