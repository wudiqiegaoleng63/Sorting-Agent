export type ChatRole = "user" | "assistant";

export type StepStatus = "pending" | "running" | "success" | "error";

export type UploadedFile = {
  file_id?: string;
  filename: string;
  file_path: string;
  download_url?: string | null;
};

export type OutputFile = {
  file_id?: string;
  filename: string;
  download_url: string;
};

export type AgentStep = {
  type: string;
  title: string;
  content?: string;
  tool_name?: string;
  arguments?: Record<string, unknown>;
  status?: StepStatus;
};

export type ChatMessage = {
  id: string;
  role: ChatRole;
  content: string;
  file?: UploadedFile | null;
  steps?: AgentStep[];
  outputFile?: OutputFile | null;
  loading?: boolean;
  error?: string | null;
  createdAt: string;
};

export type UploadResponse = {
  file_id?: string;
  filename: string;
  file_path: string;
  download_url?: string | null;
};

export type AgentRunRequest = {
  session_id?: string | null;
  task: string;
  file_path?: string | null;
};

export type AgentRunResponse = {
  session_id: string;
  answer: string;
  steps?: AgentStep[];
  output_file?: OutputFile | null;
  history_count?: number;
};
