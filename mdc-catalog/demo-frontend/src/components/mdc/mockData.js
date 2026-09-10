export const workflowSteps = [
    'Provider publishes or updates capability',
    'MDC validates provider data',
    'RDF catalogue is regenerated',
    'Fuseki dataset is refreshed',
    'Consumer searches for service',
    'Evidence-backed results are displayed'
];

export const capabilityTemplates = [
    {
        label: 'Gear manufacturing',
        value: 'gear_manufacturing',
        serviceCategory: 'precision_gears',
        partFamily: 'gear'
    },
    {
        label: 'Shaft manufacturing',
        value: 'shaft_manufacturing',
        serviceCategory: 'precision_shafts',
        partFamily: 'shaft'
    },
    {
        label: 'Metal-part manufacturing',
        value: 'metal_part_manufacturing',
        serviceCategory: 'precision_metal_parts',
        partFamily: 'metal_part'
    }
];

export const partFamilies = [
    { label: 'Gear', value: 'gear' },
    { label: 'Shaft', value: 'shaft' },
    { label: 'Metal part', value: 'metal_part' }
];

export const partTypes = {
    gears: ['spur_gear', 'helical_gear', 'bevel_gear', 'worm_gear', 'crown_gear'],
    shafts: ['plain_shaft', 'stepped_shaft', 'splined_shaft', 'worm_shaft', 'hollow_shaft'],
    metalParts: ['block', 'plate', 'bracket', 'bushing', 'roller', 'collar']
};

export const metalPartTypeOptions = [
    { label: 'Block', value: 'block' },
    { label: 'Plate', value: 'plate' },
    { label: 'Bracket', value: 'bracket' },
    { label: 'Bushing', value: 'bushing' },
    { label: 'Roller', value: 'roller' },
    { label: 'Collar', value: 'collar' }
];

export const materials = [
    'steel',
    'alloyed_carburizing_steel',
    'stainless_steel',
    'aluminum',
    'titanium',
    'nickel_alloy'
];

export const processes = [
    'machining',
    'turning',
    'milling',
    'hobbing',
    'gear_shaping',
    'deburring',
    'hard_turning',
    'grinding',
    'tooth_grinding',
    'gear_grinding',
    'gear_cutting',
    'surface_grinding',
    'heat_treatment',
    'turn_mill',
    'inspection'
];

export const certifications = [
    'ISO9001_2015',
    'ISO14001_2015',
    'ISO_TS_16949_partial',
    'APQP',
    'aerospace_traceability',
    'full_traceability'
];
