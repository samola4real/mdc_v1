import { get, sharedPath } from './client';

export const getCatalogFilters = (options) => get(sharedPath('/catalog/filters'), options);
