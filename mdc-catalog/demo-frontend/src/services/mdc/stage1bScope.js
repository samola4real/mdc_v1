export const DISPOSABLE_PROVIDER_PREFIX = 'mdc_stage1b_';

const scopedId = (id, limit) => (
    typeof id === 'string' && id.startsWith(DISPOSABLE_PROVIDER_PREFIX)
    && id.length <= limit && /^[a-z0-9]+(?:_[a-z0-9]+)*$/.test(id)
);

export const isDisposableMdcId = (id) => scopedId(id, 255);

export const isDisposableOfferingId = (id, providerId) => (
    scopedId(id, 512) && id.slice(DISPOSABLE_PROVIDER_PREFIX.length).includes('_')
    && (providerId === undefined || (isDisposableMdcId(providerId) && id.startsWith(providerId + '_')))
);
