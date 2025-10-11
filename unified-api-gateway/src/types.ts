export interface ModuleMap {
  [moduleName: string]: string;
}

export interface ApiResponse {
  status: 'success' | 'error';
  timestamp: string;
  data?: unknown;
  message?: string;
}
