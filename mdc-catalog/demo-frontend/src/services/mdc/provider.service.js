import { get, patch, post, remove, sharedPath } from './client';

const providers = (providerId) => sharedPath('/providers/' + encodeURIComponent(providerId));
const offerings = (offeringId) => sharedPath('/offerings/' + encodeURIComponent(offeringId));
const withHeaders = { withHeaders: true };
const conditional = (etag) => ({ withHeaders: true, headers: { 'If-Match': etag } });

export const validateProviderPublication = (payload) => post(sharedPath('/provider-publication/validation'), payload);
export const registerProvider = (payload) => post(sharedPath('/provider-publication'), payload, withHeaders);
export const getProvider = (providerId) => get(providers(providerId), withHeaders);
export const listProviderOfferings = (providerId) => get(providers(providerId) + '/offerings');
export const getOffering = (offeringId) => get(offerings(offeringId), withHeaders);
export const updateProvider = (providerId, payload, etag) => patch(providers(providerId), payload, conditional(etag));
export const updateOffering = (offeringId, payload, etag) => patch(offerings(offeringId), payload, conditional(etag));
export const createOffering = (providerId, payload) => post(providers(providerId) + '/offerings', payload, withHeaders);
export const deleteProvider = (providerId, etag) => remove(providers(providerId), conditional(etag));
export const deleteOffering = (offeringId, etag) => remove(offerings(offeringId), conditional(etag));
