import { BOX_PART_TYPES, ROUND_PART_TYPES, buildProviderPreviewPayload, emptyProviderForm } from './providerPayloadBuilder.js';
import { isDisposableMdcId, isDisposableOfferingId } from '../../services/mdc/stage1bScope.js';

export const SUPPORT_STATUSES = [
    { label: 'Confirmed', value: 'confirmed' },
    { label: 'Requires confirmation', value: 'candidate_requiring_confirmation' },
    { label: 'Unknown', value: 'unknown' }
];
export const QUALITY_STANDARDS = ['DIN', 'ISO', 'AGMA'];

export const FAMILY_RANGES = {
    gear: [
        { key: 'module', label: 'Module', min: 'moduleMin', max: 'moduleMax', decimal: true },
        { key: 'outside_diameter_mm', label: 'Outside diameter', min: 'diameterMinMm', max: 'diameterMaxMm', suffix: ' mm' }
    ],
    shaft: [
        { key: 'length_mm', label: 'Length', max: 'lengthMaxMm', suffix: ' mm' },
        { key: 'outer_diameter_mm', label: 'Outer diameter', min: 'outerDiameterMinMm', max: 'outerDiameterMaxMm', suffix: ' mm' }
    ]
};
export const GENERAL_RANGES = [
    { key: 'batch_size', label: 'Batch size', min: 'batchSizeMin', max: 'batchSizeMax', suffix: ' pieces' },
    { key: 'lead_time_weeks', label: 'Lead time', min: 'leadTimeMinWeeks', max: 'leadTimeMaxWeeks', suffix: ' weeks' },
    { key: 'weight_kg', label: 'Weight', max: 'weightMaxKg', suffix: ' kg' }
];
const boxRanges = [
    { key: 'length_mm', label: 'Length', max: 'maxLengthMm', suffix: ' mm' },
    { key: 'width_mm', label: 'Width', max: 'maxWidthMm', suffix: ' mm' },
    { key: 'height_mm', label: 'Height/thickness', max: 'maxHeightMm', suffix: ' mm' }
];
const roundRanges = [{ key: 'outer_diameter_mm', label: 'Outer diameter', max: 'maxDiameterMm', suffix: ' mm' }];
const splineRanges = [{ key: 'spline_module', label: 'Spline module', value: 'splineModule', decimal: true }];
const bounds = ['min', 'max', 'value'];
const evidence = { source_type: 'provider_confirmed', confidence: 'declared' };

export const registrationPartRanges = (family, type) => {
    if (family === 'shaft' && type === 'splined_shaft') return splineRanges;
    if (family !== 'metal_part') return [];
    if (BOX_PART_TYPES.includes(type)) return boxRanges;
    return ROUND_PART_TYPES.includes(type) ? roundRanges : [];
};

export const measurementFields = (ranges) => ranges.flatMap((range) => (
    bounds.filter((bound) => range[bound]).map((bound) => ({
        name: range[bound], label: bound === 'value' ? range.label : range.label + ' ' + bound,
        suffix: range.suffix, decimal: range.decimal
    }))
));

const clean = (value) => String(value ?? '').trim();
const compareName = (value) => clean(value).toLowerCase();
const entered = (value) => value !== undefined && value !== null && value !== '';
const positive = (value) => typeof value === 'number' && Number.isFinite(value) && value > 0;

export const emptyRegistrationForm = () => ({
    providerName: '', providerId: '', country: '', description: '', certifications: [], otherCertifications: [],
    offeringName: '', offeringId: '', partFamily: '', supportStatus: 'confirmed', partTypes: [],
    productionMode: '', industriesServed: '', otherServiceInformation: '', customOfferingFields: [],
    familyDetails: {}, partMeasurements: {}, materials: [], materialGrades: {}, additionalMaterials: [],
    processes: [], additionalProcesses: [], general: {}, capabilityNotes: '', customCapabilityFields: []
});

const hasContent = (value) => {
    if (typeof value === 'string') return Boolean(value.trim());
    if (Array.isArray(value)) return value.some(hasContent);
    if (value && typeof value === 'object') {
        return Object.entries(value).some(([field, item]) => field !== 'id' && hasContent(item));
    }
    return entered(value);
};

export const hasRegistrationDraft = ({ supportStatus, ...fields }) => supportStatus !== 'confirmed' || hasContent(fields);

export const selectRegistrationFamily = (form, family, confirmChange) => {
    if (family === form.partFamily) return form;
    if (hasContent([form.partTypes, form.familyDetails, form.partMeasurements]) && !confirmChange()) return form;
    return { ...form, partFamily: family, partTypes: [], familyDetails: {}, partMeasurements: {} };
};

export const selectRegistrationSupport = (form, supportStatus, confirmChange) => {
    const dropsMeasurements = form.supportStatus === 'confirmed' && supportStatus !== 'confirmed'
        && form.partTypes.some((type) => hasContent(form.partMeasurements[type]));
    return dropsMeasurements && !confirmChange() ? form : { ...form, supportStatus };
};

