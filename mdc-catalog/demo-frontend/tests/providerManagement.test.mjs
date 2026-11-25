import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import {
    buildAddedOffering, buildOfferingEdit, buildProviderEdit, catalogueLabel, editorDirty, offeringEditor,
    providerEditor, retainedPartDraft
} from '../src/components/mdc/providerManagementDraft.js';
import {
    acceptParentRevision, executeManagementWrite, loadManagementSnapshot, observeManagementTarget, observedWrite,
    strongEtag, writeRecovery
} from '../src/components/mdc/providerManagementFlow.js';
import { emptyRegistrationForm } from '../src/components/mdc/providerRegistrationPayload.js';

const providerId = 'mdc_stage1b_manage_fixture';
const offeringId = providerId + '_roller';
const alternateId = providerId + '_alternate';
const family = 'metal_part';
const options = (...items) => items.map(([value, label]) => ({ value, label }));
const filters = {
    partFamilies: options(['metal_part', 'Metal part'], ['gear', 'Gear'], ['shaft', 'Shaft']),
    serviceCategories: options(['precision_metal_parts', 'Precision metal parts']),
    serviceCategoryByFamily: { metal_part: 'precision_metal_parts', gear: 'precision_gears', shaft: 'precision_shafts' },
    partTypes: { metal_part: options(['block', 'Block'], ['roller', 'Roller'], ['plate', 'Plate']), gear: [], shaft: [] },
    certifications: options(['ISO9001_2015', 'ISO 9001:2015'], ['ISO14001_2015', 'ISO 14001:2015']),
    materials: options(['steel', 'Steel'], ['aluminum', 'Aluminum']),
    processes: options(['milling', 'Milling'], ['turning', 'Turning'])
};
const evidence = { source_type: 'provider_confirmed', confidence: 'declared' };
const source = { ...evidence, source_note: 'Fixture source' };
const part = (part_type, support_status = 'confirmed') => ({ part_type, support_status, ...source });
const provider = () => ({
    provider_id: providerId, provider_name: 'Example provider', country: 'Finland', status: 'draft',
    certifications: [{ code: 'ISO9001_2015', ...source }],
    publication_metadata: { ...evidence, fixture: 'retain' },
    custom_provider_fields: { description: 'Example description', additional_certifications: ['Fixture certification'], opaque: { version: 3 } },
    offerings: [{ offering_id: offeringId }]
});
const offering = () => ({
    offering_id: offeringId, provider_id: providerId, offering_name: 'Example metal offering', service_category: 'precision_metal_parts',
    part_family: family, support_status: 'confirmed', is_active: true,
    supported_part_types: [part('block'), part('roller'), part('plate', 'candidate_requiring_confirmation')],
    family_capabilities: {},
    part_type_capabilities: {
        block: { bounding_box_mm: { length_mm: { min: 12, max: 80, ...source }, width_mm: { max: 40, ...evidence } } },
        roller: { outer_diameter_mm: { max: 65, ...source } }
    },
    generic_capabilities: {
        materials: [
            { material: 'steel', available_grades: ['42CrMo4, normalized', 'S355', 'S355'], ...source },
            { material: 'aluminum', available_grades: ['6061'], ...source }
        ],
        processes: [{ process: 'milling', delivery_mode: 'in_house', ...evidence }],
        lead_time_weeks: { min: 2, max: 6, ...source },
        surface_finish_ra_um: { max: 3.2, ...source }
    },
    custom_offering_fields: {
        production_mode: 'Repeat', industries_served: ['Engineering, design'], other_service_information: 'Contact first',
        Reference: 'X1', OpaqueService: { value: false, revision: 2 }
    },
    custom_capability_fields: {
        tolerance: '0.05 mm', surface_finish: 'Ra 1.6 µm', quality_tolerance_standard: 'ISO 286', tolerance_class_fit: 'H7',
        additional_materials: [{ name: 'Fixture alloy', available_grades: ['Variant A, heat treated'], retained: 'source' }],
        additional_processes: ['Fixture process'], notes: 'Fixture notes',
        Inspection: { value: 'First lot', unit: 'per lot', notes: 'Ask', internal: { fixture: 'preserve' } },
        OpaqueTechnical: [1, 2]
    }
});
const resource = (data, etag = '"old-revision"') => ({ data, etag });
const edit = (editor, changes) => ({ ...editor, draft: { ...editor.draft, ...changes } });

