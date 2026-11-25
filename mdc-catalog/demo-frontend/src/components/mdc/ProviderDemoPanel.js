import React, { useEffect, useRef, useState } from 'react';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { Column } from 'primereact/column';
import { DataTable } from 'primereact/datatable';
import { Dropdown } from 'primereact/dropdown';
import { InputNumber } from 'primereact/inputnumber';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Message } from 'primereact/message';
import { MultiSelect } from 'primereact/multiselect';
import { Panel } from 'primereact/panel';
import { Toast } from 'primereact/toast';
import { getCatalogFilters, normalizeCatalogFilters } from '@/services/mdc/catalog.service';
import {
    createOffering, deleteOffering, deleteProvider, getOffering, getProvider, listProviderOfferings,
    updateOffering, updateProvider
} from '@/services/mdc/provider.service';
import { DISPOSABLE_PROVIDER_PREFIX, isDisposableMdcId, isDisposableOfferingId } from '@/services/mdc/stage1bScope';
import ProviderActionResult from './ProviderActionResult';
import ProviderPayloadPreview from './ProviderPayloadPreview';
import ProviderRegistration, { RegistrationOutcome } from './ProviderRegistration';
import StatusTag from './StatusTag';
import {
    BOX_PART_TYPES, ROUND_PART_TYPES, buildOfferingCreation, buildProviderPatches,
    emptyProviderForm, hydrateProviderForm
} from './providerPayloadBuilder';
import {
    QUALITY_STANDARDS as qualityStandards, SUPPORT_STATUSES as supportStatuses, emptyRegistrationForm, hasRegistrationDraft
} from './providerRegistrationPayload';
import { readBackRegistration } from './providerRegistrationFlow';

const textArea = { rows: 3, autoResize: true, className: 'w-full' };
const providerInputs = ['providerName', 'country', 'description', 'certifications'];
const strong = (etag) => /^"[^"\r\n]+"$/.test(etag || '');
const listBody = (field) => (row) => (row[field] || []).join(', ');

const displayRows = (rows, provider) => rows.map((offering) => ({
    id: offering.offering_id,
    providerName: provider.provider_name,
    offering: offering.offering_name,
    serviceCategory: offering.service_category,
    partFamily: offering.part_family,
    supportedPartTypes: (offering.supported_part_types || []).map((item) => item.part_type),
    materials: (offering.generic_capabilities?.materials || []).map((item) => item.material),
    processes: (offering.generic_capabilities?.processes || []).map((item) => item.process),
    status: offering.support_status
}));

