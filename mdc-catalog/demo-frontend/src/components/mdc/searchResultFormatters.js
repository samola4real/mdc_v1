export const FIELD_LABELS = {
    module: 'Module',
    diametral_pitch: 'Diametral pitch',
    outside_diameter_mm: 'Outside diameter',
    outer_diameter_mm: 'Outer diameter',
    inner_diameter_mm: 'Inner diameter',
    internal_diameter_mm: 'Internal diameter',
    length_mm: 'Length',
    spline_module: 'Spline module',
    gear_quality: 'Gear quality',
    surface_finish_ra_um: 'Surface finish Ra',
    tolerance_mm: 'Tolerance',
    batch_size: 'Batch size',
    lead_time_weeks: 'Lead time',
    weight_kg: 'Weight',
    face_width_mm: 'Face width',
    wall_thickness_mm: 'Wall thickness',
    materials: 'Material',
    processes: 'Process',
    certifications: 'Certification',
    part_type: 'Part type',
    service_category: 'Service category'
};

const CERTIFICATION_LABELS = {
    ISO9001_2015: 'ISO 9001:2015',
    ISO14001_2015: 'ISO 14001:2015',
    ISO_TS_16949_partial: 'ISO/TS 16949 partial',
    APQP: 'APQP'
};

export const snakeToTitle = (value) => {
    if (value == null || value === '') {
        return 'Not provided';
    }

    return String(value)
        .replace(/_/g, ' ')
        .replace(/\s+/g, ' ')
        .trim()
        .replace(/\b\w/g, (char) => char.toUpperCase());
};

export const formatFieldLabel = (value) => FIELD_LABELS[value] || snakeToTitle(value);

export const formatTagLabel = (value) => {
    if (value == null || value === '') {
        return 'Not provided';
    }
    if (CERTIFICATION_LABELS[value]) {
        return CERTIFICATION_LABELS[value];
    }
    return String(value).replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase()).replace('Turn Mill', 'Turn-mill');
};

export const formatCapabilityRange = (value) => {
    if (value === undefined) {
        return 'Not provided';
    }
    if (value === null) {
        return 'Unknown';
    }
    if (typeof value === 'number' || typeof value === 'boolean') {
        return String(value);
    }
    if (typeof value === 'string') {
        return value;
    }
    if (Array.isArray(value)) {
        return value.map(formatCapabilityRange).join(', ');
    }
    if (typeof value === 'object') {
        if (value.raw) {
            return String(value.raw);
        }
        if (value.standard && value.max_class != null) {
            return `${value.standard} ${value.max_class}`;
        }
        if (value.exact != null) {
            return String(value.exact);
        }
        if (value.min != null && value.max != null) {
            return `${value.min}-${value.max}`;
        }
        if (value.max != null) {
            return `<= ${value.max}`;
        }
        if (value.min != null) {
            return `>= ${value.min}`;
        }

        return Object.entries(value)
            .filter(([, item]) => item != null && item !== '')
            .map(([key, item]) => `${formatFieldLabel(key)}: ${formatCapabilityRange(item)}`)
            .join(', ') || 'Unknown';
    }

    return String(value);
};

export const formatEvidenceValue = formatCapabilityRange;

export const formatLabel = (value) => {
    if (value === undefined) return 'Not provided';
    if (value === null) return 'Unknown';
    if (Array.isArray(value)) return value.map(formatLabel).join(', ');
    if (typeof value === 'object') return formatCapabilityRange(value);
    return String(value);
};

export const getNested = (object, path, fallback = undefined) => {
    const value = path.split('.').reduce((current, key) => current?.[key], object);
    return value === undefined ? fallback : value;
};

export const formatSuitability = (status) => {
    if (status === 'matched' || status === 'full_match' || status === 'partial_match') {
        return 'Suitable';
    }
    if (status === 'unmatched') {
        return 'Candidate';
    }
    return 'Evidence incomplete';
};

export const formatSupportStatus = (status) => {
    if (status === 'matched' || status === 'confirmed') return 'Confirmed';
    if (status === 'unknown') return 'Not confirmed';
    if (status === 'unmatched') return 'Not matched';
    return formatSuitability(status);
};

export const asArray = (value) => {
    if (!value) return [];
    return Array.isArray(value) ? value : [value];
};

