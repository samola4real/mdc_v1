const declared = { source_type: 'provider_confirmed', confidence: 'declared' };
const scalar = (value) => typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean';
const text = (value) => String(value ?? '').trim();
const changed = (a, b) => JSON.stringify(a) !== JSON.stringify(b);
const hasKeys = (value) => Object.keys(value).length > 0;

const genericFields = {
    batch_size: { min: 'batchSizeMin', max: 'batchSizeMax' },
    lead_time_weeks: { min: 'leadTimeMinWeeks', max: 'leadTimeMaxWeeks' },
    weight_kg: { max: 'weightMaxKg' }
};
const familyFields = {
    gear: {
        module: { min: 'moduleMin', max: 'moduleMax' },
        outside_diameter_mm: { min: 'diameterMinMm', max: 'diameterMaxMm' }
    },
    shaft: {
        length_mm: { max: 'lengthMaxMm' },
        outer_diameter_mm: { min: 'outerDiameterMinMm', max: 'outerDiameterMaxMm' }
    }
};
const boxFields = {
    length_mm: { max: 'maxLengthMm' },
    width_mm: { max: 'maxWidthMm' },
    height_mm: { max: 'maxHeightMm' }
};
export const BOX_PART_TYPES = ['block', 'plate', 'bracket'];
export const ROUND_PART_TYPES = ['bushing', 'roller', 'collar'];
const customNotes = {
    notes: 'capabilityNotes', tolerance: 'tolerance', surface_finish: 'surfaceFinish'
};

export const emptyProviderForm = () => ({
    providerId: '', providerName: '', country: '', description: '',
    offeringId: '', offeringName: '', serviceCategory: '', partFamily: '',
    supportStatus: 'confirmed', partTypes: [], materials: [], availableGrades: '',
    processes: [], certifications: [], customOfferingFields: [], customCapabilityFields: [],
    qualityClass: '', qualityStandard: null, capabilityNotes: '', tolerance: '', surfaceFinish: ''
});

const readRanges = (form, values, fields) => {
    for (const [key, sides] of Object.entries(fields)) {
        for (const [side, input] of Object.entries(sides)) form[input] = values?.[key]?.[side] ?? null;
    }
};

// Each legacy form input controls only its named leaf. Keep other record metadata and siblings.
const editRanges = (previous = {}, fields, form, initial) => {
    const result = { ...previous };
    for (const [key, sides] of Object.entries(fields)) {
        if (!Object.values(sides).some((input) => changed(form[input] ?? null, initial[input] ?? null))) continue;
        const record = { ...declared, ...previous[key] };
        for (const [side, input] of Object.entries(sides)) {
            if (!changed(form[input] ?? null, initial[input] ?? null)) continue;
            if (form[input] == null || form[input] === '') delete record[side];
            else record[side] = form[input];
        }
        if (Object.keys(record).some((field) => !Object.hasOwn(declared, field))) result[key] = record;
        else delete result[key];
    }
    return result;
};

const editableRows = (values = {}, reserved = []) => Object.entries(values)
    .filter(([name, value]) => !reserved.includes(name) && (scalar(value) || scalar(value?.value)))
    .map(([name, value]) => ({
        name, value: text(scalar(value) ? value : value.value), unit: text(value?.unit), notes: text(value?.notes)
    }));

const editCustomRows = (rows, initialRows, previous = {}, capability = false) => {
    const result = Object.assign(Object.create(null), previous);
    const keyedRows = new Map(rows.filter(({ name, value }) => text(name) && text(value)).map((row) => [text(row.name), row]));
    for (const { name } of initialRows) {
        if (!keyedRows.has(name)) delete result[name];
    }
    for (const [name, row] of keyedRows) {
        const initialRow = initialRows.find((item) => item.name === name);
        if (initialRow && !changed(row, initialRow)) continue;
        // Opaque backend values are not shown in the form and cannot be replaced by a new row.
        if (Object.hasOwn(previous, name) && !initialRow) continue;
        if (!capability && scalar(previous[name] ?? '')) {
            result[name] = text(row.value);
        } else {
            const record = { ...(scalar(previous[name]) ? {} : previous[name]), value: text(row.value) };
            for (const key of ['unit', 'notes']) {
                if (text(row[key])) record[key] = text(row[key]);
                else delete record[key];
            }
            result[name] = record;
        }
    }
    return { ...result };
};