const ProviderDemoPanel = () => {
    const toast = useRef(null);
    const inFlight = useRef(false);
    const [mode, setMode] = useState('register');
    const [registrationForm, setRegistrationForm] = useState(emptyRegistrationForm);
    const [registrationBusy, setRegistrationBusy] = useState(false);
    const [registrationOutcome, setRegistrationOutcome] = useState(null);
    const [form, setForm] = useState(emptyProviderForm);
    const [filters, setFilters] = useState(null);
    const [filterError, setFilterError] = useState(null);
    const [catalogueAttempt, setCatalogueAttempt] = useState(0);
    const [lookupId, setLookupId] = useState('');
    const [snapshot, setSnapshot] = useState(null);
    const [loadingAction, setLoadingAction] = useState(null);
    const [actionResult, setActionResult] = useState(null);
    const [stateLoadWarning, setStateLoadWarning] = useState(null);
    const provider = snapshot?.provider.data;
    const offering = snapshot?.offering?.data;
    const rows = provider ? displayRows(snapshot.list.offerings, provider) : [];
    const selectedRow = rows.find((item) => item.id === offering?.offering_id);
    const patches = buildProviderPatches(form, provider, offering);
    const payload = mode === 'add' ? buildOfferingCreation(form) : patches;
    const manageable = isDisposableMdcId(provider?.provider_id);
    const providerEtag = strong(snapshot?.provider.etag);
    const offeringEtag = strong(snapshot?.offering?.etag);
    const editing = mode === 'update';
    const busy = Boolean(loadingAction) || registrationBusy;
    const currentType = form.partTypes.length === 1 ? form.partTypes[0] : null;
    const boxEnabled = BOX_PART_TYPES.includes(currentType);
    const roundEnabled = ROUND_PART_TYPES.includes(currentType);
    const creationReady = Boolean(filters && form.offeringName.trim() && form.partFamily && form.serviceCategory
        && isDisposableOfferingId(form.offeringId.trim(), form.providerId.trim()));

    useEffect(() => {
        let active = true;
        getCatalogFilters().then(normalizeCatalogFilters)
            .then((data) => { if (active) setFilters(data); })
            .catch((error) => { if (active) setFilterError(error.message); });
        return () => { active = false; };
    }, [catalogueAttempt]);

    const retryCatalogue = () => {
        setFilterError(null);
        setCatalogueAttempt((attempt) => attempt + 1);
    };

    const setField = (field, value) => setForm((current) => ({ ...current, [field]: value }));

    const addRow = (field, row) => setForm((current) => ({ ...current, [field]: [...current[field], row] }));
    const editRow = (field, index, key, value) => setForm((current) => ({
        ...current, [field]: current[field].map((row, offset) => offset === index ? { ...row, [key]: value } : row)
    }));
    const removeRow = (field, index) => setForm((current) => ({
        ...current, [field]: current[field].filter((_, offset) => offset !== index)
    }));
    const addCustomOfferingField = () => addRow('customOfferingFields', { name: '', value: '', unit: '', notes: '' });
    const updateCustomOfferingField = (...args) => editRow('customOfferingFields', ...args);
    const removeCustomOfferingField = (index) => removeRow('customOfferingFields', index);
    const addCustomCapabilityField = () => addRow('customCapabilityFields', { name: '', value: '', unit: '', notes: '' });
    const updateCustomCapabilityField = (...args) => editRow('customCapabilityFields', ...args);
    const removeCustomCapabilityField = (index) => removeRow('customCapabilityFields', index);

    const refresh = async (id, selectedId, preservedEntity) => {
        const [providerResponse, list] = await Promise.all([getProvider(id), listProviderOfferings(id)]);
        const preferred = list.offerings.find((item) => item.offering_id === selectedId) || list.offerings[0];
        const offeringResponse = preferred ? await getOffering(preferred.offering_id) : null;
        const fresh = hydrateProviderForm(providerResponse.data, offeringResponse?.data);
        if (preservedEntity && provider) {
            const previous = hydrateProviderForm(provider, offering);
            for (const key of Object.keys(fresh)) {
                if (providerInputs.includes(key) !== (preservedEntity === 'provider')) continue;
                if (JSON.stringify(form[key]) !== JSON.stringify(previous[key])) fresh[key] = form[key];
            }
        }
        setSnapshot({ provider: providerResponse, offering: offeringResponse, list });
        setForm(fresh);
        setLookupId(id);
    };

    const runAction = async (action, operation, inspect, { keepReceipt = false } = {}) => {
        if (inFlight.current) return;
        inFlight.current = true;
        setLoadingAction(action);
        setActionResult(null);
        if (!keepReceipt) setRegistrationOutcome(null);
        setStateLoadWarning(null);
        let response;
        let error;
        try {
            try {
                response = await operation();
            } catch (failure) {
                error = failure;
            }
            if (!keepReceipt || error) setActionResult({ action, response: response?.data || response, error });
            if (error) {
                toast.current?.show({ severity: 'warn', summary: action, detail: error.message, life: 3500 });
            }
            if (inspect && (!error || error.status == null || [404, 409, 412, 428].includes(error.status) || error.status >= 500)) {
                try {
                    await inspect(error);
                } catch (failure) {
                    setSnapshot(null);
                    setStateLoadWarning(failure.status === 404
                        ? 'The provider is absent. Confirm the intended identity before another write.'
                        : 'The resource could not be read back. Load its current state before another write.');
                }
            }
        } finally {
            inFlight.current = false;
            setLoadingAction(null);
        }
    };

    const inspectWrite = (id, selectedId, preservedEntity) => async () => {
        setMode('update');
        setLookupId(id);
        await refresh(id, selectedId, preservedEntity);
    };

    const acceptRegistration = (result) => {
        const loaded = result.readBack.kind === 'matching' ? result.readBack.snapshot : null;
        setMode('update');
        setLookupId(result.identity.providerId);
        setSnapshot(loaded);
        setForm(loaded ? hydrateProviderForm(loaded.provider.data, loaded.offering.data) : emptyProviderForm());
        setRegistrationForm(emptyRegistrationForm());
        setRegistrationOutcome(result);
        setActionResult(null);
        setStateLoadWarning(null);
    };

    const loadProvider = () => {
        const id = lookupId.trim();
        setSnapshot(null);
        setForm(emptyProviderForm());
        if (registrationOutcome?.identity.providerId === id && registrationOutcome.readBack.kind !== 'matching') {
            runAction('Load provider', async () => {
                const readBack = await readBackRegistration(registrationOutcome.identity, { getProvider, listProviderOfferings, getOffering });
                acceptRegistration({ ...registrationOutcome, readBack });
            }, undefined, { keepReceipt: true });
            return;
        }
        runAction('Load provider', () => refresh(id));
    };

    const switchMode = (nextMode) => {
        if (mode === 'register') {
            if (nextMode === 'register') return;
            if (hasRegistrationDraft(registrationForm) && !window.confirm('Discard this registration draft?')) return;
        }
        setMode(nextMode);
        setRegistrationForm(emptyRegistrationForm());
        setRegistrationOutcome(null);
        setActionResult(null);
        setStateLoadWarning(null);
        setSnapshot(null);
        setForm(emptyProviderForm());
    };

    const startOffering = () => {
        setMode('add');
        setActionResult(null);
        setRegistrationOutcome(null);
        setForm({
            ...hydrateProviderForm(provider),
            partFamily: offering?.part_family || '',
            serviceCategory: offering?.service_category || ''
        });
    };

    const handleSelection = (event) => {
        if (!event.value || event.value.id === offering?.offering_id) return;
        const id = event.value.id;
        runAction('Load offering', async () => {
            const next = await getOffering(id);
            setSnapshot((current) => ({ ...current, offering: next }));
            setForm((current) => {
                const draft = hydrateProviderForm(provider, next.data);
                for (const key of providerInputs) draft[key] = current[key];
                return draft;
            });
        });
    };

    const removeRecord = (entity) => {
        const isProvider = entity === 'provider';
        const id = isProvider ? provider.provider_id : offering.offering_id;
        if (!window.confirm('Delete disposable ' + entity + ' ' + id + '?')) return;
        const execute = isProvider
            ? () => deleteProvider(id, snapshot.provider.etag)
            : () => deleteOffering(id, snapshot.offering.etag);
        runAction('Delete ' + entity, execute, async (error) => {
            if (!error && isProvider) {
                setSnapshot(null);
                setForm(emptyProviderForm());
                return;
            }
            await refresh(provider.provider_id, id);
        });
    };

    const renderProviderInformation = () => (
        <Panel header="Provider information">
            <div className="grid formgrid">
                <div className="field col-12 md:col-4">
                    <label htmlFor="providerName" className="font-medium">Provider name</label>
                    <InputText id="providerName" value={form.providerName} onChange={(e) => setField('providerName', e.target.value)} className="w-full" />
                </div>
                <div className="field col-12 md:col-4">
                    <label htmlFor="providerId" className="font-medium">Provider ID</label>
                    <InputText id="providerId" value={form.providerId} readOnly={mode !== 'register'} onChange={(e) => setField('providerId', e.target.value)} className="w-full" />
                </div>
                <div className="field col-12 md:col-4">
                    <label htmlFor="country" className="font-medium">Country</label>
                    <InputText id="country" value={form.country} onChange={(e) => setField('country', e.target.value)} className="w-full" />
                </div>
                <div className="field col-12">
                    <label htmlFor="description" className="font-medium">Short description / notes</label>
                    <InputTextarea id="description" value={form.description} onChange={(e) => setField('description', e.target.value)} {...textArea} />
                </div>
                <div className="field col-12 md:col-4">
                    <label htmlFor="certifications" className="font-medium">Provider certifications</label>
                    <MultiSelect inputId="certifications" value={form.certifications} options={filters?.certifications || []} optionLabel="label" optionValue="value" onChange={(e) => setField('certifications', e.value)} display="chip" className="w-full" />
                </div>
            </div>
        </Panel>
    );

    const renderOfferingInformation = () => (
        <Panel header="Offering information">
            <div className="grid formgrid">
                <div className="field col-12 md:col-6">
                    <label htmlFor="offeringName" className="font-medium">Offering name</label>
                    <InputText id="offeringName" value={form.offeringName} onChange={(e) => setField('offeringName', e.target.value)} className="w-full" />
                </div>
                <div className="field col-12 md:col-6">
                    <label htmlFor="offeringId" className="font-medium">Offering ID</label>
                    <InputText id="offeringId" value={form.offeringId} readOnly={mode === 'update'} onChange={(e) => setField('offeringId', e.target.value)} className="w-full" />
                </div>
                <div className="field col-12 md:col-4">
                    <label htmlFor="serviceCategory" className="font-medium">Service category</label>
                    <InputText id="serviceCategory" value={form.serviceCategory} readOnly className="w-full" />
                </div>
                <div className="field col-12 md:col-4">
                    <label htmlFor="partFamily" className="font-medium">Part family</label>
                    <Dropdown inputId="partFamily" value={form.partFamily} options={filters?.partFamilies || []}
                        optionLabel="label" optionValue="value" disabled={mode === 'update' || !filters}
                        onChange={(event) => setForm((current) => ({
                            ...current, partFamily: event.value, serviceCategory: filters.serviceCategoryByFamily[event.value], partTypes: []
                        }))} className="w-full" />
                </div>
                <div className="field col-12 md:col-4">
                    <label htmlFor="supportStatus" className="font-medium">Support status</label>
                    <Dropdown inputId="supportStatus" value={form.supportStatus} options={supportStatuses}
                        optionLabel="label" optionValue="value" onChange={(event) => setField('supportStatus', event.value)}
                        className="w-full" />
                </div>
            </div>
        </Panel>
    );

    const renderAdditionalOfferingInformation = () => (
        <Panel header="Additional offering information">
            <div className="flex flex-column gap-3">
                {(form.customOfferingFields || []).map((field, index) => (
                    <div className="grid formgrid align-items-end" key={`offering-field-${index}`}>
                        <div className="field col-12 md:col-5">
                            <label htmlFor={`customOfferingName${index}`} className="font-medium">Field name</label>
                            <InputText
                                id={`customOfferingName${index}`}
                                value={field.name}
                                onChange={(e) => updateCustomOfferingField(index, 'name', e.target.value)}
                                className="w-full"
                            />
                        </div>
                        <div className="field col-12 md:col-5">
                            <label htmlFor={`customOfferingValue${index}`} className="font-medium">Field value</label>
                            <InputText
                                id={`customOfferingValue${index}`}
                                value={field.value}
                                onChange={(e) => updateCustomOfferingField(index, 'value', e.target.value)}
                                className="w-full"
                            />
                        </div>
                        <div className="field col-12 md:col-2">
                            <Button
                                label="Remove"
                                icon="pi pi-trash"
                                type="button"
                                severity="danger"
                                outlined
                                className="w-full"
                                onClick={() => removeCustomOfferingField(index)}
                            />
                        </div>
                    </div>
                ))}
                <div>
                    <Button
                        label="Add field"
                        icon="pi pi-plus"
                        type="button"
                        outlined
                        onClick={addCustomOfferingField}
                    />
                </div>
            </div>
        </Panel>
    );

    const renderSharedCapabilityFields = () => (
        <>
            <div className="field col-12 md:col-4">
                <label htmlFor="materials" className="font-medium">Materials</label>
                <MultiSelect inputId="materials" value={form.materials} options={filters?.materials || []} optionLabel="label" optionValue="value" onChange={(e) => setForm((current) => ({
                    ...current, materials: e.value,
                    availableGrades: e.value.length === 1 && current.materials.length === 1
                        && current.materials[0] === e.value[0] ? current.availableGrades : ''
                }))} display="chip" className="w-full" />
            </div>
            <div className="field col-12 md:col-4">
                <label htmlFor="availableGrades" className="font-medium">Material grades</label>
                <InputText id="availableGrades" value={form.availableGrades} onChange={(e) => setField('availableGrades', e.target.value)} disabled={form.materials.length !== 1} placeholder="Comma-separated grades" className="w-full" />
            </div>

            <div className="field col-12">
                <label htmlFor="processes" className="font-medium">Processes</label>
                <MultiSelect inputId="processes" value={form.processes} options={filters?.processes || []} optionLabel="label" optionValue="value" onChange={(e) => setField('processes', e.value)} display="chip" className="w-full" />
            </div>
            <div className="field col-12 md:col-3">
                <label htmlFor="batchSizeMin" className="font-medium">Batch size min</label>
                <InputNumber inputId="batchSizeMin" value={form.batchSizeMin} onValueChange={(e) => setField('batchSizeMin', e.value)} className="w-full" />
            </div>
            <div className="field col-12 md:col-3">
                <label htmlFor="batchSizeMax" className="font-medium">Batch size max</label>
                <InputNumber inputId="batchSizeMax" value={form.batchSizeMax} onValueChange={(e) => setField('batchSizeMax', e.value)} className="w-full" />
            </div>
            <div className="field col-12 md:col-3">
                <label htmlFor="leadTimeMinWeeks" className="font-medium">Lead time min weeks</label>
                <InputNumber inputId="leadTimeMinWeeks" value={form.leadTimeMinWeeks} onValueChange={(e) => setField('leadTimeMinWeeks', e.value)} className="w-full" />
            </div>
            <div className="field col-12 md:col-3">
                <label htmlFor="leadTimeMaxWeeks" className="font-medium">Lead time max weeks</label>
                <InputNumber inputId="leadTimeMaxWeeks" value={form.leadTimeMaxWeeks} onValueChange={(e) => setField('leadTimeMaxWeeks', e.value)} className="w-full" />
            </div>
            <div className="field col-12 md:col-4">
                <label htmlFor="weightMaxKg" className="font-medium">Weight max</label>
                <InputNumber inputId="weightMaxKg" value={form.weightMaxKg} onValueChange={(e) => setField('weightMaxKg', e.value)} suffix=" kg" className="w-full" />
            </div>
            <div className="field col-12">
                <label htmlFor="capabilityNotes" className="font-medium">Notes</label>
                <InputTextarea id="capabilityNotes" value={form.capabilityNotes} onChange={(e) => setField('capabilityNotes', e.target.value)} {...textArea} />
            </div>
        </>
    );

    const renderGearFields = () => (
        <>
            <div className="field col-12">
                <label htmlFor="gearPartTypes" className="font-medium">Supported gear part types</label>
                <MultiSelect inputId="gearPartTypes" value={form.partTypes} options={filters?.partTypes.gear || []} optionLabel="label" optionValue="value" onChange={(e) => setField('partTypes', e.value)} display="chip" className="w-full" />
            </div>
            <div className="field col-12 md:col-3">
                <label htmlFor="moduleMin" className="font-medium">Module min</label>
                <InputNumber inputId="moduleMin" value={form.moduleMin} onValueChange={(e) => setField('moduleMin', e.value)} minFractionDigits={1} maxFractionDigits={2} className="w-full" />
            </div>
            <div className="field col-12 md:col-3">
                <label htmlFor="moduleMax" className="font-medium">Module max</label>
                <InputNumber inputId="moduleMax" value={form.moduleMax} onValueChange={(e) => setField('moduleMax', e.value)} minFractionDigits={1} maxFractionDigits={2} className="w-full" />
            </div>
            <div className="field col-12 md:col-3">
                <label htmlFor="diameterMinMm" className="font-medium">Diameter min</label>
                <InputNumber inputId="diameterMinMm" value={form.diameterMinMm} onValueChange={(e) => setField('diameterMinMm', e.value)} suffix=" mm" className="w-full" />
            </div>
            <div className="field col-12 md:col-3">
                <label htmlFor="diameterMaxMm" className="font-medium">Diameter max</label>
                <InputNumber inputId="diameterMaxMm" value={form.diameterMaxMm} onValueChange={(e) => setField('diameterMaxMm', e.value)} suffix=" mm" className="w-full" />
            </div>
            <div className="field col-12 md:col-6">
                <label htmlFor="qualityStandard" className="font-medium">Quality standard/class</label>
                <Dropdown inputId="qualityStandard" value={form.qualityStandard} options={qualityStandards} onChange={(e) => setField('qualityStandard', e.value)} className="w-full" />
            </div>
            <div className="field col-12 md:col-6">
                <label htmlFor="qualityClass" className="font-medium">Quality class</label>
                <InputText id="qualityClass" value={form.qualityClass} onChange={(e) => setField('qualityClass', e.target.value)} className="w-full" />
            </div>
        </>
    );

    const renderShaftFields = () => (
        <>
            <div className="field col-12">
                <label htmlFor="shaftPartTypes" className="font-medium">Supported shaft part types</label>
                <MultiSelect inputId="shaftPartTypes" value={form.partTypes} options={filters?.partTypes.shaft || []} optionLabel="label" optionValue="value" onChange={(e) => setField('partTypes', e.value)} display="chip" className="w-full" />
            </div>
            <div className="field col-12 md:col-3">
                <label htmlFor="lengthMaxMm" className="font-medium">Length max</label>
                <InputNumber inputId="lengthMaxMm" value={form.lengthMaxMm} onValueChange={(e) => setField('lengthMaxMm', e.value)} suffix=" mm" className="w-full" />
            </div>
            <div className="field col-12 md:col-3">
                <label htmlFor="outerDiameterMinMm" className="font-medium">Outer diameter min</label>
                <InputNumber inputId="outerDiameterMinMm" value={form.outerDiameterMinMm} onValueChange={(e) => setField('outerDiameterMinMm', e.value)} suffix=" mm" className="w-full" />
            </div>
            <div className="field col-12 md:col-3">
                <label htmlFor="outerDiameterMaxMm" className="font-medium">Outer diameter max</label>
                <InputNumber inputId="outerDiameterMaxMm" value={form.outerDiameterMaxMm} onValueChange={(e) => setField('outerDiameterMaxMm', e.value)} suffix=" mm" className="w-full" />
            </div>
            {form.partTypes.includes('splined_shaft') && (
                <div className="field col-12 md:col-3">
                    <label htmlFor="splineModule" className="font-medium">Spline module</label>
                    <InputNumber inputId="splineModule" value={form.splineModule} onValueChange={(e) => setField('splineModule', e.value)} minFractionDigits={1} maxFractionDigits={2} className="w-full" />
                </div>
            )}
        </>
    );

    const renderMetalPartFields = () => (
        <>
            <div className="field col-12">
                <label htmlFor="metalPartTypes" className="font-medium">Supported metal part types</label>
                <MultiSelect inputId="metalPartTypes" value={form.partTypes} options={filters?.partTypes.metal_part || []} optionLabel="label" optionValue="value" onChange={(e) => setField('partTypes', e.value)} display="chip" className="w-full" />
            </div>
            {boxEnabled && (
                <div className="field col-12 md:col-3">
                    <label htmlFor="maxLengthMm" className="font-medium">Maximum length</label>
                    <InputNumber inputId="maxLengthMm" value={form.maxLengthMm} onValueChange={(e) => setField('maxLengthMm', e.value)} suffix=" mm" className="w-full" />
                </div>
            )}
            {boxEnabled && (
                <div className="field col-12 md:col-3">
                    <label htmlFor="maxWidthMm" className="font-medium">Maximum width</label>
                    <InputNumber inputId="maxWidthMm" value={form.maxWidthMm} onValueChange={(e) => setField('maxWidthMm', e.value)} suffix=" mm" className="w-full" />
                </div>
            )}
            {boxEnabled && (
                <div className="field col-12 md:col-3">
                    <label htmlFor="maxHeightMm" className="font-medium">Maximum height/thickness</label>
                    <InputNumber inputId="maxHeightMm" value={form.maxHeightMm} onValueChange={(e) => setField('maxHeightMm', e.value)} suffix=" mm" className="w-full" />
                </div>
            )}
            {roundEnabled && (
                <div className="field col-12 md:col-3">
                    <label htmlFor="maxDiameterMm" className="font-medium">Maximum diameter</label>
                    <InputNumber inputId="maxDiameterMm" value={form.maxDiameterMm} onValueChange={(e) => setField('maxDiameterMm', e.value)} suffix=" mm" className="w-full" />
                </div>
            )}
            <div className="field col-12 md:col-6">
                <label htmlFor="tolerance" className="font-medium">Tolerance</label>
                <InputText id="tolerance" value={form.tolerance} onChange={(e) => setField('tolerance', e.target.value)} className="w-full" />
            </div>
            <div className="field col-12 md:col-6">
                <label htmlFor="surfaceFinish" className="font-medium">Surface finish</label>
                <InputText id="surfaceFinish" value={form.surfaceFinish} onChange={(e) => setField('surfaceFinish', e.target.value)} className="w-full" />
            </div>
        </>
    );

    const renderTemplateFields = () => {
        if (form.partFamily === 'shaft') return renderShaftFields();
        if (form.partFamily === 'metal_part') return renderMetalPartFields();
        if (form.partFamily === 'gear') return renderGearFields();
        return null;
    };

    const renderCapabilityInformation = () => (
        <Panel header="Capability information">
            <div className="grid formgrid">
                {renderTemplateFields()}
                {renderSharedCapabilityFields()}
            </div>
            <div className="flex flex-column gap-3">
                    {(form.customCapabilityFields || []).map((field, index) => (
                        <div className="grid formgrid align-items-end" key={`capability-field-${index}`}>
                            <div className="field col-12 md:col-3">
                                <label htmlFor={`customCapabilityName${index}`} className="font-medium">Field name</label>
                                <InputText
                                    id={`customCapabilityName${index}`}
                                    value={field.name}
                                    onChange={(e) => updateCustomCapabilityField(index, 'name', e.target.value)}
                                    className="w-full"
                                />
                            </div>
                            <div className="field col-12 md:col-3">
                                <label htmlFor={`customCapabilityValue${index}`} className="font-medium">Value</label>
                                <InputText
                                    id={`customCapabilityValue${index}`}
                                    value={field.value}
                                    onChange={(e) => updateCustomCapabilityField(index, 'value', e.target.value)}
                                    className="w-full"
                                />
                            </div>
                            <div className="field col-12 md:col-2">
                                <label htmlFor={`customCapabilityUnit${index}`} className="font-medium">Unit</label>
                                <InputText
                                    id={`customCapabilityUnit${index}`}
                                    value={field.unit}
                                    onChange={(e) => updateCustomCapabilityField(index, 'unit', e.target.value)}
                                    className="w-full"
                                />
                            </div>
                            <div className="field col-12 md:col-2">
                                <label htmlFor={`customCapabilityNotes${index}`} className="font-medium">Notes</label>
                                <InputText
                                    id={`customCapabilityNotes${index}`}
                                    value={field.notes}
                                    onChange={(e) => updateCustomCapabilityField(index, 'notes', e.target.value)}
                                    className="w-full"
                                />
                            </div>
                            <div className="field col-12 md:col-2">
                                <Button
                                    label="Remove"
                                    icon="pi pi-trash"
                                    type="button"
                                    severity="danger"
                                    outlined
                                    className="w-full"
                                    onClick={() => removeCustomCapabilityField(index)}
                                />
                            </div>
                        </div>
                    ))}
                    <div>
                        <Button
                            label="Add capability field"
                            icon="pi pi-plus"
                            type="button"
                            outlined
                            onClick={addCustomCapabilityField}
                        />
                    </div>
            </div>
        </Panel>
    );

    const renderUpdateMode = () => (
        <>
            <Card title="Update Existing Provider">
                <div className="flex flex-wrap align-items-end gap-2 mb-3">
                    <div className="flex flex-column gap-2">
                        <label htmlFor="providerLookup" className="font-medium">Provider ID to look up</label>
                        <InputText id="providerLookup" value={lookupId} disabled={busy} onChange={(event) => setLookupId(event.target.value)} />
                    </div>
                    <Button label="Load provider" icon="pi pi-search" outlined disabled={busy || !lookupId.trim()}
                    onClick={loadProvider} />
                    {manageable && <Button label="Add offering" icon="pi pi-plus" outlined disabled={busy || !filters} onClick={startOffering} />}
                </div>
                {provider && !manageable && <Message severity="info" text="This provider is read-only in the Stage 1B demo." className="w-full mb-3" />}
                <DataTable value={rows} dataKey="id" paginator={rows.length > 3} rows={3}
                    selectionMode={busy ? undefined : 'single'} selection={selectedRow} onSelectionChange={handleSelection}
                    responsiveLayout="scroll" stripedRows emptyMessage="No offerings loaded">
                    <Column field="providerName" header="Provider" sortable />
                    <Column field="offering" header="Offering" sortable />
                    <Column field="serviceCategory" header="Service category" sortable />
                    <Column field="partFamily" header="Part family" sortable />
                    <Column header="Supported part types" body={listBody('supportedPartTypes')} />
                    <Column header="Materials" body={listBody('materials')} />
                    <Column header="Processes" body={listBody('processes')} />
                    <Column header="Status" body={(row) => <StatusTag value={row.status} status={row.status} />} />
                </DataTable>
            </Card>
            {provider && renderProviderInformation()}
            {offering && renderOfferingInformation()}
            {offering && renderAdditionalOfferingInformation()}
            {offering && renderCapabilityInformation()}
        </>
    );

    return (
        <div className="flex flex-column gap-4">
            <Toast ref={toast} />
            <Message severity="info" text={'Provider and offering writes are limited to disposable IDs starting with ' + DISPOSABLE_PROVIDER_PREFIX + '.'}
                className="w-full justify-content-start" />
            {mode !== 'register' && filterError && <Message severity="error" text={'Current catalogue filters are unavailable. ' + filterError} className="w-full" />}
            {stateLoadWarning && <Message severity="warn" text={stateLoadWarning} className="w-full" />}
            <div className="flex flex-wrap gap-2">
                <Button label="Register New Provider" icon="pi pi-plus" outlined={mode !== 'register'}
                    disabled={busy} onClick={() => switchMode('register')} />
                <Button label="Update Existing Provider" icon="pi pi-pencil" outlined={!editing}
                    disabled={busy} onClick={() => switchMode('update')} />
            </div>
            {mode === 'register' ? (
                <ProviderRegistration form={registrationForm} onChange={setRegistrationForm} filters={filters}
                    filterError={filterError} retryFilters={retryCatalogue} onBusyChange={setRegistrationBusy}
                    onAccepted={acceptRegistration} />
            ) : (
                <>
                    <fieldset disabled={busy} className="flex flex-column gap-4 border-none p-0 m-0">
                        {editing ? renderUpdateMode() : (
                            <>
                                {renderOfferingInformation()}
                                {renderAdditionalOfferingInformation()}
                                {renderCapabilityInformation()}
                            </>
                        )}
                    </fieldset>
                    <div className="flex flex-wrap gap-2">
                        {mode === 'add' && <Button label="Create offering" icon="pi pi-plus"
                            disabled={busy || !creationReady || !manageable}
                            onClick={() => runAction('Create offering', () => createOffering(provider.provider_id, payload),
                                inspectWrite(provider.provider_id, payload.offering_id))} />}
                        {editing && provider && (
                            <>
                                <Button label="Save provider" icon="pi pi-save" disabled={busy || !manageable || !providerEtag || !Object.keys(patches.provider).length}
                                    onClick={() => runAction('Save provider', () => updateProvider(provider.provider_id, patches.provider, snapshot.provider.etag),
                                        inspectWrite(provider.provider_id, offering?.offering_id, 'offering'))} />
                                {offering && <Button label="Save offering" icon="pi pi-save" outlined
                                    disabled={busy || !manageable || !offeringEtag || !Object.keys(patches.offering).length}
                                    onClick={() => runAction('Save offering', () => updateOffering(offering.offering_id, patches.offering, snapshot.offering.etag),
                                        inspectWrite(provider.provider_id, offering.offering_id, 'provider'))} />}
                                {offering && <Button label="Delete offering" icon="pi pi-trash" severity="danger" outlined
                                    disabled={busy || !manageable || !offeringEtag || !isDisposableOfferingId(offering.offering_id, provider.provider_id)}
                                    onClick={() => removeRecord('offering')} />}
                                <Button label="Delete provider" icon="pi pi-trash" severity="danger" outlined
                                    disabled={busy || !manageable || !providerEtag} onClick={() => removeRecord('provider')} />
                            </>
                        )}
                    </div>
                    <ProviderPayloadPreview payload={payload} />
                    <ProviderActionResult result={actionResult} />
                    <RegistrationOutcome result={registrationOutcome} />
                </>
            )}
        </div>
    );
};

export default ProviderDemoPanel;
