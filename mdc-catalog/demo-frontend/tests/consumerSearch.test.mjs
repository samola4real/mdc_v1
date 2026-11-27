import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import {
    buildSearchPayload, changePartSelection, getSpecificationProfile, resetSearchForm, validateSearchCatalogue
} from '../src/components/mdc/consumerSearchCriteria.js';
import {
    EVIDENCE_GROUPS, formatCapabilityRange, formatEvidenceList, formatSuitability, NOT_PROVIDED, offeringKey, validateSearchResponse
} from '../src/components/mdc/searchResultFormatters.js';

const options = (...values) => values.map((value) => ({ value, label: value }));
const catalog = {
    partFamilies: options('shaft', 'gear', 'metal_part'),
    partTypes: {
        gear: options('helical_gear', 'spur_gear', 'crown_gear', 'worm_gear', 'bevel_gear'),
        shaft: options('plain_shaft', 'splined_shaft', 'hollow_shaft', 'stepped_shaft', 'worm_shaft'),
        metal_part: options('block', 'plate', 'bracket', 'bushing', 'roller', 'collar')
    },
    serviceCategoryByFamily: { gear: 'precision_gears', shaft: 'precision_shafts', metal_part: 'precision_metal_parts' },
    materials: options('steel', 'aluminum'),
    processes: options('milling', 'drilling'),
    certifications: options('ISO9001_2015', 'ISO14001_2015')
};
const formFor = (partFamily, partType, specifications = {}) => ({
    ...resetSearchForm(catalog), partFamily, partType, specifications
});
const build = (form) => buildSearchPayload(form, catalog, 'keycloak-subject-fixture');
const max = (value) => ({ max: value });
const exact = (value) => ({ exact: value });
const criteria = (family, partType, specifications) => (
    JSON.parse(JSON.stringify(build(formFor(family, partType, specifications)).payload)).requirements
);
const expected = (part_family_specifications, part_type_specifications, generic_requirements = {}) => ({
    part_family_specifications, part_type_specifications, generic_requirements
});

test('catalogue selections use valid live options and derive the default when gear or spur gear is missing', () => {
    assert.equal(validateSearchCatalogue(catalog), catalog);
    assert.equal(resetSearchForm(catalog).partType, 'spur_gear');
    const helicalOnly = { ...catalog, partTypes: { ...catalog.partTypes, gear: options('helical_gear') } };
    assert.equal(resetSearchForm(helicalOnly).partType, 'helical_gear');
    const noGears = { ...catalog, partTypes: { ...catalog.partTypes, gear: [] } };
    assert.equal(resetSearchForm(noGears).partFamily, 'shaft');
    assert.equal(resetSearchForm(noGears).partType, 'plain_shaft');
    assert.throws(() => validateSearchCatalogue({ ...catalog, partTypes: {} }));
    assert.throws(() => validateSearchCatalogue({ ...catalog, materials: [{}] }));
    assert(build({ ...formFor('gear', 'spur_gear'), materials: ['not-in-catalogue'] }).errors.selection);
    assert(build(formFor('gear', 'plain_shaft')).errors.selection);
});

test('gear submits exact, inclusive range, maximum, quality and generic criteria with full decimal precision', () => {
    const gear = formFor('gear', 'spiral_gear', {});
    assert(build(gear).errors.selection);
    const form = {
        ...formFor('gear', 'spur_gear', {
            module: '2,125', diametralPitch: '4.75', outsideDiameterMm: '120.125',
            toleranceMm: '0.0005625', faceWidthMm: '18.75',
            qualityStandard: '  DIN 3962 ', qualityClass: '5.25',
            materialGrade: 'unsubmitted grade', technicalRequirements: 'unsupported'
        }),
        materials: ['steel', 'aluminum', 'steel'], processes: ['milling', 'drilling'], certifications: ['ISO9001_2015', 'ISO14001_2015']
    };
    const { payload } = build(form);
    assert.equal(payload.consumer_id, 'keycloak-subject-fixture');
    assert.equal(payload.contract_version, '1.0');
    assert.equal(payload.service_category, 'precision_gears');
    assert.deepEqual(payload.match_policy, { discovery_mode: 'lenient' });
    assert.deepEqual(payload.requirements, expected({
        module: exact(2.125), diametral_pitch: { min: 4.75, max: 4.75 },
        outside_diameter_mm: max(120.125), tolerance_mm: max(0.0005625),
        gear_quality: { standard: 'DIN 3962', max_class: 5.25 }
    }, { face_width_mm: exact(18.75) }, {
        materials: ['steel', 'aluminum'], processes: ['milling', 'drilling'], certifications: ['ISO9001_2015', 'ISO14001_2015']
    }));
});

