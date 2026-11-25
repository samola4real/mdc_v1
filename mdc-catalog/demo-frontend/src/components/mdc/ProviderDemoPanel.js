import React, { useEffect, useState } from 'react';
import { Button } from 'primereact/button';
import { Message } from 'primereact/message';
import { getCatalogFilters, normalizeCatalogFilters } from '@/services/mdc/catalog.service';
import { DISPOSABLE_PROVIDER_PREFIX } from '@/services/mdc/stage1bScope';
import ProviderManagement from './ProviderManagement';
import ProviderRegistration, { RegistrationOutcome } from './ProviderRegistration';
import { emptyRegistrationForm, hasRegistrationDraft } from './providerRegistrationPayload';
import { useProviderManagement } from './useProviderManagement';

export default function ProviderDemoPanel() {
    const [mode, setMode] = useState('register');
    const [registrationForm, setRegistrationForm] = useState(emptyRegistrationForm);
    const [registrationBusy, setRegistrationBusy] = useState(false);
    const [registrationOutcome, setRegistrationOutcome] = useState(null);
    const [filters, setFilters] = useState(null);
    const [filterError, setFilterError] = useState(null);
    const [catalogueAttempt, setCatalogueAttempt] = useState(0);
    const management = useProviderManagement(filters, (snapshot) => {
        setRegistrationOutcome((current) => current && { ...current, readBack: { kind: 'matching', snapshot } });
    });
    const busy = registrationBusy || Boolean(management.busy);

    useEffect(() => {
        let active = true;
        getCatalogFilters().then(normalizeCatalogFilters)
            .then((data) => { if (active) setFilters(data); })
            .catch(() => { if (active) setFilterError(true); });
        return () => { active = false; };
    }, [catalogueAttempt]);

    const retryCatalogue = () => {
        setFilterError(null);
        setCatalogueAttempt((attempt) => attempt + 1);
    };

    const acceptRegistration = (result) => {
        management.acceptRegistration(result);
        setRegistrationForm(emptyRegistrationForm());
        setRegistrationOutcome(result);
        setMode('update');
    };

    const switchMode = (next) => {
        if (busy) return;
        if (next === mode) {
            if (mode === 'update' && management.add) management.cancelAdd();
            return;
        }
        if (mode === 'register' && hasRegistrationDraft(registrationForm) && !window.confirm('Discard this registration draft?')) return;
        if (mode === 'update' && !management.canLeave()) return;
        management.reset();
        setRegistrationForm(emptyRegistrationForm());
        setRegistrationOutcome(null);
        setMode(next);
    };

    return (
        <div className="flex flex-column gap-4">
            <Message severity="info" text={'Provider and offering writes are limited to disposable IDs starting with ' + DISPOSABLE_PROVIDER_PREFIX + '.'}
                className="w-full justify-content-start" />
            <div className="flex flex-wrap gap-2">
                <Button label="Register New Provider" icon="pi pi-plus" outlined={mode !== 'register'}
                    disabled={busy} onClick={() => switchMode('register')} />
                <Button label="Update Existing Provider" icon="pi pi-pencil" outlined={mode !== 'update'}
                    disabled={busy} onClick={() => switchMode('update')} />
            </div>
            {mode === 'register' ? (
                <ProviderRegistration form={registrationForm} onChange={setRegistrationForm} filters={filters}
                    filterError={filterError} retryFilters={retryCatalogue} onBusyChange={setRegistrationBusy}
                    onAccepted={acceptRegistration} />
            ) : (
                <>
                    <ProviderManagement model={management} filters={filters} filterError={filterError} retryFilters={retryCatalogue} />
                    <RegistrationOutcome result={registrationOutcome} />
                </>
            )}
        </div>
    );
}