const requiredText = (errors, field, value, label, max) => {
    if (!clean(value)) errors[field] = 'Enter ' + label + '.';
    else if (clean(value).length > max) errors[field] = 'Use at most ' + max + ' characters.';
};

const controlledSelection = (values, options, field, errors) => {
    const known = new Set((options || []).map((option) => option.value));
    const selected = [...new Set(values)].filter((value) => known.has(value));
    if (values.some((value) => !known.has(value))) errors[field] = 'Select only values from the current catalogue.';
    return selected;
};

const splitUnique = (value, separator, key = (item) => item) => {
    const seen = new Set();
    return value.split(separator).map(clean).filter((item) => {
        if (!item || seen.has(key(item))) return false;
        seen.add(key(item));
        return true;
    });
};

const grades = (value = '') => splitUnique(value, ',');

const reservedNames = new Set([
    'additional_certifications', 'additional_materials', 'additional_processes',
    'production_mode', 'industries_served', 'other_service_information', 'notes',
    'tolerance', 'surface_finish', 'quality_class', 'description', 'provider_id', 'provider_name',
    'offering_id', 'offering_name', 'part_family', 'service_category', 'support_status', 'supported_part_types',
    'display_name', 'facility_id', 'material_id', 'grade_id', 'certifications', 'materials', 'processes',
    'family_capabilities', 'part_type_capabilities', 'generic_capabilities', 'custom_provider_fields',
    'custom_offering_fields', 'custom_capability_fields', 'module', 'outside_diameter_mm', 'outer_diameter_mm',
    'length_mm', 'bounding_box_mm', 'spline_module', 'gear_quality', 'batch_size', 'lead_time_weeks', 'weight_kg',
    'source_type', 'confidence', 'routes', 'route_steps', 'operation_sequence', 'machine_sequence', 'process_order',
    'subcontractor_route', 'cycle_time', 'setup_time', 'machine_availability', 'pricing', 'capacity_calendar',
    'api_key', 'access_token', 'credential', 'credentials', 'database_url', 'password', 'private_key',
    'refresh_token', 'secret', 'token', '__proto__', 'constructor', 'prototype'
]);

function readNamedRows(rows, field, errors, options = []) {
    const known = new Set(options.flatMap(({ label, value }) => [compareName(label), compareName(value)]));
    const seen = new Set();
    const accepted = [];
    for (const row of rows) {
        if (!hasContent(row)) continue;
        const name = clean(row.name);
        const key = compareName(name);
        const control = field + '.' + row.id + '.name';
        if (!name) errors[control] = 'Enter a name for this entry.';
        else if (known.has(key)) errors[control] = 'Select this value from the catalogue list.';
        else if (seen.has(key)) errors[control] = 'This name is already entered.';
        else accepted.push({ ...row, name });
        seen.add(key);
    }
    return accepted;
}

function readCustomMap(rows, field, errors, technical = false) {
    const entries = [];
    for (const row of readNamedRows(rows, field, errors)) {
        const control = field + '.' + row.id;
        const reserved = compareName(row.name).replace(/[\s-]+/g, '_');
        const value = clean(row.value);
        if (reservedNames.has(reserved)) {
            errors[control + '.name'] = 'Use a name outside the standard fields and reserved keys.';
            continue;
        }
        if (!value) {
            errors[control + '.value'] = 'Enter a value or remove this row.';
            continue;
        }
        const unit = clean(row.unit);
        const notes = clean(row.notes);
        entries.push([row.name, technical ? { value, ...(unit && { unit }), ...(notes && { notes }) } : value]);
    }
    return Object.fromEntries(entries);
}

function validateRanges(ranges, values, prefix, errors) {
    for (const range of ranges) {
        for (const bound of bounds) {
            const field = range[bound];
            if (field && entered(values[field]) && !positive(values[field])) {
                errors[prefix + '.' + field] = 'Enter a number greater than zero.';
            }
        }
        if (positive(values[range.min]) && positive(values[range.max]) && values[range.min] > values[range.max]) {
            errors[prefix + '.' + range.min] = 'Minimum must be less than or equal to maximum.';
        }
    }
}

function buildPartCapabilities(form, partTypes, errors) {
    if (form.supportStatus !== 'confirmed') return {};
    const result = {};
    for (const type of partTypes) {
        const values = form.partMeasurements[type] || {};
        const ranges = registrationPartRanges(form.partFamily, type);
        validateRanges(ranges, values, 'partMeasurements.' + type, errors);
        const records = Object.fromEntries(ranges.flatMap((range) => {
            const numeric = Object.fromEntries(bounds
                .filter((bound) => range[bound] && positive(values[range[bound]]))
                .map((bound) => [bound, values[range[bound]]]));
            return Object.keys(numeric).length ? [[range.key, { ...evidence, ...numeric }]] : [];
        }));
        if (Object.keys(records).length) result[type] = ranges === boxRanges ? { bounding_box_mm: records } : records;
    }
    return result;
}

