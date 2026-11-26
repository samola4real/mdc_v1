import {
    FAMILY_RANGES, GENERAL_RANGES, QUALITY_STANDARDS, SUPPORT_STATUSES, buildRegistrationPayload, clean,
    controlledSelection, emptyRegistrationForm, evidence, isReservedCustomName, readCustomMap, readNamedRows,
    registrationPartRanges, requiredText, validateGearQuality, validateRanges
} from './providerRegistrationPayload.js';

const preservedMessage = 'The saved format is preserved. This field cannot be edited here.';
const record = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);
const text = (value) => typeof value === 'string';
const lines = (value) => Array.isArray(value) && value.every((item) => text(item) && !/[\r\n]/.test(item));
const bounds = ['min', 'max', 'value'];

export function sameValue(left, right) {
    if (left === right) return true;
    if (Array.isArray(left) && Array.isArray(right)) {
        return left.length === right.length && left.every((item, index) => sameValue(item, right[index]));
    }
    return record(left) && record(right) && Object.keys(left).length === Object.keys(right).length
        && Object.keys(left).every((key) => Object.hasOwn(right, key) && sameValue(left[key], right[key]));
}

export const editorDirty = (editor) => Boolean(editor && !sameValue(editor.initial, editor.draft));
export const readableCode = (value) => String(value ?? '').replace(/[_-]+/g, ' ').replace(/^\w/, (letter) => letter.toUpperCase());
export const catalogueLabel = (options, value) => options?.find((item) => item.value === value)?.label || readableCode(value);

export function withSavedOptions(options = [], values) {
    const unknown = [...new Set(values)].filter((value) => value && !options.some((item) => item.value === value));
    return [...options, ...unknown.map((value) => ({ value, label: readableCode(value), disabled: true }))];
}

function saved(source, key, locked, field, isSupported, fallback = '') {
    if (!Object.hasOwn(source, key)) return fallback;
    if (isSupported(source[key])) return source[key];
    locked[field] = preservedMessage;
    return fallback;
}

const customTexts = {
    tolerance: ['familyDetails', 'tolerance'],
    surface_finish: ['familyDetails', 'surfaceFinish'],
    quality_tolerance_standard: ['familyDetails', 'qualityToleranceStandard'],
    tolerance_class_fit: ['familyDetails', 'toleranceClassFit'],
    notes: ['capabilityNotes']
};

const materialRows = (value) => Array.isArray(value) && value.every((item) => record(item) && text(item.name) && lines(item.available_grades));
const named = (items) => items.map((name, index) => ({ id: -index - 1, name }));
const gradeText = (items) => items.join('\n');

function customRows(map, technical) {
    return Object.entries(map).filter(([name, value]) => (
        clean(name) === name && !isReservedCustomName(name)
        && (technical ? record(value) && text(value.value) && ['unit', 'notes'].every((key) => !Object.hasOwn(value, key) || text(value[key]))
            : text(value))
    )).map(([name, value], index) => ({
        id: -index - 1, name, ...(technical ? { value: value.value, unit: value.unit, notes: value.notes } : { value })
    }));
}

function hydrateRanges(map, ranges, locked, prefix) {
    const result = {};
    for (const range of ranges) {
        const item = map[range.key];
        for (const bound of bounds) {
            const field = range[bound];
            if (!field || item == null) continue;
            if (record(item) && Number.isFinite(item[bound])) result[field] = item[bound];
            else if (!record(item) || Object.hasOwn(item, bound)) locked[prefix + '.' + field] = preservedMessage;
        }
    }
    return result;
}

function partRangeMap(root, ranges) {
    return ranges.some((range) => range.key === 'width_mm') ? root.bounding_box_mm || {} : root;
}

function editor(resource, form, locked) {
    return { resource, initial: form, draft: form, locked };
}

export function providerEditor(resource) {
    const { provider_id, provider_name, country, certifications, custom_provider_fields: custom = {} } = resource.data;
    const locked = {};
    return editor(resource, {
        ...emptyRegistrationForm(), providerId: provider_id, providerName: provider_name, country,
        description: saved(custom, 'description', locked, 'description', text),
        certifications: (certifications || []).map(({ code }) => code),
        otherCertifications: named(saved(custom, 'additional_certifications', locked, 'otherCertifications', lines, []))
    }, locked);
}

