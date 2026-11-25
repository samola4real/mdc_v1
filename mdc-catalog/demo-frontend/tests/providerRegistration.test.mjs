import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import {
    buildRegistrationPayload, emptyRegistrationForm, hasRegistrationDraft, measurementFields,
    registrationPartRanges, selectRegistrationFamily
} from '../src/components/mdc/providerRegistrationPayload.js';
import {
    createRegistrationRequestGuard, invalidateRegistrationValidation, isCurrentRegistrationValidation,
    readBackRegistration, registrationPayloadKey, registrationRetryBlocked, submitRegistration, validateRegistration
} from '../src/components/mdc/providerRegistrationFlow.js';
import { buildOfferingCreation, buildProviderPatches, emptyProviderForm, hydrateProviderForm } from '../src/components/mdc/providerPayloadBuilder.js';
import { isDisposableMdcId } from '../src/services/mdc/stage1bScope.js';

const options = (...items) => items.map((value) => ({ label: value, value }));
const filters = {
    partFamilies: options('gear', 'shaft', 'metal_part'),
    partTypes: { gear: options('spur_gear', 'helical_gear'), shaft: options('plain_shaft', 'splined_shaft'),
        metal_part: options('block', 'plate', 'roller') },
    serviceCategoryByFamily: { gear: 'precision_gears', shaft: 'precision_shafts', metal_part: 'precision_metal_parts' },
    certifications: [{ label: 'ISO 9001:2015', value: 'ISO9001_2015' }],
    materials: options('steel', 'aluminum'),
    processes: options('machining', 'hobbing')
};
const providerId = 'mdc_stage1b_registration_test';
const offeringId = providerId + '_offering';
const draft = (partFamily = 'metal_part') => ({
    ...emptyRegistrationForm(), providerId, offeringId, providerName: 'Test company', country: 'Finland',
    offeringName: 'Test offering', partFamily
});
const build = (form) => buildRegistrationPayload(form, filters);
const offering = (form) => build(form).payload.offerings[0];
const row = (id, name, fields = {}) => ({ id, name, ...fields });
const validFor = (payload) => ({ kind: 'valid', payloadKey: registrationPayloadKey(payload) });

test('blank registration has no seeded selections and shows only the contractual required gates', () => {
    const blank = emptyRegistrationForm();
    assert.equal(hasRegistrationDraft(blank), false);
    assert.equal(hasRegistrationDraft({ ...blank, otherCertifications: [{ id: 1 }] }), false);
    assert.equal(hasRegistrationDraft({ ...blank, providerName: 'Unsaved' }), true);
    assert.equal(Object.hasOwn(blank, 'supportStatus'), false);
    assert.deepEqual(blank.partTypes, []);
    assert.deepEqual(blank.materials, []);
    const { errors } = build(blank);
    assert.deepEqual(Object.keys(errors).sort(), ['country', 'offeringId', 'offeringName', 'partFamily', 'providerId', 'providerName']);
    assert.deepEqual(build(draft()).errors, {});
    assert.match(build({ ...draft(), offeringId: 'mdc_stage1b_another_id' }).errors.offeringId, /complete provider ID/);
});

test('family changes derive categories, confirm before discard and retain shared capabilities', () => {
    const gear = { ...draft('gear'), partTypes: ['spur_gear', 'helical_gear'],
        familyDetails: { moduleMin: 1.5, moduleMax: 3, diameterMaxMm: 200, qualityStandard: 'ISO', qualityClass: '6' },
        materials: ['steel'], materialGrades: { steel: '42CrMo4' }, processes: ['machining'], general: { batchSizeMin: 100 } };
    assert.equal(offering(gear).service_category, 'precision_gears');
    assert.equal(offering(gear).family_capabilities.gear_quality.best_class, 6);
    assert.strictEqual(selectRegistrationFamily(gear, 'shaft', () => false), gear);
    const shaft = selectRegistrationFamily(gear, 'shaft', () => true);
    assert.equal(offering(shaft).service_category, 'precision_shafts');
    assert.deepEqual(shaft.partTypes, []);
    assert.deepEqual(shaft.familyDetails, {});
    assert.deepEqual(shaft.materialGrades, gear.materialGrades);
    assert.deepEqual(shaft.general, gear.general);
    const metal = selectRegistrationFamily(shaft, 'metal_part', () => assert.fail('empty family form'));
    assert.equal(offering(metal).service_category, 'precision_metal_parts');
    const previousMetal = { ...metal, partTypes: ['block'], familyDetails: { tolerance: '0.1 mm', surfaceFinish: 'Ra 1.6' },
        partMeasurements: { block: { maxLengthMm: 80 } } };
    const backToGear = selectRegistrationFamily(previousMetal, 'gear', () => true);
    assert.deepEqual(backToGear.partMeasurements, {});
    assert.deepEqual(offering(backToGear).custom_capability_fields, {});
});

