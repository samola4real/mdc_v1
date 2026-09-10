import { demoPath, get, sharedPath } from './client';

export const getBackendHealth = (options) => get(sharedPath('/health'), options);

export const getDemoHealth = (options) => get(demoPath('/health'), options);