const selectedRecords = (selected, previous, key, defaults = {}) => selected.map((value) => (
    (previous || []).find((item) => item[key] === value) || { [key]: value, ...defaults, ...declared }
));

const confirmedPart = (part, supported) => supported.some(({ part_type, support_status }) => (
    part_type === part && support_status === 'confirmed'
));

export const hydrateProviderForm = (provider, offering) => {
    const form = {
        ...emptyProviderForm(),
        providerId: provider.provider_id,
        providerName: provider.provider_name,
        country: provider.country ?? '',
        description: text(provider.custom_provider_fields?.description),
        certifications: (provider.certifications || []).map((item) => item.code)
    };
    if (!offering) return form;
    const generic = offering.generic_capabilities || {};
    const family = offering.family_capabilities || {};
    const part = offering.part_type_capabilities || {};
    const custom = offering.custom_capability_fields || {};
    const partTypes = (offering.supported_part_types || []).map((item) => item.part_type);
    Object.assign(form, {
        offeringId: offering.offering_id, offeringName: offering.offering_name,
        supportStatus: offering.support_status, serviceCategory: offering.service_category,
        partFamily: offering.part_family, partTypes,
        materials: (generic.materials || []).map((item) => item.material),
        availableGrades: generic.materials?.length === 1 ? (generic.materials[0].available_grades || []).join(', ') : '',
        processes: (generic.processes || []).map((item) => item.process),
        customOfferingFields: editableRows(offering.custom_offering_fields),
        customCapabilityFields: editableRows(custom, [...Object.keys(customNotes), 'quality_class'])
    });
    readRanges(form, generic, genericFields);
    readRanges(form, family, familyFields[form.partFamily] || {});
    form.qualityStandard = family.gear_quality?.standard ?? null;
    form.qualityClass = text(family.gear_quality?.best_class ?? custom.quality_class);
    form.splineModule = part.splined_shaft?.spline_module?.value ?? null;
    const selected = partTypes.length === 1 ? part[partTypes[0]] : null;
    readRanges(form, selected?.bounding_box_mm, boxFields);
    form.maxDiameterMm = selected?.outer_diameter_mm?.max ?? null;
    for (const [key, input] of Object.entries(customNotes)) form[input] = text(custom[key]);
    return form;
};

const editDescription = (form, initial, previous = {}) => {
    const result = { ...previous };
    if (changed(form.description, initial.description)) {
        if (text(form.description)) result.description = text(form.description);
        else delete result.description;
    }
    return result;
};

