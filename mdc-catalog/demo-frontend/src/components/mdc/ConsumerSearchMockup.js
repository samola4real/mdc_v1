import React, { useEffect, useRef, useState } from 'react';
import { Card } from 'primereact/card';
import { Dropdown } from 'primereact/dropdown';
import { InputText } from 'primereact/inputtext';
import { Message } from 'primereact/message';
import { MultiSelect } from 'primereact/multiselect';
import { useAuth } from '@/layout/context/AuthContext';
import { getCatalogFilters, normalizeCatalogFilters } from '@/services/mdc/catalog.service';
import { searchServiceDiscovery } from '@/services/mdc/search.service';
import {
    availableSearchFamilies,
    buildSearchPayload,
    changePartSelection,
    defaultPartType,
    getSpecificationProfile,
    hasValidPartSelection,
    INVALID_REQUIREMENTS,
    resetSearchForm,
    validateSearchCatalogue
} from './consumerSearchCriteria';
import { validateSearchResponse } from './searchResultFormatters';
import SearchErrorMessage from './SearchErrorMessage';
import SearchResultsList from './SearchResultsList';
import Button from './MaaSAIButton';

const SpecificationField = ({ field, value, error, onChange }) => {
    const { id, label, text, integer, placeholder, hint } = field;
    const hintId = hint ? id + '-hint' : undefined;
    const errorId = error ? id + '-error' : undefined;
    return (
        <div className="mdc-consumer-field">
            <label htmlFor={id}>{label}</label>
            <InputText
                id={id}
                value={value ?? ''}
                inputMode={text ? undefined : integer ? 'numeric' : 'decimal'}
                placeholder={placeholder}
                invalid={Boolean(error)}
                aria-invalid={error ? true : undefined}
                aria-describedby={[hintId, errorId].filter(Boolean).join(' ') || undefined}
                onChange={(event) => onChange(event.target.value)}
            />
            {hint && <small id={hintId} className="mdc-consumer-hint">{hint}</small>}
            {error && <small id={errorId} className="p-error">{error}</small>}
        </div>
    );
};

const catalogueUnavailable = 'Manufacturing options are temporarily unavailable. Please try again.';