test('block plus roller and block plus plate keep independent dimensions through removal and reselection', () => {
    const form = {
        ...draft(), partTypes: ['block', 'roller'],
        partMeasurements: {
            block: { maxLengthMm: 80, maxWidthMm: 40, maxHeightMm: 15 },
            plate: { maxLengthMm: 120 }, roller: { maxDiameterMm: 70 }
        }
    };
    const initial = offering(form).part_type_capabilities;
    assert.equal(initial.block.bounding_box_mm.length_mm.max, 80);
    assert.equal(initial.block.bounding_box_mm.width_mm.max, 40);
    assert.equal(initial.block.bounding_box_mm.height_mm.max, 15);
    assert.equal(initial.roller.outer_diameter_mm.max, 70);
    assert.deepEqual(Object.keys(offering({ ...form, partTypes: ['roller'] }).part_type_capabilities), ['roller']);
    const boxPair = offering({ ...form, partTypes: ['block', 'plate'] }).part_type_capabilities;
    assert.equal(boxPair.block.bounding_box_mm.length_mm.max, 80);
    assert.equal(boxPair.plate.bounding_box_mm.length_mm.max, 120);
    assert.deepEqual(offering(form).part_type_capabilities, initial);
    assert.equal(measurementFields(registrationPartRanges('metal_part', 'block')).length, 3);
    assert.equal(measurementFields(registrationPartRanges('metal_part', 'roller')).length, 1);
});

test('selected spline measurements retain their draft and new support is always declared confirmed', () => {
    const initial = {
        ...draft('shaft'), partTypes: ['plain_shaft', 'splined_shaft'],
        familyDetails: { lengthMaxMm: 300, outerDiameterMinMm: 12, outerDiameterMaxMm: 50 },
        partMeasurements: { splined_shaft: { splineModule: 2 } }
    };
    assert.equal(offering(initial).family_capabilities.length_mm.max, 300);
    assert.equal(offering(initial).part_type_capabilities.splined_shaft.spline_module.value, 2);
    const withoutSpline = { ...initial, partTypes: ['plain_shaft'] };
    assert.deepEqual(offering(withoutSpline).part_type_capabilities, {});
    assert.equal(offering({ ...withoutSpline, partTypes: initial.partTypes }).part_type_capabilities.splined_shaft.spline_module.value, 2);
    for (const supportStatus of [undefined, 'candidate_requiring_confirmation', 'unknown']) {
        const { payload, errors } = build({ ...initial, supportStatus });
        const [result] = payload.offerings;
        assert.deepEqual(errors, {});
        assert.equal(result.support_status, 'confirmed');
        assert.deepEqual(result.supported_part_types, initial.partTypes.map((part_type) => ({
            part_type, support_status: 'confirmed', source_type: 'provider_confirmed', confidence: 'declared'
        })));
        assert.equal(result.part_type_capabilities.splined_shaft.spline_module.value, 2);
    }
});

test('technical text is optional for each family and gear quality keeps its canonical representation', () => {
    for (const family of ['gear', 'shaft', 'metal_part']) {
        const fit = family === 'shaft' ? 'h6' : 'H7';
        const form = { ...draft(family), familyDetails: {
            tolerance: ' 0.05 mm ', surfaceFinish: ' Ra 1.6 µm ',
            qualityToleranceStandard: ' ISO 286 ', toleranceClassFit: ' ' + fit + ' ',
            ...(family === 'gear' && { qualityStandard: 'ISO', qualityClass: '6' })
        } };
        const { payload, errors } = build(form);
        const [result] = payload.offerings;
        assert.deepEqual(errors, {}, family);
        assert.deepEqual(result.custom_capability_fields, {
            tolerance: '0.05 mm', surface_finish: 'Ra 1.6 µm',
            ...(family !== 'gear' && { quality_tolerance_standard: 'ISO 286', tolerance_class_fit: fit })
        }, family);
        assert.deepEqual(result.family_capabilities.gear_quality, family === 'gear' ? {
            source_type: 'provider_confirmed', confidence: 'declared', standard: 'ISO', best_class: 6
        } : undefined, family);
        const blank = build({ ...form, familyDetails: {
            tolerance: ' ', surfaceFinish: ' ', qualityToleranceStandard: '\t', toleranceClassFit: ' '
        } });
        assert.deepEqual(blank.errors, {}, family);
        assert.deepEqual(blank.payload.offerings[0].custom_capability_fields, {}, family);
    }
});

