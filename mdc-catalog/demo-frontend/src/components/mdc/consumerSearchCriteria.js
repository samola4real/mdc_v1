const FAMILY_SPECS = 'part_family_specifications';
const TYPE_SPECS = 'part_type_specifications';
const GENERIC = 'generic_requirements';

const numberField = (id, label, key, group = FAMILY_SPECS, bound = 'max') => ({ id, label, key, group, bound });
const tolerance = numberField('toleranceMm', 'Tolerance (mm)', 'tolerance_mm');
const faceWidth = numberField('faceWidthMm', 'Face width (mm)', 'face_width_mm', TYPE_SPECS, 'exact');
const gearFields = [
    numberField('module', 'Module (mm)', 'module', FAMILY_SPECS, 'exact'),
    numberField('diametralPitch', 'Diametral pitch', 'diametral_pitch', FAMILY_SPECS, 'pointRange'),
    numberField('outsideDiameterMm', 'Outside diameter (mm)', 'outside_diameter_mm')
];
const gearQuality = [
    { id: 'qualityStandard', label: 'Quality standard', text: true, placeholder: 'Enter the standard', hint: 'Enter the specified DIN, ISO or other standard.' },
    { id: 'qualityClass', label: 'Quality class', hint: 'Enter the maximum acceptable class.' }
];
const shaftFields = [
    numberField('lengthMm', 'Length (mm)', 'length_mm'),
    numberField('outerDiameterMm', 'Outer diameter (mm)', 'outer_diameter_mm'),
    tolerance
];
const shaftTypeFields = {
    splined_shaft: [numberField('splineModule', 'Spline module', 'spline_module', TYPE_SPECS, 'exact')],
    hollow_shaft: [
        numberField('internalDiameterMm', 'Internal diameter (mm)', 'inner_diameter_mm', TYPE_SPECS),
        numberField('wallThicknessMm', 'Wall thickness (mm)', 'wall_thickness_mm', TYPE_SPECS, 'exact')
    ]
};

const boxLengthAndWidth = [
    numberField('metalLengthMm', 'Length (mm)', 'bounding_box_mm.length_mm'),
    numberField('metalWidthMm', 'Width (mm)', 'bounding_box_mm.width_mm')
];
const boxHeight = numberField('metalHeightMm', 'Height (mm)', 'bounding_box_mm.height_mm');
const holeCount = { ...numberField('mountingHolesCount', 'Number of holes', 'number_of_holes', TYPE_SPECS), integer: true };
const weight = numberField('metalWeightKg', 'Weight (kg)', 'weight_kg', GENERIC, 'value');
const surfaceFinish = numberField('surfaceFinish', 'Surface finish Ra (µm)', 'surface_finish_ra_um', GENERIC);
const prismaticFinish = [weight, { ...tolerance, group: GENERIC }, surfaceFinish];
const rotationalDimensions = [
    numberField('metalInnerDiameterMm', 'Inner diameter (mm)', 'inner_diameter_mm'),
    numberField('metalOuterDiameterMm', 'Outer diameter (mm)', 'outer_diameter_mm'),
    numberField('metalLengthMm', 'Overall length (mm)', 'overall_length_mm')
];

const metalProfiles = {
    block: { title: 'Block Specifications', fields: [...boxLengthAndWidth, boxHeight, holeCount, ...prismaticFinish] },
    plate: {
        title: 'Plate Specifications',
        fields: [...boxLengthAndWidth, numberField('metalThicknessMm', 'Thickness (mm)', 'bounding_box_mm.height_mm'), holeCount, ...prismaticFinish]
    },
    bracket: {
        title: 'Bracket Specifications',
        fields: [
            ...boxLengthAndWidth, boxHeight,
            numberField('flangeLengthMm', 'Vertical flange length (mm)', 'vertical_flange_length_mm', TYPE_SPECS),
            numberField('horizontalFlangeLengthMm', 'Horizontal flange length (mm)', 'horizontal_flange_length_mm', TYPE_SPECS),
            ...prismaticFinish
        ]
    },
    bushing: {
        title: 'Bushing Specifications',
        fields: [...rotationalDimensions, numberField('flangeDiameterMm', 'Flange diameter (mm)', 'flange_diameter_mm', TYPE_SPECS), tolerance, surfaceFinish]
    },
    roller: { title: 'Roller Specifications', fields: [...rotationalDimensions, weight, tolerance, surfaceFinish] },
    collar: { title: 'Collar Specifications', fields: [...rotationalDimensions, tolerance, surfaceFinish] }
};

export const getSpecificationProfile = (family, type) => {
    if (family === 'gear') {
        const faceFields = ['spur_gear', 'helical_gear', 'bevel_gear', 'crown_gear'].includes(type) ? [faceWidth] : [];
        return { title: 'Gear Specifications', fields: [...gearFields, tolerance, ...gearQuality, ...faceFields] };
    }
    if (family === 'shaft') {
        const typeFields = Object.hasOwn(shaftTypeFields, type) ? shaftTypeFields[type] : [];
        return { title: 'Shaft Specifications', fields: [...shaftFields, ...typeFields] };
    }
    return Object.hasOwn(metalProfiles, type) && family === 'metal_part'
        ? metalProfiles[type]
        : { title: 'Metal Part Specifications', fields: [] };
};