test('each submitted search generates a unique request ID and uses a neutral fallback only without a subject', () => {
    const form = resetSearchForm(catalog);
    const first = build(form).payload;
    const second = build(form).payload;
    assert.match(first.request_id, /^req-[\da-f-]{36}$/);
    assert.notEqual(first.request_id, second.request_id);
    assert.equal(second.consumer_id, first.consumer_id);
    assert.equal(buildSearchPayload(form, catalog).payload.consumer_id, 'consumer_service_discovery');
    assert.deepEqual(first.requirements, expected({}, {}));
});

test('quality can be omitted and both fields are required when one is entered', () => {
    const partial = (specifications) => build(formFor('gear', 'spur_gear', specifications));
    assert.equal(partial({}).payload.requirements.part_family_specifications.gear_quality, undefined);
    for (const specifications of [{ qualityStandard: 'ISO 1328' }, { qualityClass: '5' },
        { qualityStandard: 'ISO 1328', qualityClass: '5 extra' }, { qualityStandard: '  ', qualityClass: '5' }]) {
        const { payload, errors } = partial(specifications);
        assert.equal(payload, undefined);
        assert(errors.qualityStandard || errors.qualityClass);
    }
});

test('invalid numbers and zero or fractional hole counts block submission while blanks are omitted', () => {
    for (const rawModule of ['0', '-1', '1e', 'Infinity', '1e999', '0x2', '4 mm', ' ']) {
        const { errors, payload } = build(formFor('gear', 'spur_gear', { module: rawModule }));
        assert(errors.module, rawModule);
        assert.equal(payload, undefined);
    }
    for (const mountingHolesCount of ['0', '-1', '2.5', '3.0', '9007199254740993']) {
        assert(build(formFor('metal_part', 'block', { mountingHolesCount })).errors.mountingHolesCount);
    }
    assert.deepEqual(criteria('metal_part', 'plate', { mountingHolesCount: '', surfaceFinish: '' }), expected({}, {}));
});

test('face width belongs only to supported gear types', () => {
    assert.deepEqual(criteria('gear', 'worm_gear', { module: '1', faceWidthMm: '20' }), expected({ module: exact(1) }, {}));
    for (const type of ['spur_gear', 'helical_gear', 'bevel_gear', 'crown_gear']) {
        assert.deepEqual(criteria('gear', type, { faceWidthMm: '20' }), expected({}, { face_width_mm: exact(20) }));
    }
});

test('shaft keeps common dimensions and sends geometry only on its applicable type', () => {
    const draft = { lengthMm: '100', outerDiameterMm: '25', toleranceMm: '0.025', splineModule: '2.125', internalDiameterMm: '12', wallThicknessMm: '2.5' };
    const common = { length_mm: max(100), outer_diameter_mm: max(25), tolerance_mm: max(0.025) };
    for (const type of ['plain_shaft', 'stepped_shaft', 'worm_shaft']) {
        assert.deepEqual(criteria('shaft', type, draft), expected(common, {}));
    }
    assert.deepEqual(criteria('shaft', 'splined_shaft', draft), expected(common, { spline_module: exact(2.125) }));
    assert.deepEqual(criteria('shaft', 'hollow_shaft', draft), expected(common, { inner_diameter_mm: max(12), wall_thickness_mm: exact(2.5) }));
});