test('part selections retain fit specifications and family changes clear them only after confirmation', () => {
    const fitDetails = { qualityToleranceStandard: 'ISO 286', toleranceClassFit: 'h6' };
    const shaft = { ...draft('shaft'), familyDetails: fitDetails };
    assert.deepEqual(offering({ ...shaft, partTypes: ['plain_shaft', 'splined_shaft'] }).custom_capability_fields,
        offering(shaft).custom_capability_fields);
    assert.strictEqual(selectRegistrationFamily(shaft, 'metal_part', () => false), shaft);
    const metal = selectRegistrationFamily(shaft, 'metal_part', () => true);
    assert.deepEqual(offering(metal).custom_capability_fields, {});
    const metalWithFit = { ...metal, familyDetails: { ...fitDetails, toleranceClassFit: 'H7' } };
    assert.strictEqual(selectRegistrationFamily(metalWithFit, 'gear', () => false), metalWithFit);
    const gear = selectRegistrationFamily(metalWithFit, 'gear', () => true);
    assert.deepEqual(offering(gear).custom_capability_fields, {});
    assert.deepEqual(offering(selectRegistrationFamily(gear, 'shaft', () => true)).custom_capability_fields, {});
});

test('generic technical fields cannot use reserved keys or the technical control labels', () => {
    const names = ['Tolerance', 'Surface finish', 'QUALITY_TOLERANCE_STANDARD', 'Tolerance class / fit',
        'Quality / tolerance standard', 'tolerance_class_fit'];
    const { payload, errors } = build({ ...draft('shaft'), familyDetails: {
        tolerance: '0.05 mm', surfaceFinish: 'Ra 1.6 µm', qualityToleranceStandard: 'ISO 286', toleranceClassFit: 'h6'
    }, customCapabilityFields: names.map((name, index) => row(index + 1, name, { value: 'Collision' })) });
    for (const [index] of names.entries()) assert.match(errors['customCapabilityFields.' + (index + 1) + '.name'], /reserved keys/);
    assert.deepEqual(payload.offerings[0].custom_capability_fields, {
        tolerance: '0.05 mm', surface_finish: 'Ra 1.6 µm', quality_tolerance_standard: 'ISO 286', tolerance_class_fit: 'h6'
    });
});

test('independent controlled grades and structured extension maps preserve free text', () => {
    const form = {
        ...draft(), description: 'Provider description', certifications: ['ISO9001_2015'],
        otherCertifications: [row(1, 'Certificate A'), row(2, 'Certificate B')],
        productionMode: 'Repeat orders', industriesServed: 'Engineering, design\nTransport\nTransport',
        otherServiceInformation: 'Quotation on request',
        customOfferingFields: [row(1, 'Reference', { value: 'QUOTE 1' })],
        materials: ['steel', 'aluminum'], materialGrades: { steel: '42CrMo4, 42CrMo4', aluminum: '6061' },
        additionalMaterials: [row(1, 'Independent alloy', { grades: 'Variant A, Variant B' })],
        processes: ['machining'], additionalProcesses: [row(1, 'Specialist finishing')],
        capabilityNotes: 'Offering-level note',
        customCapabilityFields: [row(1, 'Inspection detail', { value: 'On request', unit: 'per lot', notes: 'Ask provider' })]
    };
    const { payload, errors } = build(form);
    const [result] = payload.offerings;
    assert.deepEqual(errors, {});
    assert.deepEqual(payload.custom_provider_fields, {
        description: 'Provider description', additional_certifications: ['Certificate A', 'Certificate B']
    });
    assert.deepEqual(result.custom_offering_fields, {
        Reference: 'QUOTE 1', production_mode: 'Repeat orders', industries_served: ['Engineering, design', 'Transport'],
        other_service_information: 'Quotation on request'
    });
    assert.deepEqual(result.custom_capability_fields, {
        notes: 'Offering-level note', 'Inspection detail': { value: 'On request', unit: 'per lot', notes: 'Ask provider' },
        additional_materials: [{ name: 'Independent alloy', available_grades: ['Variant A', 'Variant B'] }],
        additional_processes: ['Specialist finishing']
    });
    const materialGrades = (value) => offering(value).generic_capabilities.materials.map(({ material, available_grades }) => [material, available_grades]);
    assert.deepEqual(materialGrades(form), [['steel', ['42CrMo4']], ['aluminum', ['6061']]]);
    assert.deepEqual(materialGrades({ ...form, materials: ['steel'] }), [['steel', ['42CrMo4']]]);
    assert.deepEqual(materialGrades({ ...form, materials: ['aluminum', 'steel'] }), [['aluminum', ['6061']], ['steel', ['42CrMo4']]]);
    assert.equal(result.generic_capabilities.processes[0].delivery_mode, 'unspecified');
});