const hasOption = (options, value) => options?.some((item) => item.value === value);

export const availableSearchFamilies = (catalogue) => catalogue.partFamilies.filter(({ value }) => (
    Object.hasOwn(catalogue.serviceCategoryByFamily, value) && catalogue.serviceCategoryByFamily[value]
    && catalogue.partTypes[value]?.length
));

export const defaultPartType = (catalogue, family) => (
    family === 'gear' && hasOption(catalogue.partTypes.gear, 'spur_gear')
        ? 'spur_gear'
        : catalogue.partTypes[family]?.[0]?.value ?? null
);

export const resetSearchForm = (catalogue) => {
    const families = availableSearchFamilies(catalogue);
    const partFamily = hasOption(families, 'gear') ? 'gear' : families[0]?.value ?? null;
    return { partFamily, partType: defaultPartType(catalogue, partFamily), materials: [], processes: [], certifications: [], specifications: {} };
};

export const changePartSelection = (form, partFamily, partType) => ({
    ...form, partFamily, partType, specifications: {}
});

export const validateSearchCatalogue = (catalogue) => {
    const lists = [catalogue.partFamilies, catalogue.materials, catalogue.processes, catalogue.certifications, ...Object.values(catalogue.partTypes)];
    if (lists.some((list) => list.some((option) => typeof option.value !== 'string' || !option.value.trim()
        || typeof option.label !== 'string' || !option.label.trim())) || !availableSearchFamilies(catalogue).length) {
        throw new Error('The catalogue does not contain usable manufacturing options.');
    }
    return catalogue;
};

export const hasValidPartSelection = (form, catalogue) => (
    hasOption(availableSearchFamilies(catalogue), form.partFamily) && hasOption(catalogue.partTypes[form.partFamily], form.partType)
);

const positiveDecimal = /^(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i;

const parseNumber = (raw, integer) => {
    const text = String(raw).trim().replace(',', '.');
    const value = Number(text);
    if (integer) return /^\d+$/.test(text) && Number.isSafeInteger(value) && value > 0 ? value : null;
    return positiveDecimal.test(text) && Number.isFinite(value) && value > 0 ? value : null;
};

export const NUMERIC_ERROR = 'Enter a number greater than 0.';
export const INTEGER_ERROR = 'Enter a whole number greater than 0.';
export const INVALID_REQUIREMENTS = 'Please review your manufacturing requirements.';

const numericRequirement = (value, bound) => {
    if (bound === 'value') return value;
    if (bound === 'pointRange') return { min: value, max: value };
    return { [bound]: value };
};

// Use the rendered profile for serialization as well, so hidden inputs cannot become search criteria.
export const buildSearchPayload = (form, catalogue, subject) => {
    const errors = {};
    const requirements = { [FAMILY_SPECS]: {}, [TYPE_SPECS]: {}, [GENERIC]: {} };
    const { partFamily, partType, materials, processes, certifications, specifications } = form;
    const { fields } = getSpecificationProfile(partFamily, partType);

    if (!hasValidPartSelection(form, catalogue)) {
        errors.selection = INVALID_REQUIREMENTS;
    }
    for (const [field, selections] of Object.entries({ materials, processes, certifications })) {
        if (selections.some((value) => !hasOption(catalogue[field], value))) errors.selection = INVALID_REQUIREMENTS;
        if (selections.length) requirements[GENERIC][field] = [...new Set(selections)];
    }

    for (const { id, key, group, bound, integer } of fields) {
        const raw = specifications[id];
        if (!group || raw == null || raw === '') continue;
        const value = parseNumber(raw, integer);
        if (value === null) {
            errors[id] = integer ? INTEGER_ERROR : NUMERIC_ERROR;
            continue;
        }

        const [field, component] = key.split('.');
        const criterion = numericRequirement(value, bound);
        if (component) {
            (requirements[group][field] ??= {})[component] = criterion;
        } else {
            requirements[group][field] = criterion;
        }
    }

    if (partFamily === 'gear') {
        const standard = specifications.qualityStandard?.trim();
        const rawClass = specifications.qualityClass;
        if (standard || (rawClass != null && rawClass !== '')) {
            const maxClass = parseNumber(rawClass, false);
            if (!standard) errors.qualityStandard = 'Enter the quality standard.';
            if (!maxClass) errors.qualityClass = rawClass ? NUMERIC_ERROR : 'Enter the quality class.';
            if (standard && maxClass) requirements[FAMILY_SPECS].gear_quality = { standard, max_class: maxClass };
        }
    }

    if (Object.keys(errors).length) return { errors };

    return {
        payload: {
            contract_version: '1.0',
            request_id: `req-${globalThis.crypto.randomUUID()}`,
            consumer_id: typeof subject === 'string' && subject.trim() ? subject : 'consumer_service_discovery',
            service_category: catalogue.serviceCategoryByFamily[partFamily],
            part_family: partFamily,
            part_type: partType,
            requirements,
            match_policy: { discovery_mode: 'lenient' }
        }
    };
};
