import React from 'react';
import { Button } from 'primereact/button';
import { Dropdown } from 'primereact/dropdown';
import { InputNumber } from 'primereact/inputnumber';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { MultiSelect } from 'primereact/multiselect';
import { Panel } from 'primereact/panel';
import {
    FAMILY_RANGES, GENERAL_RANGES, QUALITY_STANDARDS, SUPPORT_STATUSES, measurementFields, registrationPartRanges, selectRegistrationFamily
} from './providerRegistrationPayload';
import { catalogueLabel, retainedPartDraft, retainSelectionOrder, selectsRemoval, withSavedOptions } from './providerManagementDraft';

function Field({ name, label, value, onChange, error, help, required, kind = 'text',
    options, disabled, readOnly, suffix, decimal, width = 'md:col-4', heading = false,
    idPrefix = 'registration', viewOnly, locked, retainPrecision }) {
    const id = idPrefix + '-' + name.replaceAll('.', '-');
    const staticValue = viewOnly || Boolean(locked?.[name]);
    const common = {
        className: 'w-full' + (error ? ' p-invalid' : ''),
        disabled,
        'aria-invalid': Boolean(error),
        'aria-required': required,
        'aria-describedby': [help && id + '-help', error && id + '-error'].filter(Boolean).join(' ') || undefined
    };
    let control;
    if (staticValue) {
        let display = value;
        if (kind === 'select') display = value && catalogueLabel(options, value);
        if (kind === 'multi') display = value?.map((item) => catalogueLabel(options, item)).join(', ');
        if (kind === 'number' && value != null) display = value + (suffix || '');
        control = (
            <div className="mdc-provider-saved-value" aria-labelledby={id + '-label'}>
                {display == null || display === '' ? '—' : display}
            </div>
        );
    } else if (kind === 'number') {
        control = <InputNumber {...common} inputId={id} value={value ?? null} suffix={suffix}
            minFractionDigits={decimal ? 1 : undefined} maxFractionDigits={retainPrecision ? 15 : decimal ? 2 : undefined}
            inputClassName={error ? 'p-invalid' : undefined} onValueChange={(event) => onChange(event.value)} />;
    } else if (kind === 'select' || kind === 'multi') {
        const Select = kind === 'multi' ? MultiSelect : Dropdown;
        control = <Select {...common} inputId={id} value={value} options={options} optionLabel="label" optionValue="value"
            {...(kind === 'multi' && { display: 'chip' })} onChange={(event) => onChange(kind === 'multi' ? event.value || [] : event.value)} />;
    } else {
        const Input = kind === 'area' ? InputTextarea : InputText;
        control = <Input {...common} id={id} value={value ?? ''} readOnly={readOnly}
            {...(kind === 'area' && { rows: 2, autoResize: true })} onChange={(event) => onChange?.(event.target.value)} />;
    }
    const labelClass = heading ? undefined : 'mdc-registration-field-label font-medium';
    const fieldLabel = staticValue ? <span id={id + '-label'} className={labelClass}>{label}</span> : (
        <label htmlFor={id} className={labelClass}>
            {label}{required && <span aria-hidden="true"> *</span>}
        </label>
    );
    return (
        <div className={['field', 'col-12', width].join(' ')}>
            {heading ? <h3 className="mdc-registration-subheading mt-0 mb-2">{fieldLabel}</h3> : fieldLabel}
            {control}
            {(locked?.[name] || (!staticValue && help)) && <small id={id + '-help'} className="block mt-1 text-600">{locked?.[name] || help}</small>}
            {error && <small id={id + '-error'} className="block mt-1 p-error">{error}</small>}
        </div>
    );
}

const nameField = [{ key: 'name', label: 'Name', width: 'md:col-10' }];
const materialFields = [
    { key: 'name', label: 'Material family', width: 'md:col-5' },
    { key: 'grades', label: 'Material grades', width: 'md:col-5', help: 'Separate grades with commas.' }
];
const serviceFields = [
    { key: 'name', label: 'Field name', width: 'md:col-5' },
    { key: 'value', label: 'Field value', width: 'md:col-5' }
];
const technicalFields = [
    { key: 'name', label: 'Parameter', width: 'md:col-3' },
    { key: 'value', label: 'Value', width: 'md:col-3' },
    { key: 'unit', label: 'Unit', width: 'md:col-2' },
    { key: 'notes', label: 'Notes', width: 'md:col-2' }
];

