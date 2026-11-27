import React from 'react';
import { Message } from 'primereact/message';
import ProviderResultAccordion from './ProviderResultAccordion';

const SearchResultsList = ({ response, catalogue, hasRequirements }) => {
    if (!response) return null;

    const partTypeLabel = catalogue.partTypes[response.part_family]?.find(({ value }) => value === response.part_type)?.label;
    return (
        <section className="mdc-consumer-results" aria-labelledby="eligible-offerings">
            <div role="status">
                <h2 id="eligible-offerings">Eligible Manufacturing Offerings ({response.result_count})</h2>
                {response.result_count > 0 && <p>The following manufacturing offerings satisfy all your specified requirements.</p>}
            </div>
            {response.result_count === 0 ? (
                <Message
                    severity="info"
                    className="w-full justify-content-start"
                    text="No manufacturing offerings meet your specified requirements. Review or adjust your search criteria."
                />
            ) : (
                <ProviderResultAccordion
                    results={response.results}
                    catalogue={catalogue}
                    partTypeLabel={partTypeLabel}
                    hasRequirements={hasRequirements}
                />
            )}
        </section>
    );
};

export default SearchResultsList;
