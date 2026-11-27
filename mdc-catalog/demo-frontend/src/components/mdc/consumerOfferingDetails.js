import {
    EVIDENCE_GROUPS, formatCapabilityRange, formatEvidenceList, formatFieldLabel, NOT_PROVIDED, offeringKey
} from './searchResultFormatters.js';
import { catalogueLabel } from './providerManagementDraft.js';
import { SUPPORT_STATUSES } from './providerRegistrationPayload.js';

const SPECIFICATION_FIELDS = [
    'module', 'diametral_pitch', 'number_of_teeth', 'outside_diameter_mm', 'gear_quality',
    'bounding_box_mm', 'length_mm', 'width_mm', 'height_mm', 'inner_diameter_mm', 'outer_diameter_mm',
    'overall_length_mm', 'tolerance_mm', 'face_width_mm', 'helix_angle_deg', 'shaft_angle_deg',
    'center_distance_mm', 'principal_diameter_mm', 'number_of_steps', 'spline_module', 'spline_length_mm',
    'worm_module', 'number_of_starts', 'wall_thickness_mm', 'number_of_holes', 'vertical_flange_length_mm',
    'horizontal_flange_length_mm', 'flange_diameter_mm'
];
const GENERAL_FIELDS = ['batch_size', 'lead_time_weeks', 'weight_kg', 'tolerance_mm', 'surface_finish_ra_um', 'quality'];
const DELIVERY_MODES = { in_house: 'In-house', subcontracted: 'Subcontracted' };
const NOT_PUBLISHED = 'Not published';

const records = (list) => Array.isArray(list) ? list : [];
const publicText = (value) => typeof value === 'string' ? value.trim().normalize('NFC') : '';
const textList = (list) => records(list).map(publicText).filter(Boolean);
const row = (label, value) => ({ label, value });
const section = (title, rows) => ({ title, rows });

const specificationRows = (capabilities, fields) => fields.flatMap((field) => {
    const value = formatCapabilityRange(capabilities?.[field]);
    return value === NOT_PROVIDED ? [] : [row(formatFieldLabel(field), value)];
});

// Compare declared values, regardless of API row order or evidence metadata.
const groupedValues = (values, key, publishedValues) => {
    const grouped = new Map();
    for (const item of records(values)) {
        const code = publicText(typeof item === 'string' ? item : item?.[key]);
        if (!code || item?.support_status === 'unknown' || item?.status === 'unknown' || item?.source_type === 'unknown') continue;
        if (!grouped.has(code)) grouped.set(code, new Set());
        for (const value of publishedValues(item)) grouped.get(code).add(value);
    }
    return grouped;
};

const materialGrades = (item) => textList(item?.available_grades);
const processModes = (item) => Object.hasOwn(DELIVERY_MODES, item?.delivery_mode) ? [DELIVERY_MODES[item.delivery_mode]] : [];
const certificationCodes = (values) => [...groupedValues(values, 'code', () => []).keys()];
const applicableEvidence = (criterion, group, discoveryMode) => {
    const provided = records(criterion.provided);
    // The lenient matcher scopes material and process evidence to each preference.
    // For a material alternative, it may return a published subtype of the requested material.
    if (discoveryMode === 'lenient' && (group.field === 'materials' || group.field === 'processes')) return provided;
    const requested = new Set(textList(criterion.requested));
    return provided.filter((value) => requested.has(typeof value === 'string' ? value : value?.[group.valueKey]));
};

const PREFERENCE_LABELS = {
    materials: 'Material alternative',
    processes: 'Process preference',
    delivery: 'Delivery preference (weeks)'
};

export const buildRequirementComparison = (result, partTypeLabel, catalogue, discoveryMode) => {
    const rows = [[result.matched_capabilities, 'Matched']];
    if (discoveryMode === 'lenient') {
        rows.push([result.unmatched_capabilities, 'Not matched'], [result.unknown_capabilities, 'Not confirmed']);
    }
    return [
        { field: 'part_type', label: 'Part type', requested: partTypeLabel, provided: partTypeLabel, status: 'Matched' },
        ...rows.flatMap(([criteria, status]) => criteria.map((criterion) => {
            const { field, requested, provided } = criterion;
            const group = EVIDENCE_GROUPS.find((entry) => entry.field === field);
            const label = discoveryMode === 'lenient' && Object.hasOwn(PREFERENCE_LABELS, field)
                ? PREFERENCE_LABELS[field] : formatFieldLabel(field);
            return {
                field, label, status,
                requested: group ? formatEvidenceList(requested, group, catalogue[field]) : formatCapabilityRange(requested),
                provided: group ? formatEvidenceList(applicableEvidence(criterion, group, discoveryMode), group, catalogue[field])
                    : formatCapabilityRange(provided)
            };
        }))
    ];
};

