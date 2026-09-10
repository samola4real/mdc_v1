import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
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
import { getProviderDemoState, previewProviderPublication, simulateProviderUpdate } from '@/services/mdc/demoAdmin.service';
import ProviderActionResult from './ProviderActionResult';
import ProviderPayloadPreview from './ProviderPayloadPreview';
import StatusTag from './StatusTag';
import { buildProviderPreviewPayload } from './providerPayloadBuilder';
import {
    capabilityTemplates,
    certifications,
    materials,
    partTypes,
    processes,
    serviceCategories
} from './mockData';

const qualityStandards = ['DIN', 'ISO', 'AGMA', 'Customer specified'];
const availableGrades = ['18CrNiMo7-6', '16MnCr5', '20MnCr5'];

const templateDefaults = {
    gear_manufacturing: {
        serviceCategory: 'precision_gears',
        partFamily: 'gear',
        partTypes: ['spur_gear', 'helical_gear']
    },
    shaft_manufacturing: {
        serviceCategory: 'precision_shafts',
        partFamily: 'shaft',
        partTypes: ['splined_shaft', 'plain_shaft']
    },
    metal_part_manufacturing: {
        serviceCategory: 'precision_manufacturing',
        partFamily: 'metal_part',
        partTypes: ['block', 'bracket', 'plate']
    },
    general_precision_manufacturing: {
        serviceCategory: 'precision_manufacturing',
        partFamily: 'general_precision',
        partTypes: []
    }
};

const baseCapabilityForm = {
    supportStatus: 'declared',
    partTypes: templateDefaults.gear_manufacturing.partTypes,
    moduleMin: 1,
    moduleMax: 8,
    diameterMinMm: 20,
    diameterMaxMm: 300,
    qualityStandard: 'ISO',
    qualityClass: 'Customer specified',
    lengthMaxMm: 500,
    outerDiameterMinMm: 10,
    outerDiameterMaxMm: 120,
    splineModule: 2,
    maxLengthMm: 600,
    maxWidthMm: 400,
    maxHeightMm: 150,
    maxDiameterMm: 300,
    tolerance: 'Customer specified',
    surfaceFinish: 'Customer specified',
    capabilityDescription: '',
    partTypeKeywords: '',
    maximumSizeDescription: '',
    batchSizeMin: 1,
    batchSizeMax: 1000,
    leadTimeMinWeeks: 2,
    leadTimeMaxWeeks: 12,
    weightMaxKg: 200,
    materials: ['alloyed_carburizing_steel'],
    availableGrades: ['16MnCr5', '20MnCr5'],
    processes: ['machining'],
    certifications: ['ISO9001_2015'],
    capabilityNotes: ''
};

const registerForm = {
    action: 'register_provider',
    providerId: '',
    providerName: '',
    country: '',
    description: '',
    offeringId: '',
    offeringName: '',
    customOfferingFields: [],
    customCapabilityFields: []
};

const updateForm = {
    ...baseCapabilityForm,
    action: 'update_existing_provider',
    providerId: 'tasowheel',
    providerName: 'Tasowheel Oy',
    country: 'Finland',
    description: 'Existing provider capability update for the demo.',
    certifications: ['ISO9001_2015', 'ISO14001_2015', 'ISO_TS_16949_partial', 'APQP'],
    offeringId: 'tasowheel_precision_gears',
    offeringName: 'Precision gears',
    capabilityTemplate: 'gear_manufacturing',
    serviceCategory: 'precision_gears',
    partFamily: 'gear',
    partTypes: ['spur_gear', 'helical_gear', 'bevel_gear', 'worm_gear'],
    moduleMin: 0.3,
    moduleMax: 10,
    diameterMinMm: 10,
    diameterMaxMm: 500,
    qualityStandard: 'DIN',
    qualityClass: '4',
    processes: ['machining', 'hobbing', 'gear_grinding', 'gear_cutting'],
    materials: ['alloyed_carburizing_steel'],
    availableGrades
};

