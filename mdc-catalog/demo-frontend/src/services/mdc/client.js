import axios from 'axios';
import {
    getMdcApiBaseUrl,
    getMdcDemoApiPrefix,
    getMdcSharedApiPrefix
} from '@/config/runtimeConfig';

const DEFAULT_TIMEOUT_MS = 10000;

const trimTrailingSlash = (value = '') => value.replace(/\/+$/, '');
const trimLeadingSlash = (value = '') => value.replace(/^\/+/, '');

export const buildMdcUrl = (path) => {
    const baseUrl = trimTrailingSlash(getMdcApiBaseUrl());
    const safePath = trimLeadingSlash(path);

    if (!baseUrl) {
        return `/${safePath}`;
    }

    return `${baseUrl}/${safePath}`;
};

const joinPath = (prefix, path) => {
    const safePrefix = trimTrailingSlash(prefix || '');
    const safePath = trimLeadingSlash(path || '');

    if (!safePrefix) {
        return `/${safePath}`;
    }

    return `${safePrefix}/${safePath}`;
};

export const sharedPath = (path) => joinPath(getMdcSharedApiPrefix(), path);

export const demoPath = (path) => joinPath(getMdcDemoApiPrefix(), path);

export const normalizeMdcError = (error) => {
    if (error?.response) {
        const responseData = error.response.data;
        return {
            message: responseData?.error?.message || responseData?.message || error.message || 'Request failed',
            status: error.response.status,
            details: responseData?.error?.details || responseData?.error || responseData
        };
    }

    if (error?.request) {
        return {
            message: error.message || 'No response received',
            status: null,
            details: null
        };
    }

    return {
        message: error?.message || 'Request failed',
        status: null,
        details: error || null
    };
};

const request = async (method, path, data, options = {}) => {
    try {
        const response = await axios({
            method,
            url: buildMdcUrl(path),
            data,
            timeout: options.timeout ?? DEFAULT_TIMEOUT_MS,
            headers: {
                'Content-Type': 'application/json',
                ...(options.headers || {})
            },
            params: options.params
        });

        return response.data;
    } catch (error) {
        throw normalizeMdcError(error);
    }
};

export const get = (path, options) => request('get', path, undefined, options);

export const post = (path, data, options) => request('post', path, data, options);