test('saved Task 08 shapes hydrate with no initial edits and catalogue labels are human-readable', () => {
    const company = providerEditor(resource(provider()));
    const offer = offeringEditor(resource(offering()));
    assert.equal(company.draft.description, 'Example description');
    assert.deepEqual(company.draft.otherCertifications.map(({ name }) => name), ['Fixture certification']);
    assert.equal(offer.draft.serviceCategory, 'precision_metal_parts');
    assert.equal(catalogueLabel(filters.serviceCategories, offer.draft.serviceCategory), 'Precision metal parts');
    assert.equal(catalogueLabel([], 'saved_code'), 'Saved code');
    assert.equal(offer.draft.partTypeStatuses.plate, 'candidate_requiring_confirmation');
    assert.equal(offer.draft.partMeasurements.block.maxLengthMm, 80);
    assert.equal(offer.draft.partMeasurements.roller.maxDiameterMm, 65);
    assert.equal(offer.draft.materialGrades.steel, '42CrMo4, normalized\nS355\nS355');
    assert.equal(offer.draft.materialGrades.aluminum, '6061');
    assert.equal(offer.draft.additionalMaterials[0].grades, 'Variant A, heat treated');
    assert.equal(offer.draft.industriesServed, 'Engineering, design');
    assert.deepEqual(offer.draft.familyDetails, {
        tolerance: '0.05 mm', surfaceFinish: 'Ra 1.6 µm', qualityToleranceStandard: 'ISO 286', toleranceClassFit: 'H7'
    });
    assert.deepEqual(offer.draft.savedSpecifications, [{ label: 'Saved numeric surface finish', value: 'max 3.2 µm Ra' }]);
    assert.equal(editorDirty(company), false);
    assert.equal(editorDirty(offer), false);
    assert.deepEqual(buildProviderEdit(company, filters), { patch: {}, errors: {} });
    assert.deepEqual(buildOfferingEdit(offer, filters), { patch: {}, errors: {} });
});

test('provider and offering patches exclude immutable fields and preserve untouched records and metadata', () => {
    const company = provider();
    const providerPatch = buildProviderEdit(edit(providerEditor(resource(company)), {
        providerName: 'Improved name', providerId: 'other', description: 'Updated description',
        certifications: ['ISO9001_2015', 'ISO14001_2015']
    }), filters);
    assert.deepEqual(providerPatch, { errors: {}, patch: {
        provider_name: 'Improved name', certifications: [...company.certifications, { code: 'ISO14001_2015', ...evidence }],
        custom_provider_fields: { ...company.custom_provider_fields, description: 'Updated description' }
    } });

    const saved = offering();
    const editor = offeringEditor(resource(saved));
    const draft = edit(editor, {
        offeringId: alternateId, partFamily: 'gear', serviceCategory: 'precision_gears', offeringName: 'Improved offering',
        supportStatus: 'unknown', partMeasurements: { ...editor.draft.partMeasurements, block: { ...editor.draft.partMeasurements.block, maxLengthMm: 105 } },
        materialGrades: { ...editor.draft.materialGrades, steel: editor.draft.materialGrades.steel + '\nA36' },
        processes: [...editor.draft.processes, 'turning']
    });
    const { patch, errors } = buildOfferingEdit(draft, filters);
    assert.deepEqual(errors, {});
    assert.deepEqual(Object.keys(patch).sort(), ['generic_capabilities', 'offering_name', 'part_type_capabilities', 'support_status']);
    assert.deepEqual(patch.part_type_capabilities.block.bounding_box_mm.length_mm, { min: 12, max: 105, ...source });
    assert.deepEqual(patch.part_type_capabilities.roller, saved.part_type_capabilities.roller);
    assert.deepEqual(patch.generic_capabilities.materials[0], {
        ...saved.generic_capabilities.materials[0], available_grades: ['42CrMo4, normalized', 'S355', 'S355', 'A36']
    });
    assert.deepEqual(patch.generic_capabilities.materials[1], saved.generic_capabilities.materials[1]);
    assert.deepEqual(patch.generic_capabilities.processes, [
        saved.generic_capabilities.processes[0], { process: 'turning', delivery_mode: 'unspecified', ...evidence }
    ]);
    assert.deepEqual(patch.generic_capabilities.surface_finish_ra_um, saved.generic_capabilities.surface_finish_ra_um);
});