test('duplicate, reserved and incomplete extensions and invalid measurements require field correction', () => {
    const form = {
        ...draft('gear'), familyDetails: { moduleMin: 5, moduleMax: 2, qualityClass: 'Infinity' },
        general: { weightMaxKg: 0 }, otherCertifications: [row(1, 'Certificate'), row(2, ' certificate '), row(3, 'ISO 9001:2015')],
        additionalMaterials: [row(1, '', { grades: 'Test grade' })],
        otherServiceInformation: 'Optional',
        customOfferingFields: [row(1, 'Production mode', { value: 'Repeat' }), row(2, 'Duplicate', { value: 'One' }),
            row(3, 'duplicate', { value: 'Two' }), row(4, 'Missing value')],
        customCapabilityFields: [row(1, 'Additional materials', { value: 'Collision' }), row(2, 'notes', { value: 'Collision' })],
        additionalProcesses: [row(1, 'Machining')]
    };
    const { payload, errors } = build(form);
    for (const field of ['familyDetails.moduleMin', 'familyDetails.qualityClass', 'general.weightMaxKg', 'otherCertifications.2.name',
        'otherCertifications.3.name', 'additionalMaterials.1.name', 'customOfferingFields.1.name', 'customOfferingFields.3.name',
        'customOfferingFields.4.value', 'customCapabilityFields.1.name', 'customCapabilityFields.2.name', 'additionalProcesses.1.name']) {
        assert.ok(errors[field], field);
    }
    assert.equal(payload.offerings[0].custom_offering_fields.Duplicate, 'One');
    assert.equal(payload.offerings[0].custom_offering_fields.duplicate, undefined);
    assert.equal(offering({ ...draft('gear'), familyDetails: { qualityClass: 'AGMA class description' } }).custom_capability_fields.quality_class,
        'AGMA class description');
});

test('validation is explicit, maps domain messages, redacts private details and stays stale after reverting an edit', async () => {
    const original = build(draft()).payload;
    const invalid = await validateRegistration(original, async () => ({ valid: false, errors: { provider_name: ['Enter a name'] } }));
    assert.equal(invalid.kind, 'invalid');
    assert.equal(invalid.errors.providerName, 'Enter a name');
    assert.equal((await validateRegistration(original, async () => ({ valid: 1 }))).kind, 'invalid');
    assert.equal((await validateRegistration(original, async () => ({ status: 'completed' }))).kind, 'invalid');
    const range = 'offerings[0].generic_capabilities.batch_size.min must be less than or equal to max.';
    const bad = await validateRegistration(original, async () => { throw {
        status: 400, message: 'Invalid publication', details: { non_field_errors: [range], token: 'sample-token', stack: 'sample-stack' }
    } });
    assert.equal(bad.errors['general.batchSizeMin'], range);
    assert.equal(Object.hasOwn(bad.details, 'token'), false);
    assert.equal(Object.hasOwn(bad.details, 'stack'), false);
    const good = await validateRegistration(original, async () => ({ valid: true, normalized_payload: {} }));
    assert.equal(isCurrentRegistrationValidation(good, registrationPayloadKey(original)), true);
    const changed = build({ ...draft(), providerName: 'Edited' }).payload;
    const stale = invalidateRegistrationValidation(good, registrationPayloadKey(changed));
    assert.equal(stale.kind, 'stale');
    assert.equal(isCurrentRegistrationValidation(invalidateRegistrationValidation(stale, registrationPayloadKey(original)),
        registrationPayloadKey(original)), false);
});