function RepeatableFields({ name, heading, fields, rows, replace, errors, addLabel, disabled, fieldContext }) {
    const readOnly = fieldContext.viewOnly || fieldContext.locked?.[name];
    if (readOnly && !rows.length && !fieldContext.locked?.[name]) return null;
    const addRow = () => replace([...rows, { id: Math.max(0, ...rows.map(({ id }) => id)) + 1 }]);
    return (
        <div className="flex flex-column gap-2 mb-3">
            <h3 className="mdc-registration-subheading m-0">{heading}</h3>
            {fieldContext.locked?.[name] && <small className="text-600">{fieldContext.locked[name]}</small>}
            {errors[name] && <small className="p-error">{errors[name]}</small>}
            {rows.map((row, index) => (
                <div className="grid formgrid align-items-start" key={row.id}>
                    {fields.map(({ key, label, ...options }) => {
                        const field = [name, row.id, key].join('.');
                        return <Field key={key} {...fieldContext} {...options} name={field} label={label} value={row[key]} error={errors[field]} disabled={disabled}
                            onChange={(value) => replace(rows.map((item) => item.id === row.id ? { ...item, [key]: value } : item))} />;
                    })}
                    {!readOnly && <div className="field col-12 md:col-2">
                        <Button label="Remove" type="button" outlined severity="danger" disabled={disabled}
                            aria-label={'Remove ' + heading.toLowerCase() + ' entry ' + (index + 1)}
                            onClick={() => replace(rows.filter(({ id }) => id !== row.id))} />
                    </div>}
                </div>
            ))}
            {!readOnly && <div><Button type="button" outlined icon="pi pi-plus" label={addLabel} disabled={disabled} onClick={addRow} /></div>}
        </div>
    );
}

function Measurements({ ranges, values, prefix, errors, onChange, disabled, fieldContext }) {
    return measurementFields(ranges).map(({ name, ...field }) => {
        const key = prefix + '.' + name;
        return <Field key={key} {...fieldContext} {...field} name={key} kind="number" disabled={disabled} value={values[name]}
            error={errors[key]} onChange={(value) => onChange({ ...values, [name]: value })} />;
    });
}

const textOptions = (values) => values.map((value) => ({ value, label: value }));
const sectionHeading = { title: { role: 'heading', 'aria-level': 2 } };
const subsectionHeading = { title: { role: 'heading', 'aria-level': 3 } };

