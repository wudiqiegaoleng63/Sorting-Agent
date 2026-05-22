export interface UploadResponse {
  filename: string;
  path: string;
}

export interface AgentRunRequest {
  session_id?: string | null;
  task: string;
  file_path?: string | null;
}

export interface AgentStep {
  type: string;
  title: string;
  content: string;
  tool_name?: string | null;
  arguments?: Record<string, unknown> | null;
}

export interface OutputFile {
  file_id: string;
  filename: string;
  download_url: string;
}

export interface AgentRunResponse {
  session_id: string;
  answer: string;
  steps: AgentStep[];
  output_file: OutputFile | null;
  history_count: number;
}
