import React from 'react';
import { Message } from 'primereact/message';
import { Panel } from 'primereact/panel';

const getFriendlyError = (error) => {
    if (!error) {
        return null;
    }

    if (error.status === 404) {
        return 'The service-discovery search endpoint is not available yet. Check whether the backend search endpoint has been activated.';
    }

    if (error.status === 400) {
        return 'The search request was rejected by the backend. Please check the selected part type and requirement fields.';
    }

    if (error.status >= 500) {
        return error.message || 'The MDC backend returned a server error while processing the search request.';
    }

    if (error.status == null) {
        return 'Cannot reach MDC backend at the configured API URL. Check that Django is running at http://localhost:8000.';
    }

    return error.message || 'The MDC search request failed.';
};

const SearchErrorMessage = ({ error }) => {
    const message = getFriendlyError(error);

    if (!message) {
        return null;
    }

    return (
        <div className="flex flex-column gap-3">
            <Message
                severity="error"
                text={message}
                className="w-full justify-content-start"
            />
            {error?.details ? (
                <Panel header="Backend error details" toggleable collapsed>
                    <pre className="m-0 white-space-pre-wrap">{JSON.stringify(error.details, null, 2)}</pre>
                </Panel>
            ) : null}
        </div>
    );
};

export default SearchErrorMessage;