const staticOfferingRows = [
    {
        id: 'tasowheel_precision_gears',
        providerId: 'tasowheel',
        providerName: 'Tasowheel Oy',
        country: 'Finland',
        description: 'Existing provider capability update for the demo.',
        offering: 'Precision gears',
        serviceCategory: 'precision_gears',
        partFamily: 'gear',
        capabilityTemplate: 'gear_manufacturing',
        supportedPartTypes: ['spur_gear', 'helical_gear', 'bevel_gear', 'worm_gear'],
        materials: ['alloyed_carburizing_steel'],
        processes: ['hobbing', 'gear_grinding', 'turn_mill', 'gear_cutting'],
        certifications: ['ISO9001_2015', 'ISO14001_2015', 'ISO_TS_16949_partial', 'APQP'],
        status: 'ready'
    },
    {
        id: 'tasowheel_precision_shafts',
        providerId: 'tasowheel',
        providerName: 'Tasowheel Oy',
        country: 'Finland',
        description: 'Existing provider capability update for the demo.',
        offering: 'Precision shafts',
        serviceCategory: 'precision_shafts',
        partFamily: 'shaft',
        capabilityTemplate: 'shaft_manufacturing',
        supportedPartTypes: ['splined_shaft', 'plain_shaft', 'hollow_shaft'],
        materials: ['alloyed_carburizing_steel'],
        processes: ['hard_turning', 'grinding', 'milling', 'turn_mill'],
        certifications: ['ISO9001_2015'],
        status: 'ready'
    }
];

const textArea = {
    rows: 3,
    autoResize: true,
    className: 'w-full'
};

const createRegisterForm = () => ({
    ...registerForm,
    customOfferingFields: [],
    customCapabilityFields: []
});

const asArray = (value) => {
    if (Array.isArray(value)) return value;
    if (value && typeof value === 'object') return Object.values(value);
    return [];
};

const getCustomFieldValue = (fields, name) => {
    const target = String(name).toLowerCase();
    return (fields || []).find((field) => String(field?.name || '').toLowerCase() === target)?.value;
};

const getControlledServiceCategory = (offering) => {
    const customServiceCategory = getCustomFieldValue(offering?.custom_offering_fields, 'Service category');
    const candidate = offering?.service_category || customServiceCategory;
    return serviceCategories.includes(candidate) ? candidate : 'precision_manufacturing';
};

const getProviderStateEntries = (state) => {
    const providers = state?.providers || state?.state?.providers || state?.demo_state?.providers || state?.data?.providers;

    if (providers) {
        return asArray(providers);
    }

    return asArray(state);
};

const mapCapabilityTemplate = (offering) => {
    if (offering?.capability_template) return offering.capability_template;
    if (offering?.part_family === 'shaft') return 'shaft_manufacturing';
    if (offering?.part_family === 'metal_part') return 'metal_part_manufacturing';
    return 'general_precision_manufacturing';
};

const mapSavedProviderRows = (state) => getProviderStateEntries(state).flatMap((provider) => {
    const payload = provider?.payload || provider?.provider || provider;
    const providerId = payload?.provider_id || payload?.providerId || payload?.id || '';
    const providerName = payload?.provider_name || payload?.providerName || payload?.name || providerId || 'Saved demo provider';
    const country = payload?.country || '';
    const description = payload?.description || '';

    return asArray(payload?.offerings).map((offering, index) => {
        const capabilities = offering?.capabilities || {};
        const customOfferingFields = offering?.custom_offering_fields || [];
        const offeringId = offering?.offering_id || offering?.offeringId || offering?.id || `${providerId || 'saved_provider'}_${index}`;
        const partFamily = offering?.part_family || 'general_precision';

        return {
            id: offeringId,
            providerId,
            providerName,
            country,
            description,
            offering: offering?.offering_name || offering?.offeringName || offering?.name || offeringId,
            serviceCategory: getControlledServiceCategory({ ...offering, custom_offering_fields: customOfferingFields }),
            partFamily,
            capabilityTemplate: mapCapabilityTemplate({ ...offering, part_family: partFamily }),
            supportedPartTypes: offering?.supported_part_types || [],
            materials: capabilities?.materials || [],
            processes: capabilities?.processes || [],
            certifications: payload?.certifications || capabilities?.certifications || [],
            status: 'saved'
        };
    });
});