test('type and material removal changes only selected records and reselection restores their own draft', () => {
    const saved = offering();
    const editor = offeringEditor(resource(saved));
    const form = retainedPartDraft(editor.draft, ['roller', 'plate']);
    const omitted = { ...form, materials: ['aluminum'] };
    const removed = buildOfferingEdit({ ...editor, draft: omitted }, filters).patch;
    assert.deepEqual(removed.supported_part_types, [part('roller'), part('plate', 'candidate_requiring_confirmation')]);
    assert.deepEqual(removed.part_type_capabilities, { roller: saved.part_type_capabilities.roller });
    assert.deepEqual(removed.generic_capabilities.materials, [saved.generic_capabilities.materials[1]]);
    const restored = retainedPartDraft({ ...omitted, materials: ['aluminum', 'steel'] }, ['roller', 'plate', 'block']);
    assert.deepEqual(restored.partTypes, editor.initial.partTypes);
    assert.deepEqual(buildOfferingEdit({ ...editor, draft: restored }, filters).patch, {});
    const newType = retainedPartDraft({ ...restored, partTypeStatuses: {}, supportStatus: 'unknown' }, ['roller']);
    assert.equal(newType.partTypeStatuses.roller, 'unknown');
    assert.equal(retainedPartDraft({ ...newType, supportStatus: 'confirmed' }, ['roller']).partTypeStatuses.roller, 'unknown');
});

test('changing one type status leaves other evidence and dimensions in place', () => {
    const saved = offering();
    const editor = offeringEditor(resource(saved));
    const draft = { ...editor.draft, partTypeStatuses: { ...editor.draft.partTypeStatuses, block: 'unknown' } };
    const { patch } = buildOfferingEdit({ ...editor, draft }, filters);
    assert.deepEqual(patch.supported_part_types, [part('block', 'unknown'), part('roller'), part('plate', 'candidate_requiring_confirmation')]);
    assert.deepEqual(patch.part_type_capabilities, { roller: saved.part_type_capabilities.roller });
    assert.equal(patch.support_status, undefined);
    assert.deepEqual(buildOfferingEdit(edit(editor, { partTypeStatuses: editor.initial.partTypeStatuses }), filters).patch, {});
});

test('duplicate saved material records remain separate when editing a different material', () => {
    const saved = offering();
    const secondSteel = { material: 'steel', available_grades: ['EN8'], ...evidence, source_note: 'A second source' };
    saved.generic_capabilities.materials.push(secondSteel);
    const editor = offeringEditor(resource(saved));
    assert.deepEqual(editor.draft.materials, ['steel', 'aluminum']);
    assert.match(editor.locked['materialGrades.steel'], /multiple saved records/);
    const { patch, errors } = buildOfferingEdit(edit(editor, {
        materialGrades: { ...editor.draft.materialGrades, aluminum: '6061\n7075' }
    }), filters);
    assert.deepEqual(errors, {});
    assert.deepEqual(patch.generic_capabilities.materials, [
        saved.generic_capabilities.materials[0],
        { ...saved.generic_capabilities.materials[1], available_grades: ['6061', '7075'] },
        secondSteel
    ]);
});

