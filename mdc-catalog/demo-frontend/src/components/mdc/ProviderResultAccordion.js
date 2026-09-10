import React, { useRef } from 'react';
import { Accordion, AccordionTab } from 'primereact/accordion';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { Column } from 'primereact/column';
import { DataTable } from 'primereact/datatable';
import { Message } from 'primereact/message';
import { Panel } from 'primereact/panel';
import { Tag } from 'primereact/tag';
import { Toast } from 'primereact/toast';
import {
    asArray,
    formatCapabilityRange,
    formatEvidenceValue,
    formatFieldLabel,
    formatLabel,
    formatSupportStatus,
    formatSuitability,
    formatTagLabel,
    getNested,
    snakeToTitle
} from './searchResultFormatters';

const getProvider = (result) => result.provider || {};
const getOffering = (result) => result.offering || {};
const getMatch = (result) => result.match || {};
const getMatchedAttributes = (result) => asArray(result.matched_attributes);
const getUnmatchedAttributes = (result) => asArray(result.unmatched_attributes);
const getUnknownAttributes = (result) => asArray(result.unknown_attributes);

const getProviderName = (result) => (
    result.provider_name || result.providerName || getProvider(result).provider_name || 'Not provided'
);

const getProviderId = (result) => (
    result.provider_id || result.providerId || getProvider(result).provider_id || 'Not provided'
);

const getOfferingName = (result) => (
    result.offering_name || result.offeringName || getOffering(result).offering_name || 'Not provided'
);

const getOfferingId = (result) => (
    result.offering_id || result.offeringId || getOffering(result).offering_id || 'Not provided'
);

const getPartFamily = (result) => getOffering(result).part_family || result.part_family || 'Not provided';

const getPartTypeMatch = (result) => (
    getMatchedAttributes(result).find((item) => item?.field === 'part_type')
);

const getPartTypeLabel = (result) => {
    const partType = getPartTypeMatch(result)?.requested || result.part_type;
    return partType ? formatTagLabel(partType) : 'Not provided';
};

const getSuitability = (result) => formatSuitability(getMatch(result).status || result.status);

const getSupportStatus = (result) => (
    formatSupportStatus(
        getPartTypeMatch(result)?.status
        || getPartTypeMatch(result)?.provided?.support_status
        || getMatch(result).status
    )
);

const getSeverity = (status) => {
    if (status === 'Suitable' || status === 'Confirmed' || status === 'Matched') return 'success';
    if (status === 'Candidate' || status === 'Evidence incomplete' || status === 'Not confirmed') return 'warning';
    return 'info';
};

const formatRequirement = (attribute) => {
    if (attribute.field === 'part_type') {
        return `Part type: ${formatTagLabel(attribute.requested)}`;
    }
    return `${formatFieldLabel(attribute.field)}: ${formatEvidenceValue(attribute.requested)}`;
};

const formatCapability = (attribute) => {
    const provided = attribute.provided;

    if (attribute.field === 'part_type') {
        return provided?.support_status ? formatSupportStatus(provided.support_status) : 'Supported';
    }
    if (attribute.field === 'materials') {
        return 'Supported';
    }
    if (attribute.field === 'processes') {
        return 'Available';
    }
    if (attribute.field === 'certifications') {
        return 'Available';
    }

    return formatEvidenceValue(provided);
};

const makeSuitabilityRows = (result) => (
    [...getMatchedAttributes(result), ...getUnmatchedAttributes(result)].map((attribute, index) => ({
        id: `${attribute.field || 'attribute'}-${index}`,
        requirement: formatRequirement(attribute),
        capability: formatCapability(attribute),
        status: formatSupportStatus(attribute.status)
    }))
);

const getCanonicalCapabilityRows = (result) => (
    getMatchedAttributes(result)
        .filter((item) => !['part_type', 'materials', 'processes', 'certifications'].includes(item?.field))
        .map((item) => ({
            label: formatFieldLabel(item.field),
            value: formatCapabilityRange(item.provided ?? item.requested)
        }))
);

const flattenCapabilities = (evidence) => {
    const family = getNested(evidence, 'family_capabilities', {});
    const generic = getNested(evidence, 'generic_capabilities', {});

    return [
        ...Object.entries(family).map(([field, value]) => ({
            label: formatFieldLabel(field),
            value: formatCapabilityRange(value)
        })),
        ...[
            ['Weight', generic.weight_kg ? `up to ${formatCapabilityRange(generic.weight_kg)} kg` : null],
            ['Batch size', generic.batch_size ? `${formatCapabilityRange(generic.batch_size)} pcs` : null],
            ['Delivery time', generic.lead_time_weeks ? `${formatCapabilityRange(generic.lead_time_weeks)} weeks` : null],
            ['Surface finish Ra', generic.surface_finish_ra_um ? formatCapabilityRange(generic.surface_finish_ra_um) : null]
        ]
            .filter(([, value]) => value)
            .map(([label, value]) => ({ label, value }))
    ];
};