const metalSpecifications = {
    metalLengthMm: '70.25', metalWidthMm: '40', metalHeightMm: '22', metalThicknessMm: '5.5',
    mountingHolesCount: '4', flangeLengthMm: '14', horizontalFlangeLengthMm: '12',
    flangeDiameterMm: '18', metalInnerDiameterMm: '11', metalOuterDiameterMm: '16',
    metalWeightKg: '0.925', toleranceMm: '0.00025', surfaceFinish: '0.8',
    materialGrades: 'unsubmitted grade', holeDiameterMm: '3'
};
const box = (height) => ({ bounding_box_mm: { length_mm: max(70.25), width_mm: max(40), height_mm: max(height) } });
const rotating = { overall_length_mm: max(70.25), inner_diameter_mm: max(11), outer_diameter_mm: max(16), tolerance_mm: max(0.00025) };
const finish = { surface_finish_ra_um: max(0.8) };
const prismatic = { ...finish, weight_kg: 0.925, tolerance_mm: max(0.00025) };
const metalCases = {
    block: expected(box(22), { number_of_holes: max(4) }, prismatic),
    plate: expected(box(5.5), { number_of_holes: max(4) }, prismatic),
    bracket: expected(box(22), { vertical_flange_length_mm: max(14), horizontal_flange_length_mm: max(12) }, prismatic),
    bushing: expected(rotating, { flange_diameter_mm: max(18) }, finish),
    roller: expected(rotating, {}, { ...finish, weight_kg: 0.925 }),
    collar: expected(rotating, {}, finish)
};
for (const [type, requirements] of Object.entries(metalCases)) {
    test('metal ' + type + ' serializes only the applicable geometry and generic requirements', () => {
        assert.deepEqual(criteria('metal_part', type, metalSpecifications), requirements);
        const { title, fields } = getSpecificationProfile('metal_part', type);
        assert.equal(title, type[0].toUpperCase() + type.slice(1) + ' Specifications');
        assert(fields.length > 0);
    });
}

test('changing type or family clears all specification values and reset also clears selections', () => {
    const original = {
        ...formFor('metal_part', 'block', metalSpecifications),
        materials: ['steel', 'aluminum'], processes: ['milling'], certifications: ['ISO9001_2015']
    };
    for (const [family, type] of [['metal_part', 'plate'], ['shaft', 'hollow_shaft']]) {
        const next = changePartSelection(original, family, type);
        assert.deepEqual(next.specifications, {});
        assert.deepEqual(build(next).payload.requirements, expected({}, {}, {
            materials: ['steel', 'aluminum'], processes: ['milling'], certifications: ['ISO9001_2015']
        }));
    }
    assert.deepEqual(resetSearchForm(catalog), {
        partFamily: 'gear', partType: 'spur_gear', materials: [], processes: [], certifications: [], specifications: {}
    });
});

test('materials can be selected, removed and cleared while preserving other search requirements', () => {
    const form = { ...formFor('gear', 'spur_gear', { module: '4' }), certifications: ['ISO9001_2015'] };
    for (const materials of [['steel', 'aluminum'], ['steel'], []]) {
        const { requirements } = build({ ...form, materials }).payload;
        assert.deepEqual(requirements.part_family_specifications, { module: exact(4) });
        assert.deepEqual(requirements.generic_requirements, {
            ...(materials.length ? { materials } : {}), certifications: form.certifications
        });
    }
});

const request = { ...build(resetSearchForm(catalog)).payload, match_policy: { discovery_mode: 'strict' } };
const offer = {
    provider_id: 'manufacturer', provider_name: 'Manufacturer', offering_id: 'service-one', offering_name: 'Service 1',
    service_category: request.service_category, part_family: request.part_family, match: { status: 'full_match', score: 1 },
    matched_capabilities: [], unmatched_capabilities: [], unknown_capabilities: []
};
const response = (results) => ({
    contract_version: '1.0', request_id: request.request_id, service_category: request.service_category,
    part_family: request.part_family, part_type: request.part_type, result_count: results.length, results
});

test('strict response validation keeps offering identities, response ordering and valid empty responses', () => {
    const other = { ...offer, offering_id: 'service-two', offering_name: 'Service 2', match: { status: 'full_match', score: 0.1 } };
    const two = response([other, offer]);
    assert.equal(validateSearchResponse(two, request), two);
    assert.notEqual(offeringKey(offer), offeringKey(other));
    assert.equal(validateSearchResponse(response([]), request).result_count, 0);
});

test('ineligible, mixed, stale and malformed responses are errors instead of reclassified results', () => {
    for (const invalid of [
        response([{ ...offer, match: { status: 'partial_match', score: 1 } }]),
        response([offer, { ...offer, offering_id: 'different', unknown_capabilities: [{ field: 'module' }] }]),
        response([{ ...offer, unmatched_capabilities: [{ field: 'module' }] }]),
        response([{ ...offer, offering_id: null }]),
        response([{ ...offer, matched_capabilities: [null] }]),
        response([offer, offer]),
        { ...response([offer]), result_count: 0 },
        { ...response([]), part_type: 'crown_gear' },
        { ...response([]), request_id: 'other-request' }
    ]) {
        assert.throws(() => validateSearchResponse(invalid, request));
    }
});

