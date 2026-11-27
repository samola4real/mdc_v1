import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import {
    buildPublishedOffering, buildRequirementComparison, createOfferingDetailsLoader
} from '../src/components/mdc/consumerOfferingDetails.js';
import { buildOfferingPdf, offeringPdfFilename } from '../src/components/mdc/offeringPdf.js';
import { NOT_PROVIDED, offeringKey } from '../src/components/mdc/searchResultFormatters.js';

const option = (value, label) => ({ value, label });
const catalogue = {
    serviceCategories: [option('precision_gears', 'Precision gears'), option('precision_metal_parts', 'Precision metal parts')],
    partTypes: {
        gear: [option('spur_gear', 'Spur gear'), option('bevel_gear', 'Bevel gear')],
        metal_part: [option('plate', 'Plate')]
    },
    materials: [option('steel', 'Steel'), option('aluminum', 'Aluminum'), option('titanium', 'Titanium'),
        option('alloyed_carburizing_steel', 'Alloyed carburizing steel')],
    processes: [option('hobbing', 'Hobbing'), option('milling', 'Milling')],
    certifications: [option('ISO9001_2015', 'ISO 9001:2015'), option('ISO14001_2015', 'ISO 14001:2015')]
};
const context = {
    partType: 'spur_gear', partTypeLabel: 'Spur gear', catalogue,
    requirements: { part_family_specifications: { module: { exact: 4 } }, part_type_specifications: {}, generic_requirements: {} }
};
const provider = {
    contract_version: '1.0', provider_id: 'fixture_provider', provider_name: 'Äärelä Engineering Oy', country: 'Finland',
    status: 'active',
    custom_provider_fields: { description: 'Precision components for partners.', private_data: 'PUBLISH_NOTHING_01' },
    publication_metadata: { internal: 'PUBLISH_NOTHING_02' },
    certifications: [{ code: 'ISO9001_2015', source_note: 'PUBLISH_NOTHING_03' }]
};
const offering = {
    contract_version: '1.0', provider_id: provider.provider_id, offering_id: 'fixture_gears', offering_name: 'Precision gears',
    part_family: 'gear', service_category: 'precision_gears', is_active: true, support_status: 'confirmed',
    supported_part_types: [{ part_type: 'spur_gear', support_status: 'confirmed' }, { part_type: 'bevel_gear', support_status: 'candidate_requiring_confirmation' }],
    family_capabilities: {
        module: { min: 0.3, max: 10, source_note: 'PUBLISH_NOTHING_04' },
        outside_diameter_mm: { min: 10, max: 450 }, gear_quality: { standard: 'DIN', best_class: 4 },
        arbitrary_field: 'PUBLISH_NOTHING_05'
    },
    part_type_capabilities: { spur_gear: { face_width_mm: { value: 12.25 } }, bevel_gear: { shaft_angle_deg: { exact: 90 } } },
    generic_capabilities: {
        materials: [{ material: 'steel', available_grades: ['42CrMo4', 'Cr–äĆ'] }, { material: 'aluminum', available_grades: ['7075'] },
            { material: 'steel', available_grades: ['42CrMo4', '16MnCr5'] }],
        processes: [{ process: 'hobbing', delivery_mode: 'in_house' }, { process: 'milling', delivery_mode: 'subcontracted' }],
        batch_size: { min: 100, max: 800 }, lead_time_weeks: { max: 5 }, weight_kg: { max: 90 },
        surface_finish_ra_um: { exact: 0.625 }, certifications: [{ code: 'ISO14001_2015' }]
    },
    custom_offering_fields: { production_mode: 'Batch production', industries_served: ['Aerospace'], arbitrary_service_field: 'PUBLISH_NOTHING_06' },
    custom_capability_fields: { note: 'PUBLISH_NOTHING_07' }
};
const result = {
    provider_id: provider.provider_id, provider_name: provider.provider_name, offering_id: offering.offering_id,
    offering_name: offering.offering_name, service_category: offering.service_category, part_family: offering.part_family,
    matched_capabilities: [
        { field: 'module', requested: { exact: 4 }, provided: { min: 0.3, max: 10 } },
        { field: 'materials', requested: ['steel'], provided: [{ material: 'steel', available_grades: ['16MnCr5', '42CrMo4'] }] },
        { field: 'processes', requested: ['hobbing'], provided: [{ process: 'hobbing', delivery_mode: 'in_house' }, { process: 'milling' }] },
        { field: 'certifications', requested: ['ISO14001_2015'], provided: [{ code: 'ISO14001_2015' }] }
    ]
};
const rowsOf = (model, section) => Object.fromEntries(model.sections.find(({ title }) => title === section).rows
    .map(({ label, value }) => [label, value]));