test('named extension edits preserve opaque keys and custom row metadata and detect collisions', () => {
    const saved = offering();
    const editor = offeringEditor(resource(saved));
    const { draft } = editor;
    const { patch, errors } = buildOfferingEdit(edit(editor, {
        customOfferingFields: [{ ...draft.customOfferingFields[0], value: 'X2' }],
        customCapabilityFields: [{ ...draft.customCapabilityFields[0], value: 'Every lot', notes: '' }],
        additionalMaterials: [{ ...draft.additionalMaterials[0], grades: 'Variant A, heat treated\nVariant B' }],
        familyDetails: { ...draft.familyDetails, toleranceClassFit: 'H8' }
    }), filters);
    assert.deepEqual(errors, {});
    assert.deepEqual(patch.custom_offering_fields, { ...saved.custom_offering_fields, Reference: 'X2' });
    assert.deepEqual(patch.custom_capability_fields, { ...saved.custom_capability_fields, tolerance_class_fit: 'H8',
        additional_materials: [{ ...saved.custom_capability_fields.additional_materials[0],
            available_grades: ['Variant A, heat treated', 'Variant B'] }],
        Inspection: { value: 'Every lot', unit: 'per lot', internal: { fixture: 'preserve' } }
    });
    const collisions = buildOfferingEdit(edit(editor, { customCapabilityFields: [
        ...draft.customCapabilityFields,
        { id: 1, name: 'opaqueTechnical', value: 'bad' },
        { id: 2, name: 'Quality / tolerance standard', value: 'bad' },
        { id: 3, name: ' inspection ', value: 'bad' }
    ] }), filters);
    for (const id of [1, 2, 3]) assert.ok(collisions.errors['customCapabilityFields.' + id + '.name']);
    assert.equal(collisions.patch.custom_capability_fields, undefined);
});

test('unsupported saved formats are locked and numeric updates check hidden minimums', () => {
    const saved = offering();
    saved.custom_capability_fields.tolerance = { original: true };
    const editor = offeringEditor(resource(saved));
    assert.match(editor.locked['familyDetails.tolerance'], /preserved/);
    assert.deepEqual(buildOfferingEdit(edit(editor, { offeringName: 'Other name' }), filters).patch, { offering_name: 'Other name' });
    const editLocked = buildOfferingEdit(edit(editor, { familyDetails: { ...editor.draft.familyDetails, tolerance: '0.1 mm' } }), filters);
    assert.ok(editLocked.errors['familyDetails.tolerance']);
    const belowSaved = buildOfferingEdit(edit(editor, { partMeasurements: { ...editor.draft.partMeasurements,
        block: { ...editor.draft.partMeasurements.block, maxLengthMm: 10 } } }), filters);
    assert.match(belowSaved.errors['partMeasurements.block.maxLengthMm'], /saved bounds/);
    assert.ok(buildProviderEdit(edit(providerEditor(resource(provider())), { country: ' ' }), filters).errors.country);
    assert.ok(buildOfferingEdit(edit(editor, { offeringName: ' ' }), filters).errors.offeringName);
});

test('gear quality uses the canonical record and shaft values use the existing text map', () => {
    const gear = {
        ...offering(), part_family: 'gear', service_category: 'precision_gears', supported_part_types: [], part_type_capabilities: {},
        family_capabilities: { gear_quality: { standard: 'ISO', best_class: 6, ...source }, diametral_pitch: { value: 7, ...source } }
    };
    const editor = offeringEditor(resource(gear));
    assert.equal(editor.draft.familyDetails.qualityClass, '6');
    const { patch } = buildOfferingEdit(edit(editor, { familyDetails: { ...editor.draft.familyDetails, qualityClass: '5' } }), filters);
    assert.deepEqual(patch.family_capabilities, { ...gear.family_capabilities, gear_quality: { standard: 'ISO', best_class: 5, ...source } });
    assert.equal(patch.custom_capability_fields, undefined);
    const shaft = offeringEditor(resource({ ...gear, part_family: 'shaft', service_category: 'precision_shafts', family_capabilities: {
        length_mm: { min: 10, max: 250, ...source }
    } }));
    assert.equal(shaft.draft.familyDetails.qualityToleranceStandard, 'ISO 286');
    const result = buildOfferingEdit(edit(shaft, { familyDetails: { ...shaft.draft.familyDetails, toleranceClassFit: '' } }), filters);
    assert.deepEqual(result.errors, {});
    assert.equal(result.patch.custom_capability_fields.tolerance_class_fit, undefined);
    assert.equal(result.patch.family_capabilities, undefined);
});

