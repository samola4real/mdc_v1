import React, { useEffect, useState } from 'react';
import Button from './MaaSAIButton';
import { Message } from 'primereact/message';
import { getCatalogFilters, normalizeCatalogFilters } from '@/services/mdc/catalog.service';
import { DISPOSABLE_PROVIDER_PREFIX } from '@/services/mdc/stage1bScope';
import { ProviderActionToast, useProviderActionToast } from './ProviderActionResult';
import ProviderManagement from './ProviderManagement';
import ProviderRegistration, { RegistrationOutcome } from './ProviderRegistration';
import { managementFeedback, registrationFeedback } from './providerActionFeedback';
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
    const { toast, notify } = useProviderActionToast();
    const management = useProviderManagement(filters, (snapshot) => {
        if (!registrationOutcome || registrationOutcome.readBack.kind === 'matching') return;
        const verified = { ...registrationOutcome, readBack: { kind: 'matching', snapshot } };
        setRegistrationOutcome(verified);
        notify(registrationFeedback(verified));
    }, (result) => notify(managementFeedback(result)));
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
            <ProviderActionToast toast={toast} />
            <Message severity="info" text={'Registration and changes are available for designated test records only. Provider IDs must start with ' + DISPOSABLE_PROVIDER_PREFIX + '.'}
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
                    onAccepted={acceptRegistration} onActionResult={(result) => notify(registrationFeedback(result))} />
            ) : (
                <ProviderManagement model={management} filters={filters} filterError={filterError} retryFilters={retryCatalogue}
                    registrationContext={<RegistrationOutcome result={registrationOutcome} />} />
            )}
        </div>
    );
}