export function offeringEditor(resource) {
    const data = resource.data;
    const family = data.part_family;
    const partRecords = data.supported_part_types || [];
    const familyMap = data.family_capabilities || {};
    const typed = data.part_type_capabilities || {};
    const generic = data.generic_capabilities || {};
    const service = data.custom_offering_fields || {};
    const custom = data.custom_capability_fields || {};
    const materialRecords = generic.materials || [];
    const locked = {};
    const form = {
        ...emptyRegistrationForm(), offeringId: data.offering_id, offeringName: data.offering_name,
        partFamily: family, serviceCategory: data.service_category, supportStatus: data.support_status,
        partTypes: partRecords.map(({ part_type }) => part_type),
        partTypeStatuses: Object.fromEntries(partRecords.map(({ part_type, support_status }) => [part_type, support_status])),
        hasSavedCapabilities: Object.keys(typed),
        familyDetails: hydrateRanges(familyMap, FAMILY_RANGES[family] || [], locked, 'familyDetails'),
        general: hydrateRanges(generic, GENERAL_RANGES, locked, 'general'),
        materials: [...new Set(materialRecords.map(({ material }) => material))],
        processes: [...new Set((generic.processes || []).map(({ process }) => process))],
        productionMode: saved(service, 'production_mode', locked, 'productionMode', text),
        industriesServed: gradeText(saved(service, 'industries_served', locked, 'industriesServed', lines, [])),
        otherServiceInformation: saved(service, 'other_service_information', locked, 'otherServiceInformation', text),
        customOfferingFields: customRows(service, false),
        additionalProcesses: named(saved(custom, 'additional_processes', locked, 'additionalProcesses', lines, [])),
        customCapabilityFields: customRows(custom, true)
    };

    for (const [key, parts] of Object.entries(customTexts)) {
        if (parts.length === 1) form[parts[0]] = saved(custom, key, locked, parts[0], text);
        else if (family !== 'gear' || !['quality_tolerance_standard', 'tolerance_class_fit'].includes(key)) {
            form.familyDetails[parts[1]] = saved(custom, key, locked, parts.join('.'), text);
        }
    }
    if (family === 'gear') {
        const quality = familyMap.gear_quality || {};
        form.familyDetails.qualityStandard = saved(quality, 'standard', locked, 'familyDetails.qualityStandard',
            (value) => QUALITY_STANDARDS.includes(value));
        const legacy = saved(custom, 'quality_class', locked, 'familyDetails.qualityClass', text);
        const best = saved(quality, 'best_class', locked, 'familyDetails.qualityClass', Number.isFinite);
        if (best !== '' && Object.hasOwn(custom, 'quality_class')) locked['familyDetails.qualityClass'] = preservedMessage;
        form.familyDetails.qualityClass = best === '' ? legacy : String(best);
    }
    form.partMeasurements = Object.fromEntries(form.partTypes.map((type) => {
        const ranges = registrationPartRanges(family, type);
        return [type, hydrateRanges(partRangeMap(typed[type] || {}, ranges), ranges, locked, 'partMeasurements.' + type)];
    }));
    form.materialGrades = Object.fromEntries(form.materials.map((code) => {
        const field = 'materialGrades.' + code;
        const matching = materialRecords.filter(({ material }) => material === code);
        const grades = matching.flatMap((item) => saved(item, 'available_grades', locked, field, lines, []));
        if (matching.length > 1) locked[field] = 'This material has multiple saved records. Their grades are preserved.';
        return [code, gradeText(grades)];
    }));
    form.additionalMaterials = saved(custom, 'additional_materials', locked, 'additionalMaterials', materialRows, [])
        .map((item, index) => ({ id: -index - 1, name: item.name, grades: gradeText(item.available_grades) }));
    form.savedSpecifications = [
        ['Diametral pitch', familyMap.diametral_pitch, ''],
        ['Minimum shaft length', Number.isFinite(familyMap.length_mm?.min) ? { value: familyMap.length_mm.min } : {}, ' mm'],
        ['Saved numeric tolerance', generic.tolerance_mm, ' mm'],
        ['Saved numeric surface finish', generic.surface_finish_ra_um, ' µm Ra']
    ].flatMap(([label, entry, unit]) => {
        const values = bounds.filter((bound) => Number.isFinite(entry?.[bound]))
            .map((bound) => (bound === 'value' ? '' : bound + ' ') + entry[bound] + unit);
        return values.length ? [{ label, value: values.join(', ') }] : [];
    });
    return editor(resource, form, locked);
}

const protect = (field, locked, errors) => {
    if (!locked[field]) return true;
    errors[field] = preservedMessage;
    return false;
};