export default function ProviderRegistrationFields({ form, filters, errors, onChange, disabled,
    serviceCollapsed, setServiceCollapsed, technicalCollapsed, setTechnicalCollapsed,
    mode = 'register', showProvider = true, showOffering = true, readOnly = false, locked, idPrefix,
    providerAction, offeringAction }) {
    const update = mode === 'update';
    const fieldContext = { idPrefix, viewOnly: readOnly, locked, retainPrecision: update };
    const set = (key, value) => onChange({ ...form, [key]: value });
    const field = (name, label, options = {}) => (
        <Field {...fieldContext} name={name} label={label} value={form[name]} onChange={(value) => set(name, value)}
            error={errors[name]} {...options} disabled={disabled || options.disabled} />
    );
    const rows = (name, heading, fields, addLabel) => (
        <RepeatableFields name={name} heading={heading} rows={form[name]} fields={fields}
            replace={(value) => set(name, value)} errors={errors} addLabel={addLabel} disabled={disabled} fieldContext={fieldContext} />
    );
    const family = form.partFamily;
    const partOptions = update ? withSavedOptions(filters?.partTypes[family], Object.keys(form.partTypeStatuses || {}))
        : filters?.partTypes[family] || [];
    const measurementTypes = form.partTypes.filter((type) => update || registrationPartRanges(family, type).length);
    const category = update ? form.serviceCategory : filters?.serviceCategoryByFamily[family] || '';
    const confirmRemoval = (previous, next, options, label) => {
        const removed = selectsRemoval(previous, next);
        return !removed.length || window.confirm('Remove ' + label + ' when you save this offering? '
            + removed.map((value) => catalogueLabel(options, value)).join(', ') + '. Reselect before saving to restore the draft values.');
    };
    const changePartTypes = (value) => {
        if (!update) set('partTypes', value);
        else if (confirmRemoval(form.partTypes, value, partOptions, 'these part types and their specifications')) {
            onChange(retainedPartDraft(form, value));
        }
    };
    const changeTypeStatus = (type, status) => {
        if (status !== 'confirmed' && form.partTypeStatuses[type] === 'confirmed' && (form.hasSavedCapabilities.includes(type)
            || Object.values(form.partMeasurements[type] || {}).some((value) => value != null))
            && !window.confirm('Remove the specifications for ' + catalogueLabel(partOptions, type)
                + ' when you save this offering? Choose Confirmed again before saving to retain them.')) return;
        set('partTypeStatuses', { ...form.partTypeStatuses, [type]: status });
    };
    const familyField = (name, label, options) => (
        <Field {...fieldContext} name={'familyDetails.' + name} label={label} value={form.familyDetails[name]}
            error={errors['familyDetails.' + name]} onChange={(value) => set('familyDetails', { ...form.familyDetails, [name]: value })}
            {...options} disabled={disabled} />
    );

    return (
        <>
            {showProvider && <Panel header="Provider information" className="mdc-registration-section" pt={sectionHeading}>
                <div className="grid formgrid">
                    {field('providerName', 'Provider name', { required: true })}
                    {field('providerId', 'Provider ID', {
                        required: true, viewOnly: readOnly || update,
                        help: 'Start with mdc_stage1b_. Use lowercase letters, digits and single underscores. The ID stays fixed after registration.'
                    })}
                    {field('country', 'Country', { required: true })}
                    {field('description', 'Company description', { kind: 'area', width: '' })}
                    {field('certifications', 'Provider certifications', {
                        kind: 'multi', options: update ? withSavedOptions(filters?.certifications, form.certifications)
                            : filters?.certifications || [], disabled: !filters, width: 'md:col-6'
                    })}
                </div>
                {rows('otherCertifications', 'Other certifications', nameField, 'Add other certification')}
                {providerAction}
            </Panel>}

            {showOffering && <>
            <Panel header="Offering information" className="mdc-registration-section" pt={sectionHeading}>
                <div className="grid formgrid">
                    {field('offeringName', 'Offering name', { required: true, width: 'md:col-6' })}
                    {field('offeringId', 'Offering ID', {
                        required: true, width: 'md:col-6', viewOnly: readOnly || update,
                        help: 'Use the complete provider ID, then an underscore and a lowercase offering suffix. The ID stays fixed after creation.'
                    })}
                    {field('partFamily', 'Part family', {
                        kind: 'select', required: true, options: filters?.partFamilies || [], disabled: !filters, viewOnly: readOnly || update,
                        onChange: (value) => onChange(selectRegistrationFamily(form, value, () => window.confirm(
                            'Changing the part family will clear selected part types and family-specific specifications. Continue?'
                        )))
                    })}
                    {field('serviceCategory', 'Service category', {
                        readOnly: true, viewOnly: mode !== 'register', value: mode === 'register' ? category : catalogueLabel(filters?.serviceCategories, category)
                    })}
                    {update && field('supportStatus', 'Offering support status', { kind: 'select', options: SUPPORT_STATUSES })}
                </div>
                <Panel header="Additional service details" className="mdc-registration-subsection" pt={subsectionHeading}
                    toggleable collapsed={serviceCollapsed}
                    onToggle={(event) => setServiceCollapsed(event.value)}>
                    <div className="grid formgrid">
                        {field('productionMode', 'Production mode', {
                            help: 'Describe typical production repetition or volume.', width: 'md:col-6'
                        })}
                        {field('industriesServed', 'Industries served', {
                            kind: 'area', help: 'Enter one industry per line.', width: 'md:col-6'
                        })}
                        {field('otherServiceInformation', 'Other service information', { kind: 'area', width: '' })}
                    </div>
                    {rows('customOfferingFields', 'Custom service fields', serviceFields, 'Add service field')}
                </Panel>
            </Panel>

            <Panel header="Capability information" className="mdc-registration-section" pt={sectionHeading}>
                {!family ? <p className="m-0 text-600">Select a part family to enter capabilities.</p> : (
                    <>
                        <div className="grid formgrid">
                            {field('partTypes', 'Supported part types', {
                                kind: 'multi', options: partOptions, width: '', heading: true, onChange: changePartTypes, disabled: !filters
                            })}
                        </div>
                        <h3 className="mdc-registration-subheading mt-0 mb-3">Technical specifications</h3>
                        <div className="grid formgrid">
                            <Measurements ranges={FAMILY_RANGES[family] || []} values={form.familyDetails}
                                prefix="familyDetails" errors={errors} disabled={disabled} fieldContext={fieldContext}
                                onChange={(value) => set('familyDetails', value)} />
                            {family === 'gear' && (
                                <>
                                    {familyField('qualityStandard', 'Quality standard', {
                                        kind: 'select', options: textOptions(QUALITY_STANDARDS), width: 'md:col-6'
                                    })}
                                    {familyField('qualityClass', 'Quality class', { width: 'md:col-6' })}
                                </>
                            )}
                            {(family === 'shaft' || family === 'metal_part') && (
                                <>
                                    {familyField('qualityToleranceStandard', 'Quality / tolerance standard', {
                                        width: 'md:col-6', help: 'For example, ISO 286 where applicable.'
                                    })}
                                    {familyField('toleranceClassFit', 'Tolerance class / fit', {
                                        width: 'md:col-6', help: 'For example, h6 for a shaft or H7 for a hole, where applicable.'
                                    })}
                                </>
                            )}
                            {familyField('tolerance', 'Tolerance', { width: 'md:col-6', help: 'For example, 0.05 mm.' })}
                            {familyField('surfaceFinish', 'Surface finish', { width: 'md:col-6', help: 'For example, Ra 1.6 µm.' })}
                            {form.savedSpecifications?.map(({ label, value }, index) => (
                                <Field key={label} {...fieldContext} name={'savedSpecifications.' + index} label={label} value={value} viewOnly />
                            ))}
                        </div>
                        {measurementTypes.map((type) => (
                            <div key={type}>
                                <h4 className="mdc-registration-part-heading mt-0 mb-3">
                                    {catalogueLabel(partOptions, type)}
                                </h4>
                                <div className="grid formgrid">
                                    {update && <Field {...fieldContext} name={'partTypeStatuses.' + type} label="Part type support status"
                                        options={SUPPORT_STATUSES} kind="select" value={form.partTypeStatuses[type]} disabled={disabled}
                                        error={errors['partTypeStatuses.' + type]} onChange={(value) => changeTypeStatus(type, value)} />}
                                    {(!update || form.partTypeStatuses[type] === 'confirmed') && (
                                        <Measurements ranges={registrationPartRanges(family, type)} values={form.partMeasurements[type] || {}}
                                            prefix={'partMeasurements.' + type} errors={errors} disabled={disabled} fieldContext={fieldContext}
                                            onChange={(value) => set('partMeasurements', { ...form.partMeasurements, [type]: value })} />
                                    )}
                                </div>
                                {update && !readOnly && form.partTypeStatuses[type] !== 'confirmed'
                                    && registrationPartRanges(family, type).length > 0 && (
                                    <p className="text-600 mt-0 mb-3">Confirm this part type to publish its specifications.</p>
                                )}
                            </div>
                        ))}

                        <h3 className="mdc-registration-subheading mt-0 mb-3">Materials and grades</h3>
                        <div className="grid formgrid">
                            {field('materials', 'Materials', {
                                kind: 'multi', options: update ? withSavedOptions(filters?.materials, form.materials) : filters?.materials || [],
                                width: 'md:col-6', disabled: !filters, onChange: (value) => {
                                    if (!update) set('materials', value);
                                    else if (confirmRemoval(form.materials, value, filters?.materials, 'these materials and their grades')) {
                                        set('materials', retainSelectionOrder(value, Object.keys(form.materialGrades)));
                                    }
                                }
                            })}
                            {form.materials.map((value) => (
                                <Field key={value} {...fieldContext} name={'materialGrades.' + value}
                                    label={catalogueLabel(filters?.materials, value) + ' grades'}
                                    value={form.materialGrades[value]} kind={update ? 'area' : 'text'}
                                    help={update ? 'Enter one grade per line.' : 'Separate grades with commas.'}
                                    error={errors['materialGrades.' + value]} disabled={disabled}
                                    onChange={(grades) => set('materialGrades', { ...form.materialGrades, [value]: grades })} />
                            ))}
                        </div>
                        {rows('additionalMaterials', 'Other material families', update
                            ? [materialFields[0], { ...materialFields[1], kind: 'area', help: 'Enter one grade per line.' }] : materialFields, 'Add other material')}

                        <div className="grid formgrid">
                            {field('processes', 'Manufacturing processes', {
                                kind: 'multi', options: update ? withSavedOptions(filters?.processes, form.processes) : filters?.processes || [],
                                disabled: !filters, width: '', heading: true
                            })}
                        </div>
                        {rows('additionalProcesses', 'Other manufacturing processes', nameField, 'Add other process')}

                        <h3 className="mdc-registration-subheading mt-0 mb-3">General manufacturing capabilities</h3>
                        <p className="text-600 mt-0">Batch size is the supported customer order quantity for the offering.
                            Lead time is the offering-level delivery range.</p>
                        <div className="grid formgrid">
                            <Measurements ranges={GENERAL_RANGES} values={form.general}
                                prefix="general" errors={errors} disabled={disabled} fieldContext={fieldContext}
                                onChange={(value) => set('general', value)} />
                            {field('capabilityNotes', 'Notes', { kind: 'area', width: '' })}
                        </div>
                        <Panel header="Additional technical capabilities" className="mdc-registration-subsection" pt={subsectionHeading}
                            toggleable collapsed={technicalCollapsed}
                            onToggle={(event) => setTechnicalCollapsed(event.value)}>
                            {rows('customCapabilityFields', 'Technical entries', technicalFields, 'Add technical entry')}
                        </Panel>
                    </>
                )}
            </Panel>
            {offeringAction}
            </>}
        </>
    );
}
