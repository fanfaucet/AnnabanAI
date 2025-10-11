import { ModuleMap } from './types';
import dotenv from 'dotenv';

dotenv.config();

export const MODULE_MAP: ModuleMap = {
  'dds-core': process.env.DDS_CORE_URL || 'http://localhost:3001',
  'sparkai': process.env.SPARKAI_URL || 'http://localhost:3002',
  'oracleos': process.env.ORACLEOS_URL || 'http://localhost:3003',
};

export function registerModule(name: string, url: string): void {
  MODULE_MAP[name] = url;
}
