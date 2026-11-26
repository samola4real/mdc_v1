import { FAMILY_RANGES, GENERAL_RANGES, registrationPartRanges } from './providerRegistrationPayload.js';

export const registrationPayloadKey = JSON.stringify;
export const isCurrentRegistrationValidation = (validation, key) => (
    validation?.kind === 'valid' && validation.payloadKey === key
);

export const invalidateRegistrationValidation = (validation, key) => {
    if (!validation || validation.payloadKey === key || validation.kind === 'stale') return validation;
    return validation.kind === 'valid' ? { kind: 'stale' } : null;
};

export function createRegistrationRequestGuard() {
    let active = false;
    return async (operation) => {
        if (active) return;
        active = true;
        try {
            return await operation();
        } finally {
            active = false;
        }
    };
}

const privateKey = /^(?:authorization|cookie|credentials?|password|(?:access_|refresh_)?token|api_key|database_url|private_key|secret|stack(?:trace)?|traceback|x-vercel-protection-bypass)$/i;
const unsafeMessage = /Traceback \(most recent call last\)|\n\s*at\s+|Bearer\s+\S+|\beyJ[\w-]+\.[\w-]+\.[\w-]+|(?:password|token|secret|api.key|x-vercel-protection-bypass)\s*[:=]\s*\S+/i;
export const safeText = (value) => typeof value === 'string' && !unsafeMessage.test(value) ? value : '';

function safeDetails(value) {
    if (typeof value === 'string') return safeText(value) || '[redacted]';
    if (Array.isArray(value)) return value.map(safeDetails);
    if (value && typeof value === 'object') {
        return Object.fromEntries(Object.entries(value)
            .filter(([key]) => !privateKey.test(key))
            .map(([key, item]) => [key, safeDetails(item)]));
    }
    return value;
}

const directFields = {
    provider_id: 'providerId', provider_name: 'providerName', country: 'country', certifications: 'certifications',
    offering_id: 'offeringId', offering_name: 'offeringName', part_family: 'partFamily',
    service_category: 'partFamily', supported_part_types: 'partTypes'
};

function rangeField(ranges, path, prefix) {
    const [key, bound] = path.split('.');
    const range = ranges.find((item) => item.key === key);
    const field = range?.[bound] || range?.min || range?.max || range?.value;
    return field && prefix + '.' + field;
}

function controlFor(path, payload, showSupportStatus) {
    const canonical = path.replace(/^\$\.?/, '').replace(/^offerings\[0\]\./, '');
    const [head, ...rest] = canonical.split('.');
    const direct = head.replace(/\[\d+\]/g, '');
    const [offering = {}] = payload.offerings;
    if (showSupportStatus && direct === 'support_status') return 'supportStatus';
    if (showSupportStatus && direct === 'supported_part_types' && rest[0] === 'support_status') {
        const index = head.match(/\[(\d+)\]/)?.[1];
        const part = offering.supported_part_types?.[index]?.part_type;
        if (part) return 'partTypeStatuses.' + part;
    }
    if (Object.hasOwn(directFields, direct)) return directFields[direct];
    const tail = rest.join('.');
    if (head === 'family_capabilities') {
        if (tail.startsWith('gear_quality')) {
            return tail.endsWith('standard') ? 'familyDetails.qualityStandard' : 'familyDetails.qualityClass';
        }
        return rangeField(FAMILY_RANGES[offering.part_family] || [], tail, 'familyDetails');
    }
    if (head === 'part_type_capabilities') {
        const [type, ...pathParts] = rest;
        return rangeField(registrationPartRanges(offering.part_family, type),
            pathParts.join('.').replace(/^bounding_box_mm\./, ''), 'partMeasurements.' + type) || 'partTypes';
    }
    if (head === 'generic_capabilities') {
        if (tail.startsWith('materials')) {
            const index = tail.match(/^materials\[(\d+)\]/)?.[1];
            const material = offering.generic_capabilities?.materials?.[index]?.material;
            return material && tail.includes('.available_grades') ? 'materialGrades.' + material : 'materials';
        }
        if (tail.startsWith('processes')) return 'processes';
        return rangeField(GENERAL_RANGES, tail, 'general');
    }
    if (head === 'custom_provider_fields') return tail === 'description' ? 'description' : 'otherCertifications';
    if (head === 'custom_offering_fields') {
        return { production_mode: 'productionMode', industries_served: 'industriesServed',
            other_service_information: 'otherServiceInformation' }[tail] || 'customOfferingFields';
    }
    if (head === 'custom_capability_fields') {
        return {
            quality_class: 'familyDetails.qualityClass', notes: 'capabilityNotes',
            tolerance: 'familyDetails.tolerance', surface_finish: 'familyDetails.surfaceFinish',
            quality_tolerance_standard: 'familyDetails.qualityToleranceStandard', tolerance_class_fit: 'familyDetails.toleranceClassFit',
            additional_materials: 'additionalMaterials', additional_processes: 'additionalProcesses'
        }[rest[0]?.replace(/\[\d+\]/g, '')] || 'customCapabilityFields';
    }
    return undefined;
}