test('Add offering uses the locked provider identity and the registration offering builder', () => {
    const form = {
        ...emptyRegistrationForm(), providerId: 'other', offeringId: alternateId, offeringName: 'Additional parts',
        partFamily: family, supportStatus: 'unknown', partTypes: ['block', 'roller'],
        partMeasurements: { block: { maxLengthMm: 120 }, roller: { maxDiameterMm: 68 } },
        familyDetails: { tolerance: '0.08 mm', qualityToleranceStandard: 'ISO 286', toleranceClassFit: 'H8' }
    };
    const { payload, errors } = buildAddedOffering(form, provider(), filters);
    assert.deepEqual(errors, {});
    assert.equal(payload.provider_id, undefined);
    assert.equal(payload.offering_id, alternateId);
    assert.equal(payload.support_status, 'confirmed');
    assert.ok(payload.supported_part_types.every((item) => item.support_status === 'confirmed'));
    assert.equal(payload.part_type_capabilities.block.bounding_box_mm.length_mm.max, 120);
    assert.equal(payload.part_type_capabilities.roller.outer_diameter_mm.max, 68);
    assert.equal(payload.custom_capability_fields.tolerance_class_fit, 'H8');
    assert.ok(buildAddedOffering({ ...form, offeringId: 'mdc_stage1b_other_new' }, provider(), filters).errors.offeringId);
});

const save = (changes = { offering_name: 'Edited' }) => ({
    operation: 'save', entity: 'offering', providerId, offeringId, payload: changes, etag: '"old-revision"'
});
const reply = (data = {}, status = 200) => ({ status, data: {
    contract_version: '1.0', operation: 'update', status: 'accepted', provider_id: providerId,
    offering_id: offeringId, offering_ids: [offeringId], publication_id: 'test-publication',
    publication_status: 'sync_pending', sync_status: 'pending', ...data
} });
const missing = () => { throw { status: 404, code: 'offering_not_found' }; };

test('strong revisions and disposable ownership are required for writes', async () => {
    assert.equal(strongEtag('"old-revision"'), true);
    for (const tag of [null, 'unquoted', 'W/"weak"', '"with spaces"', '"x"\r\n']) assert.equal(strongEtag(tag), false);
    for (const request of [
        { ...save(), providerId: 'tasowheel' }, { ...save(), offeringId: 'different' }, { ...save(), etag: 'W/"weak"' }
    ]) {
        assert.equal((await executeManagementWrite(request, { updateOffering: () => assert.fail('unsafe write') })).kind, 'blocked');
    }
    const outcome = await executeManagementWrite(save(), {
        updateOffering: (id, patch, tag) => {
            assert.equal(id, offeringId);
            assert.equal(tag, '"old-revision"');
            assert.deepEqual(patch, { offering_name: 'Edited' });
            return reply();
        },
        getOffering: (id) => {
            assert.equal(id, offeringId);
            return resource({ ...offering(), offering_name: 'Edited' }, '"new-revision"');
        }
    });
    assert.equal(outcome.kind, 'accepted');
    assert.equal(outcome.receipt.syncStatus, 'pending');
    assert.equal(observedWrite(outcome.request, outcome.observed), true);
    assert.equal(writeRecovery(outcome), null);
});

test('lookup restores only the requested offering and rejects a mismatched provider identity', async () => {
    const services = {
        getProvider: async () => resource(provider()),
        listProviderOfferings: async () => ({ provider_id: providerId, offerings: [{ ...offering(), offering_id: alternateId }] }),
        getOffering: () => assert.fail('fallback read of a different offering')
    };
    const result = await loadManagementSnapshot(providerId, offeringId, services);
    assert.equal(result.offering, null);
    await assert.rejects(loadManagementSnapshot('different', offeringId, services), /provider response/);
    await assert.rejects(loadManagementSnapshot(providerId, alternateId, {
        ...services, getOffering: async () => resource({ ...offering(), offering_id: alternateId, provider_id: 'other' })
    }), /requested provider and offering/);
});

test('412 retains the submitted patch and a separate read presents the exact latest revision', async () => {
    const request = save();
    const outcome = await executeManagementWrite(request, {
        updateOffering: () => { throw { status: 412 }; },
        getOffering: () => assert.fail('412 requires deliberate review')
    });
    assert.equal(outcome.kind, 'conflict');
    assert.deepEqual(writeRecovery(outcome).request, request);
    const latest = await observeManagementTarget(request, { getOffering: async () => resource(offering(), '"next"') });
    assert.equal(latest.resource.etag, '"next"');
    assert.equal(latest.matches, false);
});

