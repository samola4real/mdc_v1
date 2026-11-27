import React, { useEffect, useRef, useState } from 'react';
import { Accordion, AccordionTab } from 'primereact/accordion';
import Button from './MaaSAIButton';
import { Message } from 'primereact/message';
import { Tag } from 'primereact/tag';
import { Toast } from 'primereact/toast';
import { getOffering, getProvider } from '@/services/mdc/provider.service';
import { buildRequirementComparison, createOfferingDetailsLoader } from './consumerOfferingDetails';
import { formatSuitability, offeringKey } from './searchResultFormatters';

const columns = ['Specification', 'Your requirement', 'Provider capability', 'Status'];
const contactMessage = 'Future implementation: contacting providers will be available in a future release.';

function RequirementComparison({ rows, lenient }) {
    return (
        <section aria-label="Requirement Comparison">
            <h3>Requirement Comparison</h3>
            <table className="mdc-consumer-comparison" aria-label="Search requirements and preferences">
                <thead>
                    <tr>{columns.map((label) => <th scope="col" key={label}>{label}</th>)}</tr>
                </thead>
                <tbody>
                    {rows.map(({ field, label, requested, provided, status }, index) => (
                        <tr key={field + '-' + index}>
                            <th scope="row">{label}</th>
                            <td><span className="mdc-comparison-mobile-label" aria-hidden="true">Your requirement</span>{requested}</td>
                            <td><span className="mdc-comparison-mobile-label" aria-hidden="true">Provider capability</span>{provided}</td>
                            <td>
                                <span className={status === 'Matched' ? 'mdc-comparison-matched' : 'mdc-comparison-unresolved'}>
                                    {status === 'Matched' && <i className="pi pi-check" aria-hidden="true" />} {status}
                                </span>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
            {lenient && rows.some(({ field }) => field === 'materials') && <p>One supported alternative satisfies the material preference.</p>}
            {rows.length === 1 && <p>No additional requirements were specified.</p>}
        </section>
    );
}

function PublishedOverview({ entry, onRetry }) {
    const kind = entry?.kind;
    return (
        <section className="mdc-offering-overview" aria-label="Manufacturing Capability Overview">
            <h3>Manufacturing Capability Overview</h3>
            {kind === 'ready' ? (
                <>
                    <p>Published capabilities for this offering.</p>
                    <div className="mdc-offering-facts-grid">
                        {entry.details.sections.map(({ title, rows }) => (
                            <section className="mdc-offering-facts" key={title}>
                                <h4>{title}</h4>
                                <ul className={title === 'Manufacturing processes' ? 'mdc-offering-process-list' : undefined}>
                                    {rows.map(({ label, value }) => (
                                        <li key={label}>
                                            <span>{label}</span>
                                            {value && <strong>{value}</strong>}
                                        </li>
                                    ))}
                                </ul>
                            </section>
                        ))}
                    </div>
                </>
            ) : <DetailsNotice entry={entry} onRetry={onRetry} />}
        </section>
    );
}

function DetailsNotice({ entry, onRetry }) {
    if (!entry || entry.kind === 'loading') return <p role="status">Loading offering details...</p>;
    if (entry.kind === 'changed' || entry.kind === 'unavailable') {
        const message = entry.kind === 'changed' ? 'This offering has changed since your search.' : 'This offering is no longer available.';
        return <Message severity="warn" className="mt-2" text={message + ' Search again to check current eligibility.'} />;
    }
    const message = {
        401: 'Your session has expired. Please sign in again.',
        403: 'You do not have permission to view offering details.'
    }[entry.status] || 'Offering details are temporarily unavailable.';
    return (
        <div className="mdc-consumer-actions mt-2">
            <Message severity="warn" text={message} />
            <Button type="button" label="Retry details" icon="pi pi-refresh" outlined onClick={onRetry} />
        </div>
    );
}

const ProviderResultAccordion = ({ results, context }) => {
    const toast = useRef(null);
    const [loader] = useState(() => createOfferingDetailsLoader({ getProvider, getOffering }));
    const [activeIndex, setActiveIndex] = useState(null);
    const [entries, setEntries] = useState({});
    const [downloading, setDownloading] = useState({});
    const downloads = useRef(new Map());
    const lenient = context.discoveryMode === 'lenient';

    useEffect(() => {
        const activeDownloads = downloads.current;
        return () => {
            loader.clear();
            activeDownloads.clear();
        };
    }, [loader]);

    const load = (result, retry) => loader.load(result, context,
        (key, entry) => setEntries((current) => ({ ...current, [key]: entry })), retry);

    const changeTab = ({ index }) => {
        setActiveIndex(index);
        if (results[index]) void load(results[index]);
    };

    const notify = (message) => {
        toast.current?.clear();
        toast.current?.show({ life: 4000, ...message });
    };

    const download = async (key, comparison) => {
        const entry = entries[key];
        if (downloads.current.has(key) || entry?.kind !== 'ready') return;
        const job = {};
        downloads.current.set(key, job);
        setDownloading((current) => ({ ...current, [key]: true }));
        try {
            const { createOfferingPdf, offeringPdfFilename } = await import('./offeringPdf');
            const pdf = await createOfferingPdf(entry.details, comparison);
            if (downloads.current.get(key) !== job) return;
            pdf.save(offeringPdfFilename(entry.details.offeringId));
            notify({ severity: 'success', summary: 'Download Offering', detail: 'Your offering PDF is ready.' });
        } catch (error) {
            if (downloads.current.get(key) === job) {
                const detail = error?.code === 'unsupported_pdf_characters'
                    ? 'The offering contains characters that the PDF export cannot display.'
                    : 'The offering PDF could not be created. Please try again.';
                notify({ severity: 'error', summary: 'Download Offering', detail });
            }
        } finally {
            if (downloads.current.get(key) === job) {
                downloads.current.delete(key);
                setDownloading((current) => ({ ...current, [key]: false }));
            }
        }
    };

    return (
        <>
            <Toast ref={toast} position="top-right" className="mdc-offering-toast" />
            <Accordion activeIndex={activeIndex} onTabChange={changeTab}>
                {results.map((result, index) => {
                    const key = offeringKey(result);
                    const entry = entries[key];
                    const comparison = activeIndex === index
                        ? buildRequirementComparison(result, context.partTypeLabel, context.catalogue, context.discoveryMode)
                        : null;
                    return (
                        <AccordionTab
                            key={key}
                            header={
                                <div className="mdc-consumer-offering">
                                    <div>
                                        <strong>{result.provider_name}</strong>
                                        <span>{result.offering_name}</span>
                                        <span className="mdc-consumer-hint">Requested part type: {context.partTypeLabel}</span>
                                    </div>
                                    <Tag value={formatSuitability(result.match.status, context.discoveryMode, context.requirements)}
                                        severity={result.match.status === 'partial_match' ? 'warning' : 'success'} rounded />
                                </div>
                            }
                        >
                            {comparison && (
                                <div className="mdc-consumer-evidence">
                                    <RequirementComparison rows={comparison} lenient={lenient} />
                                    <PublishedOverview entry={entry} onRetry={() => load(result, true)} />
                                    <div className="mdc-consumer-actions mdc-offering-actions">
                                        <Button type="button" label="Download Offering" icon="pi pi-download" loading={Boolean(downloading[key])}
                                            disabled={entry?.kind !== 'ready' || Boolean(downloading[key])}
                                            onClick={() => download(key, comparison)} />
                                        <Button type="button" label="Contact Provider" icon="pi pi-envelope" outlined
                                            onClick={() => notify({ severity: 'info', summary: 'Contact Provider', detail: contactMessage })} />
                                    </div>
                                </div>
                            )}
                        </AccordionTab>
                    );
                })}
            </Accordion>
        </>
    );
};

export default ProviderResultAccordion;
