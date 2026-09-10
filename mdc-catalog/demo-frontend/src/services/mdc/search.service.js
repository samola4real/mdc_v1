import { post, sharedPath } from './client';

export const searchServiceDiscovery = (payload, options) => (
    post(sharedPath('/service-discovery/search'), payload, options)
);
