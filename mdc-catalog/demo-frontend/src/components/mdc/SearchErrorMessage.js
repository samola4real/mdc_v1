import React from 'react';
import { Message } from 'primereact/message';
import { INVALID_REQUIREMENTS } from './consumerSearchCriteria';

const SearchErrorMessage = ({ error, fallback }) => {
    if (!error) return null;
    const message = {
        401: 'Your session has expired. Please sign in again.',
        403: 'You do not have permission to access this service.'
    }[error.status] || fallback || (error.status === 400
        ? INVALID_REQUIREMENTS
        : 'Service discovery is temporarily unavailable. Please try again shortly.');

    return <Message severity="error" text={message} className="w-full justify-content-start" />;
};

export default SearchErrorMessage;