test('fit specification edits invalidate validation and server details map to both inputs', async () => {
    for (const family of ['shaft', 'metal_part']) {
        const form = { ...draft(family), familyDetails: { qualityToleranceStandard: 'ISO 286', toleranceClassFit: 'H7' } };
        const { payload } = build(form);
        const validation = await validateRegistration(payload, async () => ({ valid: true }));
        for (const field of ['qualityToleranceStandard', 'toleranceClassFit']) {
            const changed = build({ ...form, familyDetails: { ...form.familyDetails, [field]: '' } }).payload;
            assert.equal(invalidateRegistrationValidation(validation, registrationPayloadKey(changed)).kind, 'stale');
        }
        const invalid = await validateRegistration(payload, async () => ({ valid: false, errors: {
            'offerings[0].custom_capability_fields.quality_tolerance_standard': ['Check the standard'],
            'offerings[0].custom_capability_fields.tolerance_class_fit': ['Check the fit']
        } }));
        assert.deepEqual(invalid.errors, {
            'familyDetails.qualityToleranceStandard': 'Check the standard', 'familyDetails.toleranceClassFit': 'Check the fit'
        });
    }
});

const receipt = (data = {}) => ({ status: 201, data: {
    contract_version: '1.0', operation: 'create', status: 'accepted', provider_id: providerId, offering_ids: [offeringId],
    publication_id: 'test-receipt', publication_status: 'sync_pending', sync_status: 'pending', ...data
} });
const reads = {
    getProvider: async (id) => ({ data: { provider_id: id }, etag: '"provider"' }),
    listProviderOfferings: async (id) => ({ provider_id: id, offerings: [{ offering_id: offeringId }] }),
    getOffering: async (id) => ({ data: { provider_id: providerId, offering_id: id }, etag: '"offering"' })
};

test('registration requires the exact validated payload and accepts only the matching receipt', async () => {
    const payload = build({ ...draft(), otherCertifications: [row(1, 'Test extension')] }).payload;
    const validation = await validateRegistration(payload, async () => ({ valid: true, normalized_payload: { provider: {} } }));
    const sent = [];
    const services = { ...reads, registerProvider: async (wire) => { sent.push(wire); return receipt(); } };
    assert.equal((await submitRegistration({ ...payload, country: 'Sweden' }, validation, services)).kind, 'unvalidated');
    assert.equal(sent.length, 0);
    const result = await submitRegistration(payload, validation, services);
    assert.equal(result.kind, 'accepted');
    assert.equal(result.receipt.publicationId, 'test-receipt');
    assert.equal(result.receipt.syncStatus, 'pending');
    assert.equal(result.readBack.kind, 'matching');
    assert.deepEqual(sent, [payload]);
    const completed = await submitRegistration(payload, validation, {
        ...reads, registerProvider: async () => receipt({ status: 'completed', publication_status: 'synced', sync_status: 'succeeded' })
    });
    assert.equal(completed.kind, 'accepted');
    assert.equal(completed.receipt.syncStatus, 'succeeded');
    const wrong = await submitRegistration(payload, validation, {
        ...reads, registerProvider: async () => receipt({ offering_ids: ['other'] })
    });
    assert.equal(wrong.kind, 'uncertain');
});

test('accepted read-back never selects a different offering and keeps the receipt when reads fail', async () => {
    const payload = build(draft()).payload;
    const result = await submitRegistration(payload, validFor(payload), {
        ...reads, registerProvider: async () => receipt(),
        listProviderOfferings: async () => ({ provider_id: providerId, offerings: [{ offering_id: 'other' }] }),
        getOffering: async () => assert.fail('read-back selected the wrong offering')
    });
    assert.equal(result.kind, 'accepted');
    assert.equal(result.readBack.kind, 'providerOnly');
    assert.equal(result.readBack.snapshot, undefined);
    assert.equal(result.receipt.publicationId, 'test-receipt');
});