function putText(result, key, field, next, initial, locked, errors) {
    if (next === initial || !protect(field, locked, errors)) return;
    const value = clean(next);
    if (value) result[key] = value;
    else delete result[key];
}

function putList(result, key, items) {
    if (items.length) result[key] = items;
    else delete result[key];
}

function readLines(draft, original = [], normalize = (value) => value) {
    const saved = [...original];
    const seen = new Set();
    const result = [];
    for (const value of draft.split(/\r?\n/).map(clean).filter(Boolean)) {
        const index = saved.findIndex((item) => clean(item) === value);
        const key = normalize(value);
        if (index >= 0) result.push(saved.splice(index, 1)[0]);
        else if (!seen.has(key)) result.push(value);
        seen.add(key);
    }
    return result;
}

function editNamedList(result, key, field, draft, initial, locked, errors, options) {
    if (sameValue(draft[field], initial[field]) || !protect(field, locked, errors)) return;
    const rows = readNamedRows(draft[field], field, errors, options);
    putList(result, key, rows.map((row) => {
        const savedRow = initial[field].find(({ id }) => id === row.id);
        return savedRow && clean(savedRow.name) === row.name ? savedRow.name : row.name;
    }));
}

function recordsFor(values, originals, key, extra = {}) {
    const saved = originals.filter((item) => values.includes(item[key]));
    const added = values.filter((value) => !originals.some((item) => item[key] === value));
    return [...saved, ...added.map((value) => ({ [key]: value, ...evidence, ...extra }))];
}

function editSelection(values, originalValues, options, field, errors) {
    const ordered = retainSelectionOrder(values, originalValues);
    return sameValue(ordered, originalValues) ? ordered : controlledSelection(ordered, options, field, errors);
}

function addChanged(patch, previous, field, value) {
    if (!sameValue(previous[field], value)) patch[field] = value;
}

export function buildProviderEdit({ resource, initial, draft, locked }, filters) {
    const previous = resource.data;
    const errors = {};
    const patch = {};
    requiredText(errors, 'providerName', draft.providerName, 'the provider name', 255);
    requiredText(errors, 'country', draft.country, 'the country', 100);
    for (const [wire, field] of [['provider_name', 'providerName'], ['country', 'country']]) {
        if (draft[field] !== initial[field]) addChanged(patch, previous, wire, clean(draft[field]));
    }
    const certifications = editSelection(draft.certifications, initial.certifications, filters?.certifications, 'certifications', errors);
    if (!sameValue(certifications, initial.certifications)) {
        addChanged(patch, previous, 'certifications', recordsFor(certifications, previous.certifications || [], 'code'));
    }
    const custom = { ...previous.custom_provider_fields };
    putText(custom, 'description', 'description', draft.description, initial.description, locked, errors);
    editNamedList(custom, 'additional_certifications', 'otherCertifications', draft, initial, locked, errors, filters?.certifications);
    if (!sameValue(previous.custom_provider_fields || {}, custom)) patch.custom_provider_fields = custom;
    return { patch, errors };
}

function editRanges(map, ranges, next, initial, prefix, locked, errors) {
    const result = { ...map };
    validateRanges(ranges, next, prefix, errors);
    for (const range of ranges) {
        const changed = bounds.filter((bound) => range[bound] && !sameValue(next[range[bound]], initial[range[bound]]));
        if (!changed.length) continue;
        const item = { ...(map[range.key] || evidence) };
        for (const bound of changed) {
            const field = range[bound];
            if (!protect(prefix + '.' + field, locked, errors)) continue;
            if (next[field] == null || next[field] === '') delete item[bound];
            else item[bound] = next[field];
        }
        if (item.min > item.max) {
            errors[prefix + '.' + (range.min || range.max)] = 'Minimum must be less than or equal to maximum, including saved bounds.';
        }
        if (Object.keys(item).length) result[range.key] = item;
        else delete result[range.key];
    }
    return result;
}

