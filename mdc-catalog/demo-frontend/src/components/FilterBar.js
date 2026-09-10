import React from 'react';
import { Dropdown } from 'primereact/dropdown';
import { Calendar } from 'primereact/calendar';
import { Button } from 'primereact/button';

/**
 * Reusable filter bar for analytics-style pages.
 * Pass `filters` declaratively; the component renders the matching control.
 *
 *   <FilterBar
 *     filters={[
 *       { name: 'range', kind: 'daterange', label: 'Period' },
 *       { name: 'dim',   kind: 'dropdown',  label: 'Dimension',  options: [...] },
 *       { name: 'gran',  kind: 'dropdown',  label: 'Granularity', options: [...] }
 *     ]}
 *     values={state}
 *     onChange={setState}
 *     actions={<Button label="Export CSV" />}
 *   />
 */
const FilterBar = ({ filters = [], values = {}, onChange, actions }) => {
    const set = (name, value) => onChange?.({ ...values, [name]: value });

    const renderControl = (f) => {
        if (f.kind === 'daterange') {
            return (
                <Calendar
                    value={values[f.name]}
                    onChange={(e) => set(f.name, e.value)}
                    selectionMode="range"
                    readOnlyInput
                    dateFormat="dd/mm/yy"
                    showIcon
                    placeholder="Select range"
                />
            );
        }
        if (f.kind === 'dropdown') {
            return (
                <Dropdown
                    value={values[f.name]}
                    onChange={(e) => set(f.name, e.value)}
                    options={f.options}
                    placeholder={f.placeholder || 'Select...'}
                    showClear={f.clearable}
                />
            );
        }
        return null;
    };

    return (
        <section className="filter-bar">
            <div className="filter-bar__controls">
                {filters.map((f) => (
                    <label key={f.name} className="filter-bar__field">
                        <span>{f.label}</span>
                        {renderControl(f)}
                    </label>
                ))}
            </div>
            {actions ? <div className="filter-bar__actions">{actions}</div> : null}
        </section>
    );
};

export default FilterBar;