const getMaterials = (result) => {
    const evidenceMaterials = asArray(getNested(result, 'evidence.materials'));
    const genericMaterials = asArray(getNested(result, 'evidence.generic_capabilities.materials'));
    const canonicalMaterials = getMatchedAttributes(result)
        .filter((item) => item?.field === 'materials')
        .flatMap((item) => asArray(item.provided ?? item.requested));
    return [...evidenceMaterials, ...genericMaterials, ...canonicalMaterials].flatMap((item) => {
        if (typeof item === 'string') return [item];
        return [item.material, ...asArray(item.available_grades)].filter(Boolean);
    });
};

const getProcesses = (result) => (
    [
        ...asArray(getNested(result, 'evidence.generic_capabilities.processes')),
        ...getMatchedAttributes(result)
            .filter((item) => item?.field === 'processes')
            .flatMap((item) => asArray(item.provided ?? item.requested))
    ].map((item) => (
        typeof item === 'string' ? item : item.process
    )).filter(Boolean)
);

const getCertifications = (result) => (
    [
        ...asArray(getNested(result, 'evidence.certifications')),
        ...getMatchedAttributes(result)
            .filter((item) => item?.field === 'certifications')
            .flatMap((item) => asArray(item.provided ?? item.requested))
    ].map((item) => (
        typeof item === 'string' ? item : item.code
    )).filter(Boolean)
);

const getUnknownItems = (result) => (
    getUnknownAttributes(result).map((item) => ({
        field: formatFieldLabel(item.field),
        reason: item.reason || 'Provider capability was not confirmed.'
    }))
);

const formatDemoValue = (value) => {
    if (value == null || value === '') return 'Not provided';
    if (Array.isArray(value)) return value.map(formatDemoValue).join(', ');
    if (typeof value === 'object') return formatCapabilityRange(value);
    return String(value);
};

const DemoFieldTable = ({ rows }) => {
    if (!rows || rows.length === 0) {
        return <span className="text-600">Not provided</span>;
    }

    return (
        <DataTable value={rows} dataKey="id" responsiveLayout="scroll" stripedRows>
            <Column field="name" header="Field" />
            <Column field="value" header="Value" body={(row) => formatDemoValue(row.value)} />
            <Column field="notes" header="Notes" body={(row) => formatDemoValue(row.notes)} />
        </DataTable>
    );
};

const Tags = ({ values, severity }) => {
    const unique = Array.from(new Set(values.filter(Boolean)));

    if (unique.length === 0) {
        return <span className="text-600">Not provided</span>;
    }

    return (
        <div className="flex flex-wrap gap-2">
            {unique.map((value) => (
                <Tag key={value} value={formatTagLabel(value)} severity={severity} rounded />
            ))}
        </div>
    );
};

const Header = ({ result }) => {
    const suitability = getSuitability(result);
    return (
        <div className="flex flex-column md:flex-row md:align-items-center md:justify-content-between gap-2 w-full">
            <div>
                <div className="font-semibold text-900">{getProviderName(result)}</div>
                <div className="text-sm text-600">
                    {getOfferingName(result)} | {getPartTypeLabel(result)} supported
                </div>
            </div>
            <div className="flex flex-wrap gap-2">
                {result.demo_overlay ? (
                    <Tag value="Demo registered provider" severity="info" rounded />
                ) : null}
                <Tag value={suitability} severity={getSeverity(suitability)} rounded />
            </div>
        </div>
    );
};