function editQuality(family, custom, draft, initial, locked, errors) {
    validateGearQuality(draft, errors);
    const quality = { ...family.gear_quality };
    let changed = false;
    for (const [field, key] of [['qualityStandard', 'standard'], ['qualityClass', 'best_class']]) {
        if (draft[field] === initial[field] || !protect('familyDetails.' + field, locked, errors)) continue;
        changed = true;
        const value = clean(draft[field]);
        if (field === 'qualityStandard') {
            if (value) quality[key] = value;
            else delete quality[key];
        } else {
            if (Number(value) > 0 && Number.isFinite(Number(value))) quality[key] = Number(value);
            else delete quality[key];
            if (value && Number.isNaN(Number(value))) custom.quality_class = value;
            else delete custom.quality_class;
        }
    }
    if (changed) {
        if (Object.keys(quality).length) family.gear_quality = { ...(family.gear_quality ? {} : evidence), ...quality };
        else delete family.gear_quality;
    }
}

function editCustomRows(map, field, draft, initial, errors, technical = false) {
    if (sameValue(draft, initial)) return map;
    const editable = new Set(initial.map(({ name }) => name));
    const preserved = Object.keys(map).filter((name) => !editable.has(name));
    const submitted = readCustomMap(draft, field, errors, technical, preserved);
    if (Object.keys(errors).some((key) => key.startsWith(field + '.'))) return map;
    const result = { ...map };
    for (const { name } of initial) delete result[name];
    for (const row of draft) {
        const name = clean(row.name);
        if (!Object.hasOwn(submitted, name)) continue;
        const before = initial.find(({ id }) => row.id === id);
        const savedValue = before && map[before.name];
        if (!technical || !before) {
            result[name] = before && row.value === before.value ? savedValue : submitted[name];
            continue;
        }
        const item = { ...savedValue };
        for (const key of ['value', 'unit', 'notes']) {
            if (row[key] === before[key]) continue;
            if (Object.hasOwn(submitted[name], key)) item[key] = submitted[name][key];
            else delete item[key];
        }
        result[name] = item;
    }
    return result;
}

function editAdditionalMaterials(custom, original, draft, initial, locked, errors, filters) {
    const field = 'additionalMaterials';
    if (sameValue(draft[field], initial[field]) || !protect(field, locked, errors)) return;
    const rows = readNamedRows(draft[field], field, errors, filters?.materials);
    putList(custom, 'additional_materials', rows.map((row) => {
        const prior = initial[field].find(({ id }) => row.id === id);
        const savedRow = prior ? original.additional_materials[-prior.id - 1] : {};
        return {
            ...savedRow, name: prior && clean(prior.name) === row.name ? prior.name : row.name,
            available_grades: prior && row.grades === prior.grades ? savedRow.available_grades
                : readLines(row.grades || '', savedRow.available_grades)
        };
    }));
}

function editTyped(previous, initial, draft, types, locked, errors) {
    const supported = recordsFor(types, previous.supported_part_types || [], 'part_type').map((item) => {
        const status = draft.partTypeStatuses[item.part_type];
        if (!SUPPORT_STATUSES.some(({ value }) => value === status)) errors['partTypeStatuses.' + item.part_type] = 'Select a part type support status.';
        return { ...item, support_status: status };
    });
    const typed = { ...previous.part_type_capabilities };
    for (const type of selectsRemoval(initial.partTypes, types)) delete typed[type];
    for (const { part_type: type, support_status: status } of supported) {
        if (status !== 'confirmed') {
            if (initial.partTypeStatuses[type] !== status) delete typed[type];
            continue;
        }
        const old = previous.part_type_capabilities?.[type] || {};
        const ranges = registrationPartRanges(initial.partFamily, type);
        const working = draft.partMeasurements[type] || {};
        if (sameValue(working, initial.partMeasurements[type] || {})) continue;
        const measures = editRanges(partRangeMap(old, ranges), ranges, working,
            initial.partMeasurements[type] || {}, 'partMeasurements.' + type, locked, errors);
        const next = ranges.some((range) => range.key === 'width_mm') ? { ...old } : measures;
        if (next !== measures) {
            if (Object.keys(measures).length) next.bounding_box_mm = measures;
            else delete next.bounding_box_mm;
        }
        if (Object.keys(next).length) typed[type] = next;
        else delete typed[type];
    }
    return { supported, typed };
}

