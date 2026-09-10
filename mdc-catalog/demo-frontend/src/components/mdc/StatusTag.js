import React from 'react';
import { Tag } from 'primereact/tag';

const SEVERITY = {
    success: 'success',
    ready: 'success',
    confirmed: 'success',
    matched: 'success',
    match: 'success',
    suitable: 'success',
    partial: 'warning',
    unknown: 'warning',
    warning: 'warning',
    info: 'info',
    healthy: 'success',
    online: 'success',
    enabled: 'success',
    unavailable: 'danger',
    'not implemented': 'warning',
    'demo-only': 'warning',
    error: 'danger',
    danger: 'danger'
};

const StatusTag = ({ value, status }) => {
    const nextStatus = status || value;
    return (
        <Tag
            value={value}
            severity={SEVERITY[nextStatus] || 'info'}
            rounded
        />
    );
};

export default StatusTag;