test('requirement comparison contains the confirmed type and every requested criterion with search evidence', () => {
    const rows = buildRequirementComparison(result, 'Spur gear', catalogue);
    assert.deepEqual(rows, [
        { field: 'part_type', label: 'Part type', requested: 'Spur gear', provided: 'Spur gear' },
        { field: 'module', label: 'Module (mm)', requested: '4', provided: '0.3–10' },
        { field: 'materials', label: 'Materials', requested: 'Steel', provided: 'Steel (16MnCr5, 42CrMo4)' },
        { field: 'processes', label: 'Manufacturing processes', requested: 'Hobbing', provided: 'Hobbing' },
        { field: 'certifications', label: 'Certifications', requested: 'ISO 14001:2015', provided: 'ISO 14001:2015' }
    ].map((row) => ({ ...row, status: 'Matched' })));
    const missing = buildRequirementComparison({ ...result, matched_capabilities: [{ field: 'module', requested: { exact: 4 } }] }, 'Spur gear', catalogue);
    assert.equal(missing[1].provided, NOT_PROVIDED);
    const typeOnly = buildRequirementComparison({ ...result, matched_capabilities: [] }, 'Spur gear', catalogue);
    assert.deepEqual(typeOnly, rows.slice(0, 1));
});

test('lenient comparison keeps semantic material evidence and shows unresolved preferences independently', () => {
    const publishedMaterial = { material: 'alloyed_carburizing_steel', available_grades: ['16MnCr5'] };
    const lenient = {
        ...result,
        matched_capabilities: [{ field: 'materials', requested: ['steel'], provided: [publishedMaterial] }],
        unmatched_capabilities: [{ field: 'delivery', requested: 2, provided: { max: 5 } }],
        unknown_capabilities: [
            { field: 'materials', requested: ['titanium'], provided: null },
            { field: 'processes', requested: ['milling'], provided: null }
        ]
    };
    const lenientContext = { ...context, discoveryMode: 'lenient' };
    assert.deepEqual(buildRequirementComparison(lenient, 'Spur gear', catalogue, 'lenient').slice(1), [
        { field: 'materials', label: 'Material alternative', requested: 'Steel', provided: 'Alloyed carburizing steel (16MnCr5)', status: 'Matched' },
        { field: 'delivery', label: 'Delivery preference (weeks)', requested: '2', provided: '≤ 5', status: 'Not matched' },
        { field: 'materials', label: 'Material alternative', requested: 'Titanium', provided: NOT_PROVIDED, status: 'Not confirmed' },
        { field: 'processes', label: 'Process preference', requested: 'Milling', provided: NOT_PROVIDED, status: 'Not confirmed' }
    ]);
    const details = { ...offering, generic_capabilities: { materials: [publishedMaterial], lead_time_weeks: { max: 5 } } };
    const view = buildPublishedOffering(lenient, lenientContext, provider, details);
    assert.deepEqual(rowsOf(view, 'Materials and grades'), { 'Alloyed carburizing steel': '16MnCr5' });
    assert.equal(buildPublishedOffering(lenient, lenientContext, provider, offering), null);
    assert.equal(buildPublishedOffering(lenient, lenientContext, provider, {
        ...details, generic_capabilities: { ...details.generic_capabilities, lead_time_weeks: { max: 2 } }
    }), null);
});

test('one publishable offering model keeps ranges, type-specific values, service facts, grades and certification scopes', () => {
    const view = buildPublishedOffering(result, context, provider, offering);
    assert.equal(view.providerName, provider.provider_name);
    assert.equal(view.offeringId, offering.offering_id);
    assert.deepEqual(rowsOf(view, 'Supported part types'), { 'Spur gear': 'Confirmed', 'Bevel gear': 'Requires confirmation' });
    assert.deepEqual(rowsOf(view, 'Family specifications'), {
        'Module (mm)': '0.3–10', 'Outside diameter (mm)': '10–450', 'Gear quality': 'DIN, best class 4'
    });
    assert.deepEqual(rowsOf(view, 'Spur gear specifications'), { 'Face width (mm)': '12.25' });
    assert.deepEqual(rowsOf(view, 'Materials and grades'), { Steel: '42CrMo4, Cr–äĆ, 16MnCr5', Aluminum: '7075' });
    assert.deepEqual(rowsOf(view, 'Manufacturing processes'), { Hobbing: 'In-house', Milling: 'Subcontracted' });
    assert.deepEqual(rowsOf(view, 'Provider-level certifications'), { 'ISO 9001:2015': undefined });
    assert.deepEqual(rowsOf(view, 'Offering certifications'), { 'ISO 14001:2015': undefined });
    assert.deepEqual(rowsOf(view, 'Provider and service'), {
        'Service category': 'Precision gears', Country: 'Finland', 'Provider description': 'Precision components for partners.',
        'Production mode': 'Batch production', 'Industries served': 'Aerospace'
    });
    assert.deepEqual(rowsOf(view, 'General capabilities'), {
        'Batch size (pieces)': '100–800', 'Lead time (weeks)': '≤ 5', 'Weight (kg)': '≤ 90', 'Surface finish Ra (µm)': '0.625'
    });
    assert.doesNotMatch(JSON.stringify(view), /PUBLISH_NOTHING|source_note|publication_metadata|score/);
});