test('duplicate rejection preserves identity and uncertain responses use read-only reconciliation', async () => {
    const payload = build(draft()).payload;
    const validation = validFor(payload);
    const duplicate = await submitRegistration(payload, validation, {
        registerProvider: async () => { throw { status: 409, code: 'provider_already_exists' }; },
        getProvider: async () => assert.fail('definite rejection should not read back')
    });
    assert.equal(duplicate.kind, 'rejected');
    assert.equal(registrationRetryBlocked(duplicate, payload), true);
    assert.equal(registrationRetryBlocked(duplicate, { ...payload, provider_id: 'mdc_stage1b_different' }), false);
    let posts = 0;
    const postCommit = await submitRegistration(payload, validation, {
        ...reads, registerProvider: async () => { posts++; throw { status: 503, publicationId: 'pending-receipt' }; }
    });
    assert.equal(postCommit.kind, 'uncertain');
    assert.equal(postCommit.readBack.kind, 'matching');
    assert.equal(postCommit.receipt.publicationId, 'pending-receipt');
    assert.equal(posts, 1);
    assert.equal(registrationRetryBlocked(postCommit, payload), true);
    const absent = await submitRegistration(payload, validation, {
        registerProvider: async () => { posts++; throw { status: null }; },
        getProvider: async () => { throw { status: 404, code: 'not_found' }; }
    });
    assert.equal(absent.readBack.kind, 'absent');
    assert.equal(registrationRetryBlocked(absent, payload), false);
    assert.equal(posts, 2);
    const unknown = await readBackRegistration({ providerId, offeringId }, {
        getProvider: async () => { throw { status: 404, code: 'mdc_route_not_found' }; }
    });
    assert.equal(unknown.kind, 'unknown');
});

test('the request guard suppresses concurrent submissions and releases after completion or failure', async () => {
    const once = createRegistrationRequestGuard();
    let resolveFirst;
    const pending = once(() => new Promise((resolve) => { resolveFirst = resolve; }));
    await once(() => assert.fail('duplicate submission'));
    resolveFirst('done');
    assert.equal(await pending, 'done');
    await assert.rejects(once(async () => { throw new Error('failure'); }), /failure/);
    assert.equal(await once(async () => 'next'), 'next');
});

test('legacy update and add preserve opaque extensions and retain the baseline read-only guard', () => {
    const { payload } = build({
        ...draft(), otherCertifications: [row(1, 'Test certificate')],
        familyDetails: { tolerance: '0.05 mm', qualityToleranceStandard: 'ISO 286', toleranceClassFit: 'H7' },
        materials: ['steel', 'aluminum'], materialGrades: { steel: '42CrMo4', aluminum: '6061' },
        additionalMaterials: [row(1, 'Other alloy', { grades: 'Other grade' })],
        industriesServed: 'Manufacturing'
    });
    const provider = {
        provider_id: payload.provider_id, provider_name: payload.provider_name, country: payload.country,
        certifications: payload.certifications, custom_provider_fields: payload.custom_provider_fields
    };
    const [savedOffering] = payload.offerings;
    const restored = hydrateProviderForm(provider, savedOffering);
    assert.deepEqual(buildProviderPatches(restored, provider, savedOffering), { provider: {}, offering: {} });
    const patches = buildProviderPatches({ ...restored, description: 'Added notes', batchSizeMin: 10 }, provider, savedOffering);
    assert.deepEqual(patches.provider.custom_provider_fields.additional_certifications, ['Test certificate']);
    assert.deepEqual(patches.offering.generic_capabilities.materials, savedOffering.generic_capabilities.materials);
    assert.equal(patches.offering.custom_capability_fields, undefined);
    assert.equal(patches.offering.custom_offering_fields, undefined);
    const tolerancePatch = buildProviderPatches({ ...restored, tolerance: '0.08 mm' }, provider, savedOffering).offering;
    assert.deepEqual(tolerancePatch.custom_capability_fields, {
        ...savedOffering.custom_capability_fields, tolerance: '0.08 mm'
    });
    const add = buildOfferingCreation({
        ...emptyProviderForm(), providerId, offeringId, offeringName: 'Legacy add',
        serviceCategory: 'precision_gears', partFamily: 'gear', partTypes: ['spur_gear'],
        materials: ['steel'], availableGrades: '42CrMo4', supportStatus: 'candidate_requiring_confirmation'
    });
    assert.equal(add.generic_capabilities.materials[0].available_grades[0], '42CrMo4');
    assert.equal(add.offering_id, offeringId);
    assert.equal(add.support_status, 'candidate_requiring_confirmation');
    assert.equal(add.supported_part_types[0].support_status, 'candidate_requiring_confirmation');
    assert.equal(isDisposableMdcId('tasowheel'), false);
    assert.equal(isDisposableMdcId('precipart'), false);
});

test('registration and the shared Update/Add view do not mount the advanced payload panel', () => {
    for (const component of ['ProviderRegistration', 'ProviderDemoPanel']) {
        const source = readFileSync(new URL('../src/components/mdc/' + component + '.js', import.meta.url), 'utf8');
        assert.doesNotMatch(source, /ProviderPayloadPreview|Advanced \/ payload preview/);
    }
});
