import React from 'react';
import { Message } from 'primereact/message';
import ProviderResultAccordion from './ProviderResultAccordion';
import { catalogueLabel } from './providerManagementDraft';

const SearchResultsList = ({ response, catalogue, requirements, discoveryMode }) => {
    if (!response) return null;

    const lenient = discoveryMode === 'lenient';
    const partTypeLabel = catalogueLabel(catalogue.partTypes[response.part_family], response.part_type);
    return (
        <section className="mdc-consumer-results" aria-labelledby="eligible-offerings">
            <div role="status">
                <h2 id="eligible-offerings">{lenient ? 'Manufacturing Offerings' : 'Eligible Manufacturing Offerings'} ({response.result_count})</h2>
                {response.result_count > 0 && <p>{lenient
                    ? 'These offerings meet your mandatory requirements. Open an offering to see how it meets your preferences.'
                    : 'The following manufacturing offerings satisfy all your specified requirements.'}</p>}
            </div>
            {response.result_count === 0 ? (
                <Message
                    severity="info"
                    className="w-full justify-content-start"
                    text={lenient
                        ? 'No manufacturing offerings meet your mandatory requirements. Review or adjust your search criteria.'
                        : 'No manufacturing offerings meet your specified requirements. Review or adjust your search criteria.'}
                />
            ) : (
                <ProviderResultAccordion
                    key={response.request_id}
                    results={response.results}
                    context={{ partType: response.part_type, partTypeLabel, catalogue, requirements, discoveryMode }}
                />
            )}
        </section>
    );
};

export default SearchResultsList;