const mergeOfferingRows = (staticRows, savedRows) => {
    const rowsById = new Map();
    [...staticRows, ...savedRows].forEach((row) => {
        if (row?.id) {
            rowsById.set(row.id, row);
        }
    });
    return Array.from(rowsById.values());
};

const ProviderDemoPanel = () => {
    const toast = useRef(null);
    const [mode, setMode] = useState('register');
    const [updateRows, setUpdateRows] = useState(staticOfferingRows);
    const [selectedOffering, setSelectedOffering] = useState(staticOfferingRows[0]);
    const [form, setForm] = useState(createRegisterForm);
    const [loadingAction, setLoadingAction] = useState(null);
    const [actionResult, setActionResult] = useState(null);
    const [stateLoadWarning, setStateLoadWarning] = useState(null);

    const payload = useMemo(() => buildProviderPreviewPayload(form), [form]);

    const setField = (field, value) => setForm((current) => ({ ...current, [field]: value }));

    const loadProviderState = useCallback(async ({ showToast = false } = {}) => {
        try {
            const state = await getProviderDemoState();
            const savedRows = mapSavedProviderRows(state);
            const nextRows = mergeOfferingRows(staticOfferingRows, savedRows);
            setUpdateRows(nextRows);
            setStateLoadWarning(null);

            setSelectedOffering((current) => (
                nextRows.find((row) => row.id === current?.id) || nextRows[0] || null
            ));

            if (showToast) {
                toast.current?.show({
                    severity: 'success',
                    summary: 'Provider state loaded',
                    detail: 'Saved demo providers were loaded.',
                    life: 2000
                });
            }
        } catch (error) {
            setUpdateRows(staticOfferingRows);
            setSelectedOffering((current) => (
                staticOfferingRows.find((row) => row.id === current?.id) || staticOfferingRows[0]
            ));
            setStateLoadWarning('Saved demo providers could not be loaded. Showing static Tasowheel demo rows.');
        }
    }, []);

    useEffect(() => {
        loadProviderState();
    }, [loadProviderState]);

    const addCustomOfferingField = () => {
        setForm((current) => ({
            ...current,
            customOfferingFields: [
                ...(current.customOfferingFields || []),
                { name: '', value: '' }
            ]
        }));
    };

    const updateCustomOfferingField = (index, field, value) => {
        setForm((current) => ({
            ...current,
            customOfferingFields: (current.customOfferingFields || []).map((item, itemIndex) => (
                itemIndex === index ? { ...item, [field]: value } : item
            ))
        }));
    };

    const removeCustomOfferingField = (index) => {
        setForm((current) => ({
            ...current,
            customOfferingFields: (current.customOfferingFields || []).filter((_, itemIndex) => itemIndex !== index)
        }));
    };

    const addCustomCapabilityField = () => {
        setForm((current) => ({
            ...current,
            customCapabilityFields: [
                ...(current.customCapabilityFields || []),
                { name: '', value: '', unit: '', notes: '' }
            ]
        }));
    };

    const updateCustomCapabilityField = (index, field, value) => {
        setForm((current) => ({
            ...current,
            customCapabilityFields: (current.customCapabilityFields || []).map((item, itemIndex) => (
                itemIndex === index ? { ...item, [field]: value } : item
            ))
        }));
    };

    const removeCustomCapabilityField = (index) => {
        setForm((current) => ({
            ...current,
            customCapabilityFields: (current.customCapabilityFields || []).filter((_, itemIndex) => itemIndex !== index)
        }));
    };

    const applyTemplate = (templateValue) => {
        const defaults = templateDefaults[templateValue] || templateDefaults.gear_manufacturing;
        setForm((current) => ({
            ...current,
            capabilityTemplate: templateValue,
            ...defaults
        }));
    };

    const switchMode = (nextMode) => {
        toast.current?.clear();
        setMode(nextMode);
        setActionResult(null);
        setForm(nextMode === 'register' ? createRegisterForm() : updateForm);
    };

    const listBody = (field) => (row) => (row[field] || []).join(', ');
    const statusBody = (row) => <StatusTag value={row.status} status={row.status} />;

    const handleSelection = (e) => {
        const next = e.value;
        setSelectedOffering(next);
        if (!next) return;

        setForm((current) => ({
            ...current,
            action: 'update_existing_provider',
            providerId: next.providerId || updateForm.providerId,
            providerName: next.providerName || updateForm.providerName,
            country: next.country || updateForm.country,
            description: next.description || updateForm.description,
            offeringId: next.id,
            offeringName: next.offering,
            serviceCategory: next.serviceCategory,
            partFamily: next.partFamily,
            capabilityTemplate: next.capabilityTemplate || (next.partFamily === 'shaft' ? 'shaft_manufacturing' : 'gear_manufacturing'),
            partTypes: next.supportedPartTypes || [],
            materials: next.materials || [],
            certifications: next.certifications || [],
            processes: Array.from(new Set(next.processes || []))
        }));
    };

    const runAction = async (action) => {
        const isPreview = action === 'preview';
        toast.current?.clear();
        setLoadingAction(action);
        setActionResult(null);

        try {
            const response = isPreview
                ? await previewProviderPublication(payload)
                : await simulateProviderUpdate(payload);
            if (!isPreview && payload.action === 'register_provider') {
                await loadProviderState();
            }
            setActionResult({ action, payloadAction: payload.action, response });
            toast.current?.show({
                severity: 'success',
                summary: isPreview ? 'Preview validation' : 'Demo save',
                detail: 'Demo provider endpoint responded successfully.',
                life: 2500
            });
        } catch (error) {
            setActionResult({ action, payloadAction: payload.action, error });
            toast.current?.show({
                severity: error?.status === 501 ? 'warn' : 'error',
                summary: isPreview ? 'Preview validation' : 'Demo save',
                detail: error?.message || 'Provider demo action failed.',
                life: 3500
            });
        } finally {
            setLoadingAction(null);
        }
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
                    <InputText id="providerId" value={form.providerId} onChange={(e) => setField('providerId', e.target.value)} className="w-full" />
                </div>
                <div className="field col-12 md:col-4">
                    <label htmlFor="country" className="font-medium">Country</label>
                    <InputText id="country" value={form.country} onChange={(e) => setField('country', e.target.value)} className="w-full" />
                </div>
                <div className="field col-12">
                    <label htmlFor="description" className="font-medium">Short description / notes</label>
                    <InputTextarea id="description" value={form.description} onChange={(e) => setField('description', e.target.value)} {...textArea} />
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
                    <InputText id="offeringId" value={form.offeringId} onChange={(e) => setField('offeringId', e.target.value)} className="w-full" />
                </div>
                {mode === 'update' ? (
                    <>
                        <div className="field col-12 md:col-6">
                            <label htmlFor="serviceCategory" className="font-medium">Service category / capability area</label>
                            <Dropdown inputId="serviceCategory" value={form.serviceCategory} options={serviceCategories} onChange={(e) => setField('serviceCategory', e.value)} className="w-full" />
                        </div>
                        <div className="field col-12 md:col-6">
                            <label htmlFor="capabilityTemplate" className="font-medium">Capability template</label>
                            <Dropdown
                                inputId="capabilityTemplate"
                                value={form.capabilityTemplate}
                                options={capabilityTemplates}
                                optionLabel="label"
                                optionValue="value"
                                onChange={(e) => applyTemplate(e.value)}
                                className="w-full"
                            />
                        </div>
                        <div className="field col-12">
                            <p className="text-600 line-height-3 mb-0">
                                Choose a template to show useful capability fields. If the provider does not fit a specific template, use General precision manufacturing.
                            </p>
                        </div>
                    </>
                ) : null}
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
                <MultiSelect inputId="materials" value={form.materials} options={materials} onChange={(e) => setField('materials', e.value)} display="chip" className="w-full" />
            </div>
            <div className="field col-12 md:col-4">
                <label htmlFor="availableGrades" className="font-medium">Material grades</label>
                <MultiSelect inputId="availableGrades" value={form.availableGrades} options={availableGrades} onChange={(e) => setField('availableGrades', e.value)} display="chip" className="w-full" />
            </div>
            <div className="field col-12 md:col-4">
                <label htmlFor="certifications" className="font-medium">Certifications</label>
                <MultiSelect inputId="certifications" value={form.certifications} options={certifications} onChange={(e) => setField('certifications', e.value)} display="chip" className="w-full" />
            </div>
            <div className="field col-12">
                <label htmlFor="processes" className="font-medium">Processes</label>
                <MultiSelect inputId="processes" value={form.processes} options={processes} onChange={(e) => setField('processes', e.value)} display="chip" className="w-full" />
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
                <MultiSelect inputId="gearPartTypes" value={form.partTypes} options={partTypes.gears} onChange={(e) => setField('partTypes', e.value)} display="chip" className="w-full" />
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
                <MultiSelect inputId="shaftPartTypes" value={form.partTypes} options={partTypes.shafts} onChange={(e) => setField('partTypes', e.value)} display="chip" className="w-full" />
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
            <div className="field col-12 md:col-3">
                <label htmlFor="splineModule" className="font-medium">Spline module</label>
                <InputNumber inputId="splineModule" value={form.splineModule} onValueChange={(e) => setField('splineModule', e.value)} minFractionDigits={1} maxFractionDigits={2} className="w-full" />
            </div>
        </>
    );

    const renderMetalPartFields = () => (
        <>
            <div className="field col-12">
                <label htmlFor="metalPartTypes" className="font-medium">Supported metal part types</label>
                <MultiSelect inputId="metalPartTypes" value={form.partTypes} options={partTypes.metalParts} onChange={(e) => setField('partTypes', e.value)} display="chip" className="w-full" />
            </div>
            <div className="field col-12 md:col-3">
                <label htmlFor="maxLengthMm" className="font-medium">Maximum length</label>
                <InputNumber inputId="maxLengthMm" value={form.maxLengthMm} onValueChange={(e) => setField('maxLengthMm', e.value)} suffix=" mm" className="w-full" />
            </div>
            <div className="field col-12 md:col-3">
                <label htmlFor="maxWidthMm" className="font-medium">Maximum width</label>
                <InputNumber inputId="maxWidthMm" value={form.maxWidthMm} onValueChange={(e) => setField('maxWidthMm', e.value)} suffix=" mm" className="w-full" />
            </div>
            <div className="field col-12 md:col-3">
                <label htmlFor="maxHeightMm" className="font-medium">Maximum height/thickness</label>
                <InputNumber inputId="maxHeightMm" value={form.maxHeightMm} onValueChange={(e) => setField('maxHeightMm', e.value)} suffix=" mm" className="w-full" />
            </div>
            <div className="field col-12 md:col-3">
                <label htmlFor="maxDiameterMm" className="font-medium">Maximum diameter</label>
                <InputNumber inputId="maxDiameterMm" value={form.maxDiameterMm} onValueChange={(e) => setField('maxDiameterMm', e.value)} suffix=" mm" className="w-full" />
            </div>
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

    const renderGeneralFields = () => (
        <>
            <div className="field col-12">
                <label htmlFor="capabilityDescription" className="font-medium">Capability description</label>
                <InputTextarea id="capabilityDescription" value={form.capabilityDescription} onChange={(e) => setField('capabilityDescription', e.target.value)} {...textArea} />
            </div>
            <div className="field col-12 md:col-6">
                <label htmlFor="partTypeKeywords" className="font-medium">Supported part types / keywords</label>
                <InputText id="partTypeKeywords" value={form.partTypeKeywords} onChange={(e) => setField('partTypeKeywords', e.target.value)} className="w-full" placeholder="shafts, housings, precision assemblies" />
            </div>
            <div className="field col-12 md:col-6">
                <label htmlFor="maximumSizeDescription" className="font-medium">Maximum size / dimensions</label>
                <InputText id="maximumSizeDescription" value={form.maximumSizeDescription} onChange={(e) => setField('maximumSizeDescription', e.target.value)} className="w-full" />
            </div>
        </>
    );

    const renderTemplateFields = () => {
        if (form.capabilityTemplate === 'shaft_manufacturing') return renderShaftFields();
        if (form.capabilityTemplate === 'metal_part_manufacturing') return renderMetalPartFields();
        if (form.capabilityTemplate === 'general_precision_manufacturing') return renderGeneralFields();
        return renderGearFields();
    };

    const renderCapabilityInformation = () => (
        <Panel header="Capability information">
            {mode === 'register' ? (
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
            ) : (
                <div className="grid formgrid">
                    {renderTemplateFields()}
                    {renderSharedCapabilityFields()}
                </div>
            )}
        </Panel>
    );

    const renderRegisterMode = () => (
        <>
            {renderProviderInformation()}
            {renderOfferingInformation()}
            {renderAdditionalOfferingInformation()}
            {renderCapabilityInformation()}
        </>
    );

    const renderUpdateMode = () => (
        <>
            <Card title="Update Existing Provider">
                {stateLoadWarning ? (
                    <Message severity="warn" text={stateLoadWarning} className="w-full justify-content-start mb-3" />
                ) : null}
                <DataTable
                    value={updateRows}
                    dataKey="id"
                    paginator={updateRows.length > 3}
                    rows={3}
                    selectionMode="single"
                    selection={selectedOffering}
                    onSelectionChange={handleSelection}
                    responsiveLayout="scroll"
                    stripedRows
                >
                    <Column field="providerName" header="Provider" sortable />
                    <Column field="offering" header="Offering" sortable />
                    <Column field="serviceCategory" header="Service category" sortable />
                    <Column field="partFamily" header="Part family" sortable />
                    <Column header="Supported part types" body={listBody('supportedPartTypes')} />
                    <Column header="Materials" body={listBody('materials')} />
                    <Column header="Processes" body={listBody('processes')} />
                    <Column header="Status" body={statusBody} />
                </DataTable>
            </Card>
            {renderProviderInformation()}
            {renderOfferingInformation()}
            {renderCapabilityInformation()}
        </>
    );

    return (
        <div className="flex flex-column gap-4">
            <Toast ref={toast} />

            <div className="flex flex-wrap gap-2">
                <Button
                    label="Register New Provider"
                    icon="pi pi-plus"
                    outlined={mode !== 'register'}
                    onClick={() => switchMode('register')}
                />
                <Button
                    label="Update Existing Provider"
                    icon="pi pi-pencil"
                    outlined={mode !== 'update'}
                    onClick={() => switchMode('update')}
                />
            </div>

            {mode === 'register' ? renderRegisterMode() : renderUpdateMode()}

            <div className="flex flex-wrap gap-2">
                <Button
                    label={mode === 'register' ? 'Preview' : 'Preview update'}
                    icon="pi pi-eye"
                    loading={loadingAction === 'preview'}
                    disabled={Boolean(loadingAction)}
                    onClick={() => runAction('preview')}
                />
                <Button
                    label={mode === 'register' ? 'Register for demo' : 'Save update for demo'}
                    icon={mode === 'register' ? 'pi pi-plus' : 'pi pi-save'}
                    outlined
                    loading={loadingAction === 'save'}
                    disabled={Boolean(loadingAction)}
                    onClick={() => runAction('save')}
                />
            </div>

            <ProviderPayloadPreview payload={payload} />
            <ProviderActionResult result={actionResult} payload={payload} />
        </div>
    );
};

export default ProviderDemoPanel;