test('lenient validation accepts unresolved alternatives and partial preferences, and rejects unresolved hard evidence', () => {
    const lenient = { ...request, match_policy: { discovery_mode: 'lenient' } };
    const steel = { field: 'materials', requested: ['steel'], provided: [{ material: 'steel' }] };
    const titanium = { field: 'materials', requested: ['titanium'], provided: null };
    const delivery = { field: 'delivery', requested: 2, provided: { max: 5 } };
    const mixed = { ...offer, matched_capabilities: [steel], unknown_capabilities: [titanium] };
    const partial = { ...mixed, match: { status: 'partial_match', score: 0.5 }, unmatched_capabilities: [delivery] };
    assert.deepEqual(validateSearchResponse(response([mixed]), lenient).results, [mixed]);
    assert.deepEqual(validateSearchResponse(response([partial]), lenient).results, [partial]);
    assert.equal(formatSuitability('partial_match', 'lenient', lenient.requirements), 'Partial preference match');
    assert.equal(formatSuitability('full_match', 'lenient', lenient.requirements), 'Requirements met');
    assert.throws(() => validateSearchResponse(response([{ ...mixed, matched_capabilities: [] }]), lenient));
    assert.throws(() => validateSearchResponse(response([{ ...partial, unknown_capabilities: [{ ...titanium, field: 'module' }] }]), lenient));
    assert.throws(() => validateSearchResponse(response([{ ...partial, match: { ...partial.match, score: 2 } }]), lenient));
    assert.throws(() => validateSearchResponse(response([partial]), request));
});

test('rendering formats only returned evidence, including grades and dimensional bounds', () => {
    assert.equal(formatCapabilityRange(undefined), NOT_PROVIDED);
    assert.equal(formatCapabilityRange({ min: 1, max: 4 }), '1–4');
    assert.equal(formatCapabilityRange({ max: 0.000625 }), '≤ 0.000625');
    assert.equal(formatCapabilityRange({ standard: 'ISO 1328', best_class: 5 }), 'ISO 1328, best class 5');
    assert.equal(formatCapabilityRange({ length_mm: { max: 15 } }), 'Length (mm): ≤ 15');
    const [materials, processes, certifications] = EVIDENCE_GROUPS;
    const steel = [{ value: 'steel', label: 'Steel' }];
    assert.equal(formatEvidenceList(undefined, materials, steel), NOT_PROVIDED);
    assert.equal(formatEvidenceList([{ material: 'steel', available_grades: ['42CrMo4'] }], materials, steel), 'Steel (42CrMo4)');
    assert.equal(formatEvidenceList([{ process: 'milling', support_status: 'unknown' }], processes, catalog.processes), NOT_PROVIDED);
    assert.equal(formatEvidenceList([{ code: 'ISO9001_2015' }], certifications, [{ value: 'ISO9001_2015', label: 'ISO 9001:2015' }]), 'ISO 9001:2015');
});

test('active Consumer and shared catalogue screens omit development copy and diagnostic panels', () => {
    const consumer = ['ConsumerSearchMockup.js', 'SearchResultsList.js', 'SearchErrorMessage.js', 'ProviderResultAccordion.js']
        .map((name) => 'components/mdc/' + name);
    const screens = [...consumer, 'components/mdc/DemoRoleGuard.js', 'components/mdc/ProviderDemoPanel.js',
        'components/mdc/AdminProviderDeletion.js', 'components/mdc/ProviderManagement.js', 'layout/AppMenu.js',
        'pages/demo/index.js', 'pages/demo/provider.js', 'pages/demo/consumer-search.js'];
    for (const screen of screens) {
        const source = readFileSync(new URL('../src/' + screen, import.meta.url), 'utf8');
        assert.doesNotMatch(source, /MDC Demo Console|Demo Admin|demo role|local vocabulary|Stage 1B demo|MDC Preview|Request payload preview|Advanced\/debug|Backend error details|Match score/i, screen);
        if (consumer.includes(screen)) assert.doesNotMatch(source, /<pre\b|SearchPayloadPreview|JSON\.stringify/, screen);
    }
});