test('valid missing data omits empty sections and keeps grades scoped to the right material', () => {
    const sparse = buildPublishedOffering({ ...result, matched_capabilities: [] }, context, { ...provider, certifications: [], country: '' }, {
        ...offering, family_capabilities: {}, part_type_capabilities: {},
        generic_capabilities: { materials: [{ material: 'steel' }] }
    });
    assert.deepEqual(rowsOf(sparse, 'Materials and grades'), { Steel: 'Not published' });
    assert(!sparse.sections.some(({ title }) => ['Manufacturing processes', 'Family specifications', 'Provider-level certifications'].includes(title)));
    assert(!Object.hasOwn(rowsOf(sparse, 'Provider and service'), 'Country'));
});

test('prismatic bounding boxes and exact, value and one-sided dimensions retain labels and units', () => {
    const metal = {
        ...offering, part_family: 'metal_part', service_category: 'precision_metal_parts',
        supported_part_types: [{ part_type: 'plate', support_status: 'confirmed' }],
        family_capabilities: { bounding_box_mm: { length_mm: { min: 25 }, width_mm: { max: 145 }, height_mm: { exact: 13.5 } } },
        part_type_capabilities: { plate: { number_of_holes: { value: 4 } } }
    };
    const details = buildPublishedOffering({
        ...result, part_family: metal.part_family, service_category: metal.service_category, matched_capabilities: []
    }, { ...context, partType: 'plate', partTypeLabel: 'Plate' }, provider, metal);
    assert.deepEqual(rowsOf(details, 'Family specifications'),
        { 'Bounding box': 'Length (mm): ≥ 25, Width (mm): ≤ 145, Height (mm): 13.5' });
    assert.deepEqual(rowsOf(details, 'Plate specifications'), { 'Number of holes': '4' });
});

test('mismatched identity, ownership, active status, family/category or selected support makes details unusable', () => {
    for (const changed of [
        { offering_id: 'some_other_offering' }, { provider_id: 'someone_else' },
        { offering_name: 'Renamed' }, { service_category: 'precision_shafts' }, { part_family: 'shaft' },
        { is_active: false }, { support_status: 'unknown' }, { supported_part_types: [] },
        { supported_part_types: [{ part_type: 'spur_gear', support_status: 'candidate_requiring_confirmation' }] }
    ]) assert.equal(buildPublishedOffering(result, context, provider, { ...offering, ...changed }), null);
    for (const changed of [{ provider_id: 'wrong' }, { status: 'suspended' }, { provider_name: 'New brand' }]) {
        assert.equal(buildPublishedOffering(result, context, { ...provider, ...changed }, offering), null);
    }
});

test('a changed or disappeared capability conflicts with earlier evidence even if other facts remain published', () => {
    assert.equal(buildPublishedOffering(result, context, provider, { ...offering, family_capabilities: { module: { min: 0.3, max: 6 } } }), null);
    for (const changed of [
        { materials: [{ material: 'steel', available_grades: ['16MnCr5'] }] },
        { processes: [{ process: 'hobbing', delivery_mode: 'subcontracted' }] },
        { certifications: [] }
    ]) assert.equal(buildPublishedOffering(result, context, provider, { ...offering, generic_capabilities: { ...offering.generic_capabilities, ...changed } }), null);
    const typedResult = { ...result, matched_capabilities: [{ field: 'face_width_mm', requested: { exact: 12.25 }, provided: { exact: 12.25 } }] };
    const typedContext = { ...context, requirements: { ...context.requirements, part_type_specifications: { face_width_mm: { exact: 12.25 } } } };
    assert(buildPublishedOffering(typedResult, typedContext, provider, offering));
    assert.equal(buildPublishedOffering(typedResult, typedContext, provider, { ...offering, part_type_capabilities: {} }), null);
});