const consistentWithSearchEvidence = (result, context, provider, offering) => {
    const { partType, requirements, discoveryMode } = context;
    const generic = offering.generic_capabilities || {};
    const currentLists = {
        materials: groupedValues(generic.materials, 'material', materialGrades),
        processes: groupedValues(generic.processes, 'process', processModes),
        certifications: groupedValues([...records(provider.certifications), ...records(generic.certifications)], 'code', () => [])
    };
    const family = offering.family_capabilities || {};
    const typed = offering.part_type_capabilities?.[partType] || {};

    const confirmedEvidence = discoveryMode === 'lenient'
        ? [...result.matched_capabilities, ...result.unmatched_capabilities]
        : result.matched_capabilities;
    return confirmedEvidence.every((criterion) => {
        const { field, provided } = criterion;
        const group = EVIDENCE_GROUPS.find((entry) => entry.field === field);
        if (group) {
            const details = field === 'materials' ? materialGrades : field === 'processes' ? processModes : () => [];
            const searchValues = groupedValues(applicableEvidence(criterion, group, discoveryMode), group.valueKey, details);
            return [...searchValues].every(([code, values]) => {
                const current = currentLists[field].get(code);
                return current && [...values].every((value) => current.has(value));
            });
        }
        const earlier = formatCapabilityRange(provided);
        if (earlier === NOT_PROVIDED) return true;
        const publishedField = field === 'delivery' ? 'lead_time_weeks' : field;
        let source = generic;
        if (Object.hasOwn(requirements.part_family_specifications, field)) source = family;
        if (Object.hasOwn(requirements.part_type_specifications, field)) source = typed;
        return earlier === formatCapabilityRange(source[publishedField]);
    });
};

export const buildPublishedOffering = (result, context, provider, offering) => {
    const { partType, partTypeLabel, catalogue } = context;
    const partTypes = records(offering?.supported_part_types);
    if (provider?.contract_version !== '1.0' || offering?.contract_version !== '1.0'
        || provider.provider_id !== result.provider_id || offering.provider_id !== result.provider_id
        || offering.offering_id !== result.offering_id || provider.provider_name !== result.provider_name
        || offering.offering_name !== result.offering_name || offering.service_category !== result.service_category
        || offering.part_family !== result.part_family || provider.status !== 'active'
        || offering.is_active !== true || offering.support_status !== 'confirmed'
        || !partTypes.some((item) => item?.part_type === partType && item.support_status === 'confirmed')
        || !consistentWithSearchEvidence(result, context, provider, offering)) {
        return null;
    }

    const generic = offering.generic_capabilities || {};
    const service = offering.custom_offering_fields;
    const country = publicText(provider.country);
    const materials = groupedValues(generic.materials, 'material', materialGrades);
    const processes = groupedValues(generic.processes, 'process', processModes);
    const certRows = (values) => certificationCodes(values).map((value) => row(catalogueLabel(catalogue.certifications, value)));
    const serviceInformation = [
        row('Service category', catalogueLabel(catalogue.serviceCategories, offering.service_category)),
        row('Country', country),
        row('Provider description', publicText(provider.custom_provider_fields?.description)),
        row('Production mode', publicText(service?.production_mode)),
        row('Industries served', textList(service?.industries_served).join(', '))
    ].filter(({ value }) => value);

    const sections = [
        section('Provider and service', serviceInformation),
        section('Supported part types', partTypes.flatMap((item) => {
            const value = publicText(item?.part_type);
            if (!value) return [];
            return [row(catalogueLabel(catalogue.partTypes[offering.part_family], value),
                catalogueLabel(SUPPORT_STATUSES, item.support_status || 'unknown'))];
        })),
        section('Family specifications', specificationRows(offering.family_capabilities, SPECIFICATION_FIELDS)),
        section(partTypeLabel + ' specifications', specificationRows(offering.part_type_capabilities?.[partType], SPECIFICATION_FIELDS)),
        section('General capabilities', specificationRows(generic, GENERAL_FIELDS)),
        section('Materials and grades', [...materials].map(([code, grades]) => (
            row(catalogueLabel(catalogue.materials, code), [...grades].join(', ') || NOT_PUBLISHED)
        ))),
        section('Manufacturing processes', [...processes].map(([code, modes]) => (
            row(catalogueLabel(catalogue.processes, code), [...modes].join(', '))
        ))),
        section('Provider-level certifications', certRows(provider.certifications)),
        section('Offering certifications', certRows(generic.certifications))
    ].filter(({ rows }) => rows.length > 0);

    return {
        providerName: publicText(provider.provider_name),
        offeringName: publicText(offering.offering_name),
        offeringId: offering.offering_id,
        partTypeLabel,
        sections
    };
};

export const createOfferingDetailsLoader = ({ getProvider, getOffering }) => {
    const entries = new Map();
    return {
        async load(result, context, publish, retry = false) {
            const key = offeringKey(result);
            const existing = entries.get(key);
            if (existing && !(retry && existing.kind === 'error')) return;
            const pending = { kind: 'loading' };
            entries.set(key, pending);
            publish(key, pending);

            let next;
            try {
                const [provider, offering] = await Promise.all([
                    getProvider(result.provider_id), getOffering(result.offering_id)
                ]);
                const details = buildPublishedOffering(result, context, provider.data, offering.data);
                next = details ? { kind: 'ready', details } : { kind: 'changed' };
            } catch (error) {
                next = error?.status === 404 ? { kind: 'unavailable' } : { kind: 'error', status: error?.status };
            }
            if (entries.get(key) !== pending) return;
            entries.set(key, next);
            publish(key, next);
        },
        clear() {
            entries.clear();
        }
    };
};