test('an offering write can advance the parent ETag only when its saved provider fields match', () => {
    const saved = provider();
    const editor = edit(providerEditor(resource(saved)), { providerName: 'Local provider draft' });
    const bumped = acceptParentRevision(editor, resource({ ...saved, offerings: [{ offering_id: alternateId }] }, '"new-parent"'));
    assert.equal(bumped.resource.etag, '"new-parent"');
    assert.equal(bumped.draft.providerName, 'Local provider draft');
    assert.equal(acceptParentRevision(editor, resource({ ...saved, country: 'Other' }, '"unrelated-updated"')), editor);
    assert.equal(acceptParentRevision(editor, resource({ ...saved, provider_id: 'other' }, '"unrelated-id"')), editor);
});

test('503 read-back reconciles matching values without replay and treats mismatches as uncertain', async () => {
    let calls = 0;
    const write = () => { calls++; throw { status: 503, publicationId: 'partial-receipt', syncStatus: 'pending' }; };
    const request = save({ custom_capability_fields: { a: 1, b: 2 } });
    const outcome = await executeManagementWrite(request, {
        updateOffering: write, getOffering: async () => resource({ ...offering(), custom_capability_fields: { b: 2, a: 1 } })
    });
    assert.equal(outcome.kind, 'uncertain');
    assert.equal(outcome.receipt.publicationId, 'partial-receipt');
    assert.equal(writeRecovery(outcome), null);
    assert.equal(calls, 1);
    const bad = await executeManagementWrite(request, {
        updateOffering: write, getOffering: async () => resource({ ...offering(), offering_id: alternateId })
    });
    assert.equal(bad.observed.kind, 'unknown');
    assert.equal(writeRecovery(bad), bad);
    assert.equal(calls, 2);
    const wrongReceipt = await executeManagementWrite(request, {
        updateOffering: () => reply({ offering_ids: [alternateId] }), getOffering: async () => resource(offering())
    });
    assert.equal(wrongReceipt.kind, 'uncertain');
    assert.equal(wrongReceipt.receipt, undefined);
});

test('deletion and Add use exact identities and only canonical 404 establishes absence', async () => {
    const target = { ...save(), operation: 'delete', payload: undefined };
    const result = await executeManagementWrite(target, {
        deleteOffering: (id, etag) => {
            assert.deepEqual([id, etag], [offeringId, '"old-revision"']);
            return reply({ operation: 'delete', target: { entity_type: 'offering', entity_id: offeringId } });
        },
        getOffering: missing
    });
    assert.equal(result.kind, 'accepted');
    assert.equal(result.observed.kind, 'absent');
    assert.equal(writeRecovery(result), null);
    const unknown = await observeManagementTarget(target, { getOffering: () => { throw { status: 404, code: 'mdc_route_not_found' }; } });
    assert.equal(unknown.kind, 'unknown');
    const creation = { ...save(), operation: 'create', payload: { offering_id: offeringId } };
    const duplicate = await executeManagementWrite(creation, {
        createOffering: (id, payload) => {
            assert.equal(id, providerId);
            assert.deepEqual(payload, creation.payload);
            throw { status: 409, code: 'offering_already_exists' };
        },
        getOffering: () => assert.fail('definite rejection must not trigger an automatic read or write')
    });
    assert.equal(duplicate.kind, 'rejected');
    assert.equal(duplicate.code, 'offering_already_exists');
});

test('Provider Area shares the registration fields and omits developer response panels', () => {
    const component = (name) => readFileSync(new URL('../src/components/mdc/' + name + '.js', import.meta.url), 'utf8');
    assert.match(component('ProviderRegistration'), /<ProviderRegistrationFields\b/);
    assert.match(component('ProviderManagement'), /<ProviderRegistrationFields\b/);
    for (const name of ['ProviderDemoPanel', 'ProviderManagement', 'ProviderActionResult', 'ProviderRegistration']) {
        assert.doesNotMatch(component(name), /<pre\b|ProviderPayloadPreview|MDC response details|Additional offering information/);
    }
});