test('details start on selection, are deduplicated within a search and never share records across offering IDs', async () => {
    const calls = [];
    const makeSecond = (data) => ({ ...data, offering_id: 'fixture_other_gear', offering_name: 'Other gears' });
    const loader = createOfferingDetailsLoader({
        getProvider(id) { calls.push(['provider', id]); return { data: provider }; },
        getOffering(id) { calls.push(['offering', id]); return { data: id === offering.offering_id ? offering : makeSecond(offering) }; }
    });
    const log = [];
    const publish = (key, entry) => log.push([key, entry]);
    assert.deepEqual(calls, []);
    await Promise.all([loader.load(result, context, publish), loader.load(result, context, publish)]);
    await loader.load(result, context, publish);
    await loader.load(makeSecond(result), context, publish);
    assert.equal(calls.length, 4);
    assert.deepEqual(log.map(([key, entry]) => [key, entry.kind]),
        [[offeringKey(result), 'loading'], [offeringKey(result), 'ready'], [offeringKey(makeSecond(result)), 'loading'], [offeringKey(makeSecond(result)), 'ready']]);
    assert.equal(log.at(-1)[1].details.offeringName, 'Other gears');
});

test('clearing a search scope prevents an old request from overwriting a subsequent load of the same identity', async () => {
    let finishFirst;
    const first = new Promise((resolve) => { finishFirst = resolve; });
    let offeringCalls = 0;
    const loader = createOfferingDetailsLoader({
        getProvider: () => ({ data: provider }),
        getOffering: () => (++offeringCalls === 1 ? first : { data: offering })
    });
    const published = [];
    const notify = (key, data) => published.push([key, data.kind]);
    const pending = loader.load(result, context, notify);
    loader.clear();
    await loader.load(result, context, notify);
    finishFirst({ data: { ...offering, is_active: false } });
    await pending;
    assert.deepEqual(published.map(([, kind]) => kind), ['loading', 'loading', 'ready']);
});

test('detail transport failures are retryable while missing and changed records require a new search', async () => {
    for (const [failure, failureKind] of [[502, 'error'], [404, 'unavailable'], [null, 'changed']]) {
        let calls = 0;
        const loader = createOfferingDetailsLoader({
            getProvider: () => ({ data: provider }),
            async getOffering() {
                if (++calls > 1) return { data: offering };
                if (failure) throw Object.assign(new Error('internal fixture'), { status: failure });
                return { data: { ...offering, is_active: false } };
            }
        });
        const kinds = [];
        const publish = (_key, entry) => kinds.push(entry.kind);
        await loader.load(result, context, publish);
        await loader.load(result, context, publish);
        await loader.load(result, context, publish, true);
        assert.deepEqual(kinds, failureKind === 'error' ? ['loading', failureKind, 'loading', 'ready'] : ['loading', failureKind]);
    }
});

test('PDF uses the allowlisted view model, embeds Unicode and paginates long values', () => {
    const longDescription = 'Éléments précis, Łódź, Ra ≤ 0.625 µm. '.repeat(150);
    const published = buildPublishedOffering(result, context,
        { ...provider, custom_provider_fields: { description: longDescription, private: 'PUBLISH_NOTHING_08' } }, offering);
    const comparison = buildRequirementComparison(result, context.partTypeLabel, catalogue);
    const font = readFileSync(new URL('../public/layout/fonts/offering-pdf/DejaVuSans.ttf', import.meta.url)).toString('base64');
    const pdf = buildOfferingPdf(published, comparison, font, new Date('2026-11-27T12:00:00Z'));
    const fontMetadata = pdf.getFont().metadata;
    for (const character of 'ÄäĆŁóź≤≥µ–°Δ') assert(fontMetadata.characterToGlyph(character.codePointAt(0)), character);
    assert(pdf.getNumberOfPages() >= 3);
    const output = Buffer.from(pdf.output('arraybuffer'));
    assert.match(output.toString('ascii', 0, 5), /^%PDF-/);
    assert.match(output.toString('ascii'), /\/FontFile2/);
    assert.match(output.toString('ascii'), /\/ToUnicode/);
    assert.match(output.toString('ascii'), /%%EOF\s*$/);
    assert.doesNotMatch(JSON.stringify(published), /PUBLISH_NOTHING/);
    assert.throws(() => buildOfferingPdf({ ...published, providerName: '株式会社' }, comparison, font),
        { code: 'unsupported_pdf_characters' });
});

test('file names are exact for catalogue offerings and safe for filesystem special cases', () => {
    assert.equal(offeringPdfFilename('fixture_gears'), 'fixture_gears.pdf');
    assert.equal(offeringPdfFilename('../night shift/offer?'), '_night_shift_offer_.pdf');
    assert.equal(offeringPdfFilename('COM1'), 'offering_COM1.pdf');
    assert(offeringPdfFilename('x'.repeat(300)).length <= 124);
});
