import React from 'react';
import { Accordion, AccordionTab } from 'primereact/accordion';
import { Tag } from 'primereact/tag';
import {
    EVIDENCE_GROUPS,
    formatCapabilityRange,
    formatEvidenceList,
    formatFieldLabel,
    formatSuitability,
    NOT_PROVIDED,
    offeringKey
} from './searchResultFormatters';

const groupedFields = new Set(EVIDENCE_GROUPS.map(({ field }) => field));

const CapabilityComparison = ({ capabilities }) => (
    capabilities.length ? (
        <table className="mdc-consumer-comparison">
            <thead>
                <tr>
                    <th scope="col">Manufacturing specification</th>
                    <th scope="col">Your requirement</th>
                    <th scope="col">Provider capability</th>
                </tr>
            </thead>
            <tbody>
                {capabilities.map(({ field, requested, provided }) => (
                    <tr key={field}>
                        <th scope="row">{formatFieldLabel(field)}</th>
                        <td>{formatCapabilityRange(requested)}</td>
                        <td>{formatCapabilityRange(provided)}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    ) : <p>Manufacturing specifications: {NOT_PROVIDED}</p>
);

const OfferingEvidence = ({ result, catalogue, partTypeLabel, hasRequirements }) => (
    <div className="mdc-consumer-evidence">
        {partTypeLabel && <p className="mdc-consumer-part-confirmed">Confirmed part type: <strong>{partTypeLabel}</strong></p>}
        <h3>Capability comparison</h3>
        {hasRequirements ? (
            <>
                <CapabilityComparison capabilities={result.matched_capabilities.filter(({ field }) => !groupedFields.has(field))} />
                <dl className="mdc-consumer-grid mdc-consumer-evidence-groups">
                    {EVIDENCE_GROUPS.map((group) => {
                        const capability = result.matched_capabilities.find(({ field }) => field === group.field);
                        const options = catalogue?.[group.field];
                        return (
                            <div key={group.field}>
                                <dt>{group.label}</dt>
                                <dd>{formatEvidenceList(capability?.provided, group, options)}</dd>
                                {capability?.requested && <dd className="mdc-consumer-hint">Requested: {formatEvidenceList(capability.requested, group, options)}</dd>}
                            </div>
                        );
                    })}
                </dl>
            </>
        ) : <p>No additional requirements were specified.</p>}
    </div>
);

const ProviderResultAccordion = ({ results, catalogue, partTypeLabel, hasRequirements }) => (
    <Accordion>
        {results.map((result) => (
            <AccordionTab
                key={offeringKey(result)}
                header={
                    <div className="mdc-consumer-offering">
                        <div>
                            <strong>{result.provider_name}</strong>
                            <span>{result.offering_name}</span>
                            {partTypeLabel && <span className="mdc-consumer-hint">Requested part type: {partTypeLabel}</span>}
                        </div>
                        <Tag value={formatSuitability(result.match.status)} severity="success" rounded />
                    </div>
                }
            >
                <OfferingEvidence
                    result={result}
                    catalogue={catalogue}
                    partTypeLabel={partTypeLabel}
                    hasRequirements={hasRequirements}
                />
            </AccordionTab>
        ))}
    </Accordion>
);

export default ProviderResultAccordion;
