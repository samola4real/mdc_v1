import React from 'react';
import { Message } from 'primereact/message';
import ProviderResultAccordion from './ProviderResultAccordion';

const getResults = (response) => {
    if (Array.isArray(response)) {
        return response;
    }
    if (Array.isArray(response?.results)) {
        return response.results;
    }
    if (Array.isArray(response?.data?.results)) {
        return response.data.results;
    }
    return [];
};

const SearchResultsList = ({ response, demoProviderWarning }) => {
    const results = getResults(response);
    const backendCount = response?.demo_overlay?.backend_count;
    const demoCount = response?.demo_overlay?.demo_count || 0;
    const showDemoOnlyMessage = results.length > 0 && backendCount === 0 && demoCount > 0;
    const warning = demoProviderWarning || response?.demo_overlay?.warning;

    if (!response) {
        return null;
    }

    if (results.length === 0) {
        return (
            <div className="flex flex-column gap-3">
                {warning ? (
                    <Message severity="warn" text={warning} className="w-full justify-content-start" />
                ) : null}
                <Message
                    severity="info"
                    text="No providers found for this request. Try changing part type, material, process or optional requirements."
                    className="w-full justify-content-start"
                />
            </div>
        );
    }

    return (
        <div className="flex flex-column gap-3">
            {warning ? (
                <Message severity="warn" text={warning} className="w-full justify-content-start" />
            ) : null}
            {showDemoOnlyMessage ? (
                <Message
                    severity="info"
                    text="No catalogue providers found, but demo registered providers match this request."
                    className="w-full justify-content-start"
                />
            ) : null}
            <h2 className="m-0 text-900">Suitable providers found</h2>
            <ProviderResultAccordion results={results} />
        </div>
    );
};

export default SearchResultsList;
