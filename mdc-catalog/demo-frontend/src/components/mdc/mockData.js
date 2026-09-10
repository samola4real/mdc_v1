export const demoBackends = [
    {
        label: 'Active backend',
        value: 'Fuseki + H5 policy',
        tone: 'success',
        description: 'Primary MVD path for evidence-backed semantic service discovery.'
    },
    {
        label: 'Fallback 1',
        value: 'RDFLib + H5 policy',
        tone: 'info',
        description: 'Local RDF fallback with the same H5 policy matching direction.'
    },
    {
        label: 'Fallback 2',
        value: 'Harmonized YAML + H5 matcher',
        tone: 'warning',
        description: 'Structured YAML fallback for static demo continuity.'
    },
    {
        label: 'Dataset',
        value: 'mdc-service-discovery',
        tone: 'info',
        description: 'Named semantic catalogue dataset used in the demo flow.'
    },
    {
        label: 'Demo API namespace',
        value: '/api/demo/',
        tone: 'warning',
        description: 'Future demo-only actions stay outside the Marketplace contract.'
    },
    {
        label: 'Shared API status',
        value: 'unchanged',
        tone: 'success',
        description: 'Marketplace-facing endpoints remain separate from demo controls.'
    }
];

export const workflowSteps = [
    'Provider publishes or updates capability',
    'MDC validates provider data',
    'RDF catalogue is regenerated',
    'Fuseki dataset is refreshed',
    'Consumer searches for service',
    'Evidence-backed results are displayed'
];

export const providers = [
    {
        id: 'tasowheel',
        name: 'Tasowheel Oy',
        country: 'Finland',
        status: 'Demo provider',
        summary: 'Precision component provider used for the static MDC service discovery shell.'
    }
];

export const serviceCategories = [
    'precision_gears',
    'precision_shafts',
    'precision_manufacturing',
    'gear_manufacturing',
    'shaft_manufacturing',
    'turn_mill_services'
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
        serviceCategory: 'precision_manufacturing',
        partFamily: 'metal_part'
    },
    {
        label: 'General precision manufacturing',
        value: 'general_precision_manufacturing',
        serviceCategory: 'precision_manufacturing',
        partFamily: 'general_precision'
    }
];

export const partFamilies = [
    { label: 'Gear', value: 'gear' },
    { label: 'Shaft', value: 'shaft' },
    { label: 'Metal part', value: 'metal_part' }
];

export const partTypes = {
    gears: ['spur_gear', 'helical_gear', 'bevel_gear', 'worm_gear'],
    shafts: ['splined_shaft', 'plain_shaft', 'hollow_shaft'],
    metalParts: ['block', 'plate', 'bracket', 'bushing', 'roller', 'collar']
};

export const allPartTypes = [...partTypes.gears, ...partTypes.shafts, ...partTypes.metalParts];

export const metalPartTypeOptions = [
    { label: 'Block', value: 'block' },
    { label: 'Plate', value: 'plate' },
    { label: 'Bracket', value: 'bracket' },
    { label: 'Bushing', value: 'bushing' },
    { label: 'Roller', value: 'roller' },
    { label: 'Collar', value: 'collar' }
];

export const materials = [
    'alloyed_carburizing_steel',
    '18CrNiMo7-6',
    '16MnCr5',
    '20MnCr5'
];

export const processes = [
    'machining',
    'hobbing',
    'gear_shaping',
    'deburring',
    'hard_turning',
    'grinding',
    'tooth_grinding',
    'gear_grinding',
    'gear_cutting',
    'surface_grinding',
    'milling',
    'turn_mill'
];

export const certifications = [
    'ISO9001_2015',
    'ISO14001_2015',
    'ISO_TS_16949_partial',
    'APQP'
];

export const offerings = [
    {
        id: 'precision-gears',
        offering: 'Precision gears',
        serviceCategory: 'gear_manufacturing',
        partFamily: 'gears',
        supportedPartTypes: ['spur_gear', 'helical_gear', 'bevel_gear', 'worm_gear'],
        materials: ['alloyed_carburizing_steel', '18CrNiMo7-6', '16MnCr5', '20MnCr5'],
        processes: ['hobbing', 'gear_grinding', 'turn_mill', 'gear_cutting'],
        status: 'ready'
    },
    {
        id: 'precision-shafts',
        offering: 'Precision shafts',
        serviceCategory: 'shaft_manufacturing',
        partFamily: 'shafts',
        supportedPartTypes: ['splined_shaft', 'plain_shaft', 'hollow_shaft'],
        materials: ['alloyed_carburizing_steel', '16MnCr5', '20MnCr5'],
        processes: ['hard_turning', 'grinding', 'milling', 'turn_mill'],
        status: 'ready'
    }
];

export const mockSearchResults = [
    {
        id: 'result-tasowheel-gears',
        provider: 'Tasowheel Oy',
        offering: 'Precision gears',
        status: 'confirmed',
        partTypeSupport: 'confirmed',
        evidence: [
            'Module: 0.3-10',
            'Diameter: 10-450 mm',
            'Material: alloyed carburizing steel',
            'Grades: 18CrNiMo7-6, 16MnCr5, 20MnCr5',
            'Processes: hobbing, gear grinding, turn-mill',
            'Certifications: ISO9001_2015, ISO14001_2015'
        ],
        advanced: [
            'Primary backend: Fuseki + H5 policy',
            'Dataset: mdc-service-discovery',
            'Score intentionally hidden in F1 shell'
        ]
    }
];

export const auditRows = [
    {
        id: 1,
        time: '09:00',
        action: 'Demo shell opened',
        status: 'info',
        message: 'Static admin panel loaded with mock catalogue status.'
    },
    {
        id: 2,
        time: '09:05',
        action: 'Provider preview',
        status: 'success',
        message: 'Tasowheel precision gears preview shown without backend call.'
    },
    {
        id: 3,
        time: '09:10',
        action: 'Consumer search',
        status: 'success',
        message: 'Mock evidence-backed result displayed from local static data.'
    },
    {
        id: 4,
        time: '09:15',
        action: 'RDF reload action',
        status: 'warning',
        message: 'Placeholder only; future endpoint will live under /api/demo/.'
    }
];