export function buildOfferingEdit({ resource, initial, draft, locked }, filters) {
    const previous = resource.data;
    const errors = {};
    const patch = {};
    requiredText(errors, 'offeringName', draft.offeringName, 'the offering name', 255);
    if (draft.offeringName !== initial.offeringName) addChanged(patch, previous, 'offering_name', clean(draft.offeringName));
    if (draft.supportStatus !== initial.supportStatus) {
        if (!SUPPORT_STATUSES.some(({ value }) => value === draft.supportStatus)) errors.supportStatus = 'Select an offering support status.';
        else patch.support_status = draft.supportStatus;
    }
    const types = editSelection(draft.partTypes, initial.partTypes, filters?.partTypes[initial.partFamily], 'partTypes', errors);
    const { supported, typed } = editTyped(previous, initial, draft, types, locked, errors);
    if (!sameValue(previous.supported_part_types || [], supported)) patch.supported_part_types = supported;
    if (!sameValue(previous.part_type_capabilities || {}, typed)) patch.part_type_capabilities = typed;

    const family = editRanges(previous.family_capabilities || {}, FAMILY_RANGES[initial.partFamily] || [],
        draft.familyDetails, initial.familyDetails, 'familyDetails', locked, errors);
    const generic = editRanges(previous.generic_capabilities || {}, GENERAL_RANGES, draft.general, initial.general, 'general', locked, errors);
    const materials = editSelection(draft.materials, initial.materials, filters?.materials, 'materials', errors);
    if (!sameValue(materials, initial.materials) || materials.some((item) => draft.materialGrades[item] !== initial.materialGrades[item])) {
        generic.materials = recordsFor(materials, generic.materials || [], 'material').map((item) => {
            const code = item.material;
            const field = 'materialGrades.' + code;
            if (draft.materialGrades[code] === initial.materialGrades[code] || !protect(field, locked, errors)) return item;
            return { ...item, available_grades: readLines(draft.materialGrades[code] || '', item.available_grades) };
        });
    }
    const processes = editSelection(draft.processes, initial.processes, filters?.processes, 'processes', errors);
    if (!sameValue(processes, initial.processes)) {
        generic.processes = recordsFor(processes, generic.processes || [], 'process', { delivery_mode: 'unspecified' });
    }
    const service = editCustomRows({ ...previous.custom_offering_fields }, 'customOfferingFields', draft.customOfferingFields,
        initial.customOfferingFields, errors);
    putText(service, 'production_mode', 'productionMode', draft.productionMode, initial.productionMode, locked, errors);
    putText(service, 'other_service_information', 'otherServiceInformation', draft.otherServiceInformation, initial.otherServiceInformation, locked, errors);
    if (draft.industriesServed !== initial.industriesServed && protect('industriesServed', locked, errors)) {
        putList(service, 'industries_served', readLines(draft.industriesServed, service.industries_served, (value) => value.toLowerCase()));
    }
    const originalCustom = previous.custom_capability_fields || {};
    const custom = editCustomRows({ ...originalCustom }, 'customCapabilityFields', draft.customCapabilityFields,
        initial.customCapabilityFields, errors, true);
    for (const [key, parts] of Object.entries(customTexts)) {
        const [group, field] = parts;
        if (!field) putText(custom, key, group, draft[group], initial[group], locked, errors);
        else if (initial.partFamily !== 'gear' || !['quality_tolerance_standard', 'tolerance_class_fit'].includes(key)) {
            putText(custom, key, parts.join('.'), draft[group][field], initial[group][field], locked, errors);
        }
    }
    if (initial.partFamily === 'gear') editQuality(family, custom, draft.familyDetails, initial.familyDetails, locked, errors);
    editNamedList(custom, 'additional_processes', 'additionalProcesses', draft, initial, locked, errors, filters?.processes);
    editAdditionalMaterials(custom, originalCustom, draft, initial, locked, errors, filters);
    for (const [key, value] of Object.entries({
        family_capabilities: family, generic_capabilities: generic, custom_offering_fields: service, custom_capability_fields: custom
    })) if (!sameValue(previous[key] || {}, value)) patch[key] = value;
    return { patch, errors };
}

export function buildAddedOffering(form, provider, filters) {
    const { payload, errors } = buildRegistrationPayload({
        ...form, providerId: provider.provider_id, providerName: provider.provider_name, country: provider.country
    }, filters);
    return { payload: payload.offerings[0], errors };
}

export function selectsRemoval(previous, next) {
    return previous.filter((value) => !next.includes(value));
}

export function retainSelectionOrder(values, original) {
    return [...original.filter((value) => values.includes(value)), ...values.filter((value) => !original.includes(value))];
}

export function retainedPartDraft(form, types) {
    const statuses = { ...form.partTypeStatuses };
    for (const type of types) if (!Object.hasOwn(statuses, type)) statuses[type] = form.supportStatus;
    return { ...form, partTypes: retainSelectionOrder(types, Object.keys(statuses)), partTypeStatuses: statuses };
}