export function registrationValidationFeedback(details, payload, showSupportStatus = false) {
    const errors = {};
    const messages = [];
    const visit = (value, path) => {
        if (typeof value === 'string') {
            const message = safeText(value);
            if (!message) return;
            const embedded = message.match(/(?:\$\.)?\bofferings\[0\](?:\.[\w]+(?:\[\d+\])?)+/)?.[0]
                || message.match(/\b(?:provider_id|offering_id|provider_name|country)\b/)?.[0];
            const field = controlFor(path, payload, showSupportStatus) || controlFor(embedded || '', payload, showSupportStatus);
            if (field) errors[field] ||= message;
            else messages.push(message);
        } else if (Array.isArray(value)) {
            value.forEach((item, index) => visit(item, typeof item === 'string' ? path : path + '[' + index + ']'));
        } else if (value && typeof value === 'object') {
            Object.entries(value).forEach(([key, item]) => {
                const nextPath = key === 'non_field_errors' ? path : [path, key].filter(Boolean).join('.');
                visit(item, nextPath);
            });
        }
    };
    visit(details, '');
    return { errors, messages: [...new Set(messages)] };
}

export async function validateRegistration(payload, validatePublication) {
    const payloadKey = registrationPayloadKey(payload);
    try {
        const response = await validatePublication(payload);
        if (response?.valid === true) return { kind: 'valid', payloadKey, details: safeDetails(response) };
        const details = response?.error?.details ?? response?.errors;
        return {
            kind: 'invalid', payloadKey, details: safeDetails(response),
            message: safeText(response?.message ?? response?.error?.message),
            ...registrationValidationFeedback(details, payload)
        };
    } catch (error) {
        const message = safeText(error?.message);
        return {
            kind: error?.status === 400 ? 'invalid' : 'unavailable', payloadKey,
            ...registrationValidationFeedback(error?.details, payload),
            message, details: safeDetails(error?.details)
        };
    }
}

const registrationIdentity = (payload) => ({
    providerId: payload.provider_id, offeringId: payload.offerings[0].offering_id
});

export async function readBackRegistration({ providerId, offeringId }, services) {
    let provider;
    try {
        provider = await services.getProvider(providerId);
    } catch (error) {
        return { kind: error?.status === 404 && ['not_found', 'provider_not_found'].includes(error.code) ? 'absent' : 'unknown' };
    }
    if (provider?.data?.provider_id !== providerId) return { kind: 'unknown' };
    try {
        const list = await services.listProviderOfferings(providerId);
        if (list?.provider_id === providerId && list.offerings?.some((row) => row.offering_id === offeringId)) {
            const offering = await services.getOffering(offeringId);
            if (offering.data?.offering_id === offeringId && offering.data?.provider_id === providerId) {
                return { kind: 'matching', snapshot: { provider, offering, list } };
            }
        }
    } catch {
        // A canonical provider read still establishes that this provider ID exists.
    }
    return { kind: 'providerOnly' };
}

const receiptFrom = (data, error) => ({
    publicationId: safeText(data?.publication_id ?? error?.publicationId),
    publicationStatus: safeText(data?.publication_status ?? error?.publicationStatus),
    syncStatus: safeText(data?.sync_status ?? error?.syncStatus)
});

function acceptedReceipt(response, identity) {
    const data = response?.data;
    if (response?.status !== 201 || data?.contract_version !== '1.0' || data.operation !== 'create'
        || data.provider_id !== identity.providerId || !Array.isArray(data.offering_ids)
        || data.offering_ids.length !== 1 || data.offering_ids[0] !== identity.offeringId
        || !receiptFrom(data).publicationId) return false;
    return (data.status === 'accepted' && data.publication_status === 'sync_pending' && data.sync_status === 'pending')
        || (data.status === 'completed' && data.publication_status === 'synced' && data.sync_status === 'succeeded');
}

export function registrationRetryBlocked(outcome, payload) {
    if (!outcome) return false;
    const identity = registrationIdentity(payload);
    if (outcome.kind === 'uncertain') {
        return outcome.identity.providerId === identity.providerId && outcome.readBack.kind !== 'absent';
    }
    if (outcome.kind === 'rejected' && outcome.status === 409) {
        if (outcome.code === 'offering_already_exists') return outcome.identity.offeringId === identity.offeringId;
        return outcome.identity.providerId === identity.providerId;
    }
    return false;
}

export async function submitRegistration(payload, validation, services) {
    if (!isCurrentRegistrationValidation(validation, registrationPayloadKey(payload))) return { kind: 'unvalidated' };
    const identity = registrationIdentity(payload);
    let response;
    try {
        response = await services.registerProvider(payload);
    } catch (error) {
        const receipt = receiptFrom(null, error);
        if (error?.status >= 400 && error.status < 500 && error.status !== 408) {
            return {
                kind: 'rejected', identity, receipt, status: error.status, code: safeText(error.code),
                message: safeText(error.message), details: safeDetails(error.details),
                ...registrationValidationFeedback(error.details, payload)
            };
        }
        return { kind: 'uncertain', identity, receipt, readBack: await readBackRegistration(identity, services) };
    }
    const receipt = receiptFrom(response?.data);
    const accepted = acceptedReceipt(response, identity);
    const readBack = await readBackRegistration(identity, services);
    return {
        kind: accepted ? 'accepted' : 'uncertain', identity, receipt, readBack,
        ...(accepted && { details: safeDetails(response.data) })
    };
}