export function buildRegistrationPayload(form, filters) {
    const errors = {};
    const familyDetails = form.familyDetails;
    const providerId = clean(form.providerId);
    const offeringId = clean(form.offeringId);
    requiredText(errors, 'providerName', form.providerName, 'the provider name', 255);
    requiredText(errors, 'country', form.country, 'the country', 100);
    requiredText(errors, 'offeringName', form.offeringName, 'the offering name', 255);
    if (!providerId) errors.providerId = 'Enter a provider ID.';
    else if (providerId.length > 255) errors.providerId = 'Use at most 255 characters for the provider ID.';
    else if (!isDisposableMdcId(providerId)) {
        errors.providerId = 'Use mdc_stage1b_ followed by lowercase letters or numbers in groups separated by single underscores.';
    }
    if (!offeringId) errors.offeringId = 'Enter an offering ID.';
    else if (offeringId.length > 512) errors.offeringId = 'Use at most 512 characters for the offering ID.';
    else if (!isDisposableOfferingId(offeringId, providerId)) {
        errors.offeringId = 'Use the complete provider ID followed by an underscore and an offering suffix.';
    }
    const serviceCategory = filters?.serviceCategoryByFamily[form.partFamily] || '';
    if (!serviceCategory || !filters?.partFamilies.some(({ value }) => value === form.partFamily)) {
        errors.partFamily = 'Select a part family from the catalogue.';
    }
    if (!SUPPORT_STATUSES.some(({ value }) => value === form.supportStatus)) {
        errors.supportStatus = 'Select a support status.';
    }

    const partTypes = controlledSelection(form.partTypes, filters?.partTypes[form.partFamily], 'partTypes', errors);
    const certifications = controlledSelection(form.certifications, filters?.certifications, 'certifications', errors);
    const materials = controlledSelection(form.materials, filters?.materials, 'materials', errors);
    const processes = controlledSelection(form.processes, filters?.processes, 'processes', errors);

    validateRanges(FAMILY_RANGES[form.partFamily] || [], familyDetails, 'familyDetails', errors);
    validateRanges(GENERAL_RANGES, form.general, 'general', errors);
    if (form.partFamily === 'gear') {
        const qualityClass = clean(familyDetails.qualityClass);
        if (qualityClass && !Number.isNaN(Number(qualityClass)) && !positive(Number(qualityClass))) {
            errors['familyDetails.qualityClass'] = 'Enter a positive numeric class or a nonnumeric class designation.';
        }
        if (familyDetails.qualityStandard && !QUALITY_STANDARDS.includes(familyDetails.qualityStandard)) {
            errors['familyDetails.qualityStandard'] = 'Select DIN, ISO or AGMA.';
        }
    }

    const extraCertifications = readNamedRows(form.otherCertifications, 'otherCertifications', errors, filters?.certifications);
    const extraMaterials = readNamedRows(form.additionalMaterials, 'additionalMaterials', errors, filters?.materials);
    const extraProcesses = readNamedRows(form.additionalProcesses, 'additionalProcesses', errors, filters?.processes);
    const offeringCustom = readCustomMap(form.customOfferingFields, 'customOfferingFields', errors);
    const capabilityCustom = readCustomMap(form.customCapabilityFields, 'customCapabilityFields', errors, true);

    // Reuse the existing canonical envelope, range and provenance construction.
    const payload = buildProviderPreviewPayload({
        ...emptyProviderForm(),
        ...form.general, ...familyDetails,
        providerId, offeringId, serviceCategory, partTypes, certifications, materials, processes,
        providerName: form.providerName, offeringName: form.offeringName, country: form.country,
        description: form.description, partFamily: form.partFamily, supportStatus: form.supportStatus,
        capabilityNotes: form.capabilityNotes,
        tolerance: form.partFamily === 'metal_part' ? familyDetails.tolerance : '',
        surfaceFinish: form.partFamily === 'metal_part' ? familyDetails.surfaceFinish : ''
    });
    const [offering] = payload.offerings;
    offering.part_type_capabilities = buildPartCapabilities(form, partTypes, errors);
    if (offering.generic_capabilities.materials) {
        offering.generic_capabilities.materials = offering.generic_capabilities.materials.map((record) => {
            const available_grades = grades(form.materialGrades[record.material]);
            return available_grades.length ? { ...record, available_grades } : record;
        });
    }
    if (extraCertifications.length) {
        payload.custom_provider_fields = {
            ...payload.custom_provider_fields, additional_certifications: extraCertifications.map(({ name }) => name)
        };
    }
    const industries = splitUnique(form.industriesServed, /\r?\n/, compareName);
    offering.custom_offering_fields = {
        ...offeringCustom,
        ...(clean(form.productionMode) && { production_mode: clean(form.productionMode) }),
        ...(industries.length && { industries_served: industries }),
        ...(clean(form.otherServiceInformation) && { other_service_information: clean(form.otherServiceInformation) })
    };
    offering.custom_capability_fields = {
        ...offering.custom_capability_fields, ...capabilityCustom,
        ...(extraMaterials.length && { additional_materials: extraMaterials.map(({ name, grades: value }) => (
            { name, available_grades: grades(value) }
        )) }),
        ...(extraProcesses.length && { additional_processes: extraProcesses.map(({ name }) => name) })
    };

    return { payload, errors };
}
