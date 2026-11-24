import axios from 'axios';
import { getMdcApiBaseUrl, getMdcSharedApiPrefix } from '@/config/runtimeConfig';
import { getKeycloakAccessToken } from '@/services/keycloak/keycloak';

const DEFAULT_TIMEOUT_MS = 15000;
const trimTrailingSlash = (value = '') => value.replace(/\/+$/, '');
const trimLeadingSlash = (value = '') => value.replace(/^\/+/, '');

export const buildMdcUrl = (path) => (
    trimTrailingSlash(getMdcApiBaseUrl()) + '/' + trimLeadingSlash(path)
);
export const sharedPath = (path) => (
    trimTrailingSlash(getMdcSharedApiPrefix()) + '/' + trimLeadingSlash(path)
);

export const normalizeMdcError = (error) => {
    const body = error?.response?.data;
    const apiError = body?.error;
    return {
        message: apiError?.message || body?.message || error?.message || 'MDC request failed.',
        status: error?.response?.status ?? error?.status ?? null,
        code: apiError?.code,
        details: apiError?.details ?? null,
        publicationId: body?.publication_id,
        publicationStatus: body?.publication_status,
        syncStatus: body?.sync_status
    };
};

const request = async (method, path, data, options = {}) => {
    const url = buildMdcUrl(path);
    if (!url.startsWith('/api/mdc/')) {
        throw { status: null, message: 'Use the local Stage 1 MDC transport.' };
    }
    let token;
    try {
        token = await getKeycloakAccessToken();
    } catch {
        throw { status: 401, message: 'Your MaaSAI session could not be refreshed. Sign in again.' };
    }
    try {
        const response = await axios({
            method, url, data, params: options.params,
            timeout: options.timeout ?? DEFAULT_TIMEOUT_MS,
            headers: {
                'Content-Type': 'application/json',
                ...(options.headers || {}),
                ...(token ? { Authorization: 'Bearer ' + token } : {})
            }
        });
        return options.withHeaders
            ? { data: response.data, status: response.status, etag: response.headers.etag || null }
            : response.data;
    } catch (error) {
        throw normalizeMdcError(error);
    }
};

export const get = (path, options) => request('get', path, undefined, options);
export const post = (path, data, options) => request('post', path, data, options);
export const patch = (path, data, options) => request('patch', path, data, options);
export const remove = (path, options) => request('delete', path, undefined, options);
