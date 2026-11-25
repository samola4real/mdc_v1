import { get, sharedPath } from './client';

export const getCatalogFilters = (options) => get(sharedPath('/catalog/filters'), options);

const toOptions = (items) => items.map((item) => ({ ...item, label: item.label || item.value }));

export const normalizeCatalogFilters = (data) => {
    if (data?.contract_version !== '1.0' || !data.part_types
        || !['part_families', 'service_categories', 'materials', 'processes', 'certifications']
            .every((name) => Array.isArray(data[name]))
        || !Object.values(data.part_types).every(Array.isArray)) {
        throw new Error('The catalogue-filter response does not match contract version 1.0.');
    }

    return {
        partFamilies: toOptions(data.part_families),
        partTypes: Object.fromEntries(Object.entries(data.part_types).map(([family, items]) => [family, toOptions(items)])),
        materials: toOptions(data.materials),
        processes: toOptions(data.processes),
        certifications: toOptions(data.certifications),
        serviceCategoryByFamily: Object.fromEntries(data.service_categories.map((item) => [item.part_family, item.value]))
    };
};
