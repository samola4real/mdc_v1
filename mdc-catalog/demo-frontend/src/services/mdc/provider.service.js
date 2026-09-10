import { get, post, sharedPath } from './client';

export const validateProviderPublication = (payload, options) => (
    post(sharedPath('/provider-publication/validate'), payload, options)
);

export const publishProviderPublication = (payload, options) => (
    post(sharedPath('/provider-publication/publish'), payload, options)
);

export const getProviders = (options) => get(sharedPath('/providers'), options);

export const getProvider = (providerId, options) => (
    get(sharedPath(`/providers/${encodeURIComponent(providerId)}`), options)
);
