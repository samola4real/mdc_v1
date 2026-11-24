import React from 'react';
import { Message } from 'primereact/message';
import ProviderResultAccordion from './ProviderResultAccordion';
import { normalizeSearchResults } from './searchResultFormatters';

const SearchResultsList = ({ response }) => {
    if (!response) return null;

    const results = normalizeSearchResults(response);
    if (response.result_count === 0) {
        return (
            <Message severity="info" className="w-full justify-content-start"
                text="No providers found for this request. Try changing the part type or optional requirements." />
        );
    }

    return (
        <div className="flex flex-column gap-3">
            <h2 className="m-0 text-900">Catalogue matches ({response.result_count})</h2>
            <ProviderResultAccordion results={results} />
        </div>
    );
};

export default SearchResultsList;