const makeOffering = (form, initial, previous = {}) => {
    const supported = selectedRecords(form.partTypes, previous.supported_part_types, 'part_type', {
        support_status: form.supportStatus
    });
    const family = editRanges(previous.family_capabilities, familyFields[form.partFamily] || {}, form, initial);
    const generic = editRanges(previous.generic_capabilities, genericFields, form, initial);
    const custom = editCustomRows(form.customCapabilityFields, initial.customCapabilityFields, previous.custom_capability_fields, true);
    for (const [key, input] of Object.entries(customNotes)) {
        if (changed(form[input], initial[input])) {
            if (text(form[input])) custom[key] = text(form[input]);
            else delete custom[key];
        }
    }
    if (form.partFamily === 'gear' && (changed(form.qualityClass, initial.qualityClass)
        || changed(form.qualityStandard, initial.qualityStandard))) {
        const quality = { ...declared, ...family.gear_quality };
        const bestClass = Number(form.qualityClass);
        if (form.qualityStandard) quality.standard = form.qualityStandard;
        else delete quality.standard;
        if (bestClass > 0 && Number.isFinite(bestClass)) quality.best_class = bestClass;
        else delete quality.best_class;
        if (quality.standard || quality.best_class || Object.keys(quality).some((key) => !Object.hasOwn(declared, key))) {
            family.gear_quality = quality;
        } else delete family.gear_quality;
        if (text(form.qualityClass) && !(bestClass > 0)) custom.quality_class = text(form.qualityClass);
        else delete custom.quality_class;
    }

    if (changed(form.materials, initial.materials) || (form.materials.length === 1 && changed(form.availableGrades, initial.availableGrades))) {
        generic.materials = selectedRecords(form.materials, previous.generic_capabilities?.materials, 'material');
        if (generic.materials.length === 1 && changed(form.availableGrades, initial.availableGrades)) {
            generic.materials[0] = {
                ...generic.materials[0], available_grades: form.availableGrades.split(',').map(text).filter(Boolean)
            };
        }
    }
    if (changed(form.processes, initial.processes)) {
        generic.processes = selectedRecords(form.processes, previous.generic_capabilities?.processes, 'process', {
            delivery_mode: 'unspecified'
        });
    }

    const part = Object.fromEntries(Object.entries(previous.part_type_capabilities || {})
        .filter(([name]) => confirmedPart(name, supported)));
    if (confirmedPart('splined_shaft', supported)) {
        const next = editRanges(part.splined_shaft, { spline_module: { value: 'splineModule' } }, form, initial);
        if (hasKeys(next)) part.splined_shaft = next;
        else delete part.splined_shaft;
    }
    const [onlyType] = form.partTypes;
    if (form.partTypes.length === 1 && confirmedPart(onlyType, supported)) {
        let next = { ...part[onlyType] };
        if (BOX_PART_TYPES.includes(onlyType)) {
            const box = editRanges(next.bounding_box_mm, boxFields, form, initial);
            if (hasKeys(box)) next.bounding_box_mm = box;
            else delete next.bounding_box_mm;
        }
        if (ROUND_PART_TYPES.includes(onlyType)) {
            next = editRanges(next, { outer_diameter_mm: { max: 'maxDiameterMm' } }, form, initial);
        }
        if (hasKeys(next)) part[onlyType] = next;
        else delete part[onlyType];
    }

    return {
        offering_name: text(form.offeringName),
        support_status: form.supportStatus,
        supported_part_types: supported,
        family_capabilities: family,
        part_type_capabilities: part,
        generic_capabilities: generic,
        custom_offering_fields: editCustomRows(form.customOfferingFields, initial.customOfferingFields, previous.custom_offering_fields),
        custom_capability_fields: custom
    };
};

export const buildOfferingCreation = (form) => ({
    offering_id: text(form.offeringId),
    service_category: form.serviceCategory,
    part_family: form.partFamily,
    ...makeOffering(form, emptyProviderForm())
});

export const buildProviderPreviewPayload = (form) => ({
    contract_version: '1.0',
    provider_id: text(form.providerId),
    provider_name: text(form.providerName),
    country: text(form.country),
    ...(text(form.description) ? { custom_provider_fields: { description: text(form.description) } } : {}),
    certifications: selectedRecords(form.certifications, [], 'code'),
    offerings: [buildOfferingCreation(form)]
});

export const buildProviderPatches = (form, provider, offering) => {
    if (!provider) return { provider: {}, offering: {} };
    const initial = hydrateProviderForm(provider, offering);
    const patch = {};
    if (changed(form.providerName, initial.providerName)) patch.provider_name = text(form.providerName);
    if (changed(form.country, initial.country)) patch.country = text(form.country);
    if (changed(form.description, initial.description)) {
        patch.custom_provider_fields = editDescription(form, initial, provider.custom_provider_fields);
    }
    if (changed(form.certifications, initial.certifications)) {
        patch.certifications = selectedRecords(form.certifications, provider.certifications, 'code');
    }
    const offeringPatch = {};
    if (offering) {
        const next = makeOffering(form, initial, offering);
        const original = makeOffering(initial, initial, offering);
        for (const [key, value] of Object.entries(next)) {
            if (changed(value, original[key])) offeringPatch[key] = value;
        }
    }
    return { provider: patch, offering: offeringPatch };
};