const ConsumerSearchMockup = () => {
    const { keycloak } = useAuth();
    const [catalogue, setCatalogue] = useState(null);
    const [catalogueError, setCatalogueError] = useState(null);
    const [catalogueAttempt, setCatalogueAttempt] = useState(0);
    const [form, setForm] = useState(null);
    const [fieldErrors, setFieldErrors] = useState({});
    const [outcome, setOutcome] = useState(null);
    const [loading, setLoading] = useState(false);
    const activeSearch = useRef(null);

    useEffect(() => {
        let active = true;
        getCatalogFilters()
            .then(normalizeCatalogFilters)
            .then(validateSearchCatalogue)
            .then((loaded) => {
                if (!active) return;
                setForm(resetSearchForm(loaded));
                setCatalogue(loaded);
            })
            .catch((error) => {
                if (active) setCatalogueError(error);
            });
        return () => { active = false; };
    }, [catalogueAttempt]);

    useEffect(() => () => { activeSearch.current = null; }, []);

    const changeCriteria = (next) => {
        if (activeSearch.current) activeSearch.current.obsolete = true;
        setOutcome(null);
        setFieldErrors({});
        setForm(next);
    };

    const submit = async (event) => {
        event.preventDefault();
        if (activeSearch.current || !catalogue || !form) return;
        const { payload, errors } = buildSearchPayload(form, catalogue, keycloak?.subject);
        setOutcome(null);
        setFieldErrors(errors || {});
        if (errors) {
            event.currentTarget.elements.namedItem(Object.keys(errors)[0])?.focus();
            return;
        }

        const job = { obsolete: false };
        activeSearch.current = job;
        setLoading(true);
        try {
            const response = validateSearchResponse(await searchServiceDiscovery(payload), payload);
            if (activeSearch.current === job && !job.obsolete) {
                setOutcome({ response, requirements: payload.requirements });
            }
        } catch (error) {
            if (activeSearch.current === job && !job.obsolete) setOutcome({ error });
        } finally {
            if (activeSearch.current === job) {
                activeSearch.current = null;
                setLoading(false);
            }
        }
    };

    const validSelection = Boolean(form && catalogue && hasValidPartSelection(form, catalogue));
    const profile = validSelection ? getSpecificationProfile(form.partFamily, form.partType) : null;
    const selectOptions = { optionLabel: 'label', optionValue: 'value' };
    const partTypes = catalogue?.partTypes[form?.partFamily] || [];

    return (
        <>
            <Card className="mdc-consumer-requirements">
                <h2>Manufacturing Requirements</h2>
                <p>Select a part family and part type. Complete any additional requirements relevant to your product.</p>
                {catalogueError ? (
                    <div className="flex flex-wrap align-items-center gap-2 mt-3">
                        <SearchErrorMessage error={catalogueError} fallback={catalogueUnavailable} />
                        <Button
                            label="Retry"
                            icon="pi pi-refresh"
                            outlined
                            onClick={() => {
                                setCatalogueError(null);
                                setCatalogueAttempt((attempt) => attempt + 1);
                            }}
                        />
                    </div>
                ) : !catalogue && (
                    <Message severity="info" className="mt-3 w-full justify-content-start" text="Loading manufacturing options..." />
                )}

                <form onSubmit={submit} className="mdc-consumer-form" noValidate>
                    <div className="mdc-consumer-grid mdc-consumer-selection">
                        <div className="mdc-consumer-field">
                            <label htmlFor="partFamily">Part family <span aria-hidden="true">*</span></label>
                            <Dropdown
                                {...selectOptions}
                                inputId="partFamily"
                                value={form?.partFamily}
                                options={catalogue ? availableSearchFamilies(catalogue) : []}
                                placeholder="Select a part family"
                                disabled={!catalogue}
                                required
                                onChange={({ value }) => changeCriteria(changePartSelection(form, value, defaultPartType(catalogue, value)))}
                            />
                        </div>
                        <div className="mdc-consumer-field">
                            <label htmlFor="partType">Part type <span aria-hidden="true">*</span></label>
                            <Dropdown
                                {...selectOptions}
                                inputId="partType"
                                value={form?.partType}
                                options={partTypes}
                                placeholder="Select a part type"
                                disabled={!partTypes.length}
                                required
                                onChange={({ value }) => changeCriteria(changePartSelection(form, form.partFamily, value))}
                            />
                        </div>
                    </div>

                    <section className="mdc-consumer-manufacturing" aria-labelledby="material-requirements">
                        <h3 id="material-requirements">Material and Manufacturing Requirements</h3>
                        <div className="mdc-consumer-grid">
                            <div className="mdc-consumer-field">
                                <label htmlFor="material">Material</label>
                                <Dropdown
                                    {...selectOptions}
                                    inputId="material"
                                    value={form?.material}
                                    options={catalogue?.materials || []}
                                    placeholder="Select a material"
                                    showClear
                                    disabled={!catalogue}
                                    onChange={({ value }) => changeCriteria({ ...form, material: value })}
                                />
                            </div>
                            <div className="mdc-consumer-field">
                                <label htmlFor="processes">Manufacturing processes</label>
                                <MultiSelect
                                    {...selectOptions}
                                    inputId="processes"
                                    value={form?.processes || []}
                                    options={catalogue?.processes || []}
                                    placeholder="Select manufacturing processes"
                                    showClear
                                    maxSelectedLabels={2}
                                    selectedItemsLabel="{0} processes selected"
                                    disabled={!catalogue}
                                    onChange={({ value }) => changeCriteria({ ...form, processes: value || [] })}
                                />
                            </div>
                            <div className="mdc-consumer-field">
                                <label htmlFor="certifications">Certifications</label>
                                <MultiSelect
                                    {...selectOptions}
                                    inputId="certifications"
                                    value={form?.certifications || []}
                                    options={catalogue?.certifications || []}
                                    placeholder="Select certifications"
                                    filter
                                    filterPlaceholder="Search certifications"
                                    resetFilterOnHide
                                    showSelectAll={false}
                                    display="chip"
                                    showClear
                                    disabled={!catalogue}
                                    className="mdc-consumer-certifications"
                                    onChange={({ value }) => changeCriteria({ ...form, certifications: value || [] })}
                                />
                            </div>
                        </div>
                    </section>

                    {profile && (
                        <section className="mdc-consumer-specifications" aria-labelledby="part-specifications">
                            <h3 id="part-specifications"><i className="pi pi-sliders-h" aria-hidden="true" /> {profile.title}</h3>
                            <div className="mdc-consumer-specifications-body">
                                <p>Complete only the specifications required for your product. Leave unspecified fields blank.</p>
                                <div className="mdc-consumer-grid">
                                    {profile.fields.map((field) => (
                                        <SpecificationField
                                            key={field.id}
                                            field={field}
                                            value={form.specifications[field.id]}
                                            error={fieldErrors[field.id]}
                                            onChange={(value) => changeCriteria({
                                                ...form, specifications: { ...form.specifications, [field.id]: value }
                                            })}
                                        />
                                    ))}
                                </div>
                            </div>
                        </section>
                    )}

                    {Object.keys(fieldErrors).length > 0 && (
                        <Message severity="warn" className="w-full justify-content-start" text={INVALID_REQUIREMENTS} />
                    )}
                    <div className="mdc-consumer-actions">
                        <Button
                            type="submit"
                            label="Find Manufacturing Services"
                            icon="pi pi-search"
                            loading={loading}
                            disabled={loading || !validSelection}
                        />
                        <Button type="button" label="Reset" outlined disabled={!catalogue} onClick={() => changeCriteria(resetSearchForm(catalogue))} />
                        {loading && <span role="status">Finding eligible manufacturing services...</span>}
                    </div>
                </form>
            </Card>

            <SearchErrorMessage error={outcome?.error} />
            <SearchResultsList response={outcome?.response} catalogue={catalogue} requirements={outcome?.requirements} />
        </>
    );
};

export { buildSearchPayload } from './consumerSearchCriteria';
export default ConsumerSearchMockup;
