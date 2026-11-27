export const NOT_PROVIDED = 'Not provided in this result';

const FIELD_LABELS = {
    module: 'Module (mm)',
    diametral_pitch: 'Diametral pitch',
    bounding_box_mm: 'Bounding box',
    surface_finish_ra_um: 'Surface finish Ra (µm)',
    delivery: 'Delivery time (weeks)',
    lead_time_weeks: 'Lead time (weeks)',
    batch_size: 'Batch size (pieces)',
    weight_kg: 'Weight (kg)',
    materials: 'Materials',
    processes: 'Manufacturing processes',
    certifications: 'Certifications'
};

export const formatFieldLabel = (field) => {
    if (Object.hasOwn(FIELD_LABELS, field)) return FIELD_LABELS[field];
    const label = field.replace(/_mm$/, ' (mm)').replace(/_deg$/, ' (°)').replace(/_/g, ' ');
    return label.charAt(0).toUpperCase() + label.slice(1);
};

export const formatCapabilityRange = (value) => {
    if (Number.isFinite(value) || nonemptyString(value)) return String(value);
    if (!value || typeof value !== 'object') return NOT_PROVIDED;

    if (nonemptyString(value.standard)) {
        if (Number.isFinite(value.best_class)) return `${value.standard}, best class ${value.best_class}`;
        if (Number.isFinite(value.max_class)) return `${value.standard}, class ≤ ${value.max_class}`;
        return value.standard;
    }
    if (Number.isFinite(value.exact)) return String(value.exact);
    if (Number.isFinite(value.value)) return String(value.value);
    const hasMin = Number.isFinite(value.min);
    const hasMax = Number.isFinite(value.max);
    if (hasMin && hasMax) return value.min === value.max ? String(value.min) : `${value.min}–${value.max}`;
    if (hasMax) return `≤ ${value.max}`;
    if (hasMin) return `≥ ${value.min}`;

    const dimensions = ['length_mm', 'width_mm', 'height_mm'].flatMap((field) => {
        const dimension = formatCapabilityRange(value[field]);
        return dimension === NOT_PROVIDED ? [] : [`${formatFieldLabel(field)}: ${dimension}`];
    });
    return dimensions.length ? dimensions.join(', ') : NOT_PROVIDED;
};

export const EVIDENCE_GROUPS = [
    { field: 'materials', label: 'Materials and grades', valueKey: 'material' },
    { field: 'processes', label: 'Manufacturing processes', valueKey: 'process' },
    { field: 'certifications', label: 'Certifications', valueKey: 'code' }
];

export const formatEvidenceList = (values, { valueKey }, options = []) => {
    if (!Array.isArray(values)) return NOT_PROVIDED;
    const labels = values.flatMap((item) => {
        const value = typeof item === 'string' ? item : item?.[valueKey];
        if (!nonemptyString(value) || item?.support_status === 'unknown' || item?.status === 'unknown') return [];
        const label = options.find((option) => option.value === value)?.label || value.replace(/_/g, ' ');
        const grades = Array.isArray(item?.available_grades) ? item.available_grades.filter((grade) => typeof grade === 'string' && grade.trim()) : [];
        return [grades.length ? `${label} (${grades.join(', ')})` : label];
    });
    return [...new Set(labels)].join(', ') || NOT_PROVIDED;
};

export const formatSuitability = (status) => {
    if (status === 'matched' || status === 'full_match') return 'Eligible';
    if (status === 'unmatched' || status === 'partial_match') return 'Requirements unmet';
    return 'Evidence incomplete';
};

export const offeringKey = (result) => JSON.stringify([result.provider_id, result.offering_id]);

const nonemptyString = (value) => typeof value === 'string' && Boolean(value.trim());
const emptyArray = (value) => Array.isArray(value) && value.length === 0;

export const validateSearchResponse = (response, request) => {
    const matchesRequest = response?.contract_version === '1.0'
        && ['request_id', 'service_category', 'part_family', 'part_type'].every((key) => response[key] === request[key]);
    if (!matchesRequest || !Array.isArray(response.results) || response.result_count !== response.results.length) {
        throw new Error('Invalid service-discovery response.');
    }
    const seenOfferings = new Set();
    for (const result of response.results) {
        if (result?.match?.status !== 'full_match'
            || !['provider_id', 'provider_name', 'offering_id', 'offering_name'].every((field) => nonemptyString(result[field]))
            || result.service_category !== response.service_category || result.part_family !== response.part_family
            || !emptyArray(result.unmatched_capabilities) || !emptyArray(result.unknown_capabilities)
            || !Array.isArray(result.matched_capabilities)
            || result.matched_capabilities.some((item) => !nonemptyString(item?.field) || item.requested == null)
            || seenOfferings.has(offeringKey(result))) {
            throw new Error('Invalid eligible offering in the service-discovery response.');
        }
        seenOfferings.add(offeringKey(result));
    }
    return response;
};
