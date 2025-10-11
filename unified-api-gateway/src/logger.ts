import fs from 'fs';
import path from 'path';

const LOG_FILE = path.join(__dirname, '../gateway.log');

export function logRequest(moduleName: string, action: string, status: string, message?: string): void {
  const entry = `${new Date().toISOString()} | Module: ${moduleName} | Action: ${action} | Status: ${status} | Message: ${message ?? 'N/A'}\n`;
  try {
    fs.appendFileSync(LOG_FILE, entry, { encoding: 'utf8' });
  } catch (error) {
    console.error('Logger write failed:', error);
  }
}
