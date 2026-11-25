import { get, sharedPath } from './client';

export const getBackendHealth = (options) => get(sharedPath('/health'), options);