const ProviderResultPanel = ({ result }) => {
    const toast = useRef(null);
    const suitability = getSuitability(result);
    const supportStatus = getSupportStatus(result);
    const suitabilityRows = makeSuitabilityRows(result);
    const capabilities = [
        ...getCanonicalCapabilityRows(result),
        ...flattenCapabilities(result.evidence || {})
    ];
    const unknownItems = getUnknownItems(result);

    const demoAction = (label) => {
        toast.current?.show({
            severity: 'info',
            summary: label,
            detail: 'Demo action only - this will be connected to the Marketplace workflow later.',
            life: 2500
        });
    };

    return (
        <div className="flex flex-column gap-4">
            <Toast ref={toast} />
            <Card>
                <div className="grid">
                    <div className="col-12 md:col-6">
                        <div className="text-sm text-600">Provider</div>
                        <div className="font-semibold text-900">{getProviderName(result)}</div>
                    </div>
                    <div className="col-12 md:col-6">
                        <div className="text-sm text-600">Offering</div>
                        <div className="font-semibold text-900">{getOfferingName(result)}</div>
                    </div>
                    <div className="col-12 md:col-6">
                        <div className="text-sm text-600">Part type</div>
                        <div className="font-semibold text-900">{getPartTypeLabel(result)}</div>
                    </div>
                    <div className="col-12 md:col-6">
                        <div className="flex flex-wrap gap-2">
                            <Tag value={`Suitability: ${suitability}`} severity={getSeverity(suitability)} rounded />
                            <Tag value={`Support status: ${supportStatus}`} severity={getSeverity(supportStatus)} rounded />
                        </div>
                    </div>
                </div>
            </Card>

            {result.demo_overlay ? (
                <>
                    <Card title="Provider summary">
                        <div className="grid">
                            <div className="col-12 md:col-6">
                                <div className="text-sm text-600">Country</div>
                                <div className="font-medium text-900">
                                    {result.demo_overlay.country || 'Not provided'}
                                </div>
                            </div>
                            <div className="col-12 md:col-6">
                                <div className="text-sm text-600">Source</div>
                                <Tag value={result.demo_overlay.source} severity="info" rounded />
                            </div>
                            <div className="col-12">
                                <div className="text-sm text-600">Description</div>
                                <div className="font-medium text-900">
                                    {result.demo_overlay.description || 'Registered through the demo provider workflow.'}
                                </div>
                            </div>
                        </div>
                    </Card>

                    <Card title="Why this appears">
                        <p className="m-0 line-height-3 text-700">{result.demo_overlay.reason}</p>
                    </Card>

                    <Card title="Demo offering fields">
                        <DemoFieldTable rows={result.demo_overlay.customOfferingFields} />
                    </Card>

                    <Card title="Demo capability fields">
                        <DemoFieldTable rows={result.demo_overlay.customCapabilityFields} />
                    </Card>
                </>
            ) : null}

            <Card title="Why this provider is suitable">
                <DataTable value={suitabilityRows} dataKey="id" responsiveLayout="scroll" stripedRows>
                    <Column field="requirement" header="Your requirement" />
                    <Column field="capability" header="Provider capability" />
                    <Column
                        field="status"
                        header="Status"
                        body={(row) => <Tag value={row.status} severity={getSeverity(row.status)} rounded />}
                    />
                </DataTable>
            </Card>

            <Card title="Provider manufacturing capability">
                {capabilities.length > 0 ? (
                    <div className="grid">
                        {capabilities.map((item) => (
                            <div className="col-12 md:col-6" key={`${item.label}-${item.value}`}>
                                <div className="text-sm text-600">{item.label}</div>
                                <div className="font-medium text-900">{item.value}</div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <span className="text-600">Not provided</span>
                )}
            </Card>

            <Card title="Materials">
                <Tags values={getMaterials(result)} />
            </Card>

            <Card title="Processes">
                <Tags values={getProcesses(result)} />
            </Card>

            <Card title="Certifications">
                <Tags values={getCertifications(result)} />
            </Card>

            {unknownItems.length > 0 ? (
                <Message
                    severity="warn"
                    className="w-full justify-content-start"
                    content={
                        <div>
                            <div className="font-semibold mb-2">Not confirmed by provider:</div>
                            <div className="flex flex-wrap gap-2">
                                {unknownItems.map((item) => (
                                    <Tag
                                        key={`${item.field}-${item.reason}`}
                                        value={`${item.field}: ${item.reason}`}
                                        severity="warning"
                                        rounded
                                    />
                                ))}
                            </div>
                        </div>
                    }
                />
            ) : null}

            <div className="flex flex-wrap gap-2">
                <Button label="Request quotation" icon="pi pi-send" onClick={() => demoAction('Request quotation')} />
                <Button label="View provider details" icon="pi pi-building" outlined onClick={() => demoAction('View provider details')} />
                <Button label="Save result" icon="pi pi-bookmark" outlined onClick={() => demoAction('Save result')} />
            </div>

            <Panel header="Advanced/debug response JSON" toggleable collapsed>
                <div className="text-sm text-600 mb-2">
                    Provider ID: {getProviderId(result)} | Offering ID: {getOfferingId(result)} | Family: {snakeToTitle(getPartFamily(result))}
                </div>
                <pre className="m-0 white-space-pre-wrap">{JSON.stringify(result, null, 2)}</pre>
            </Panel>
        </div>
    );
};

const ProviderResultAccordion = ({ results }) => (
    <Accordion multiple={false}>
        {results.map((result, index) => (
            <AccordionTab
                key={getOfferingId(result) || getProviderId(result) || index}
                header={<Header result={result} />}
            >
                <ProviderResultPanel result={result} />
            </AccordionTab>
        ))}
    </Accordion>
);

export default ProviderResultAccordion;
