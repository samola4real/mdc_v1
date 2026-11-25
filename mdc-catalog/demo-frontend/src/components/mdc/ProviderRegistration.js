import React, { useState } from 'react';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { Message } from 'primereact/message';
import {
    getOffering, getProvider, listProviderOfferings, registerProvider, validateProviderPublication
} from '@/services/mdc/provider.service';
import ProviderRegistrationFields from './ProviderRegistrationFields';
import { buildRegistrationPayload } from './providerRegistrationPayload';
import {
    createRegistrationRequestGuard, invalidateRegistrationValidation, isCurrentRegistrationValidation,
    readBackRegistration, registrationPayloadKey, registrationRetryBlocked, submitRegistration, validateRegistration
} from './providerRegistrationFlow';

const services = { getOffering, getProvider, listProviderOfferings, registerProvider };

function ValidationFeedback({ result, locallyInvalid }) {
    if (!result && !locallyInvalid) return null;
    let message = 'Please correct the highlighted information.';
    let severity = 'error';
    if (result?.kind === 'stale') {
        message = 'Information changed. Validate again before registering.';
        severity = 'warn';
    } else if (!locallyInvalid && result?.kind === 'valid') {
        message = 'Validation successful. Your information is ready to register.';
        severity = 'success';
    } else if (!locallyInvalid && result?.kind === 'unavailable') {
        message = 'Validation could not be completed. Try validating again when the service is available.';
    }
    return (
        <Card>
            <div className="flex flex-column gap-3" aria-live="polite">
                <Message severity={severity} text={message} className="w-full justify-content-start" />
                {result?.message && <div>{result.message}</div>}
                {result?.messages?.map((text) => <div key={text}>{text}</div>)}
            </div>
        </Card>
    );
}

const readBackMessages = {
    absent: 'The provider ID was absent on read-back. Validate again before choosing to retry.',
    matching: 'Both submitted IDs were found. Load the existing provider to review it.',
    providerOnly: 'The provider ID exists. The submitted offering could not be confirmed. Load the existing provider to review it.',
    unknown: 'Read-back could not establish whether the provider exists. Check the provider again before retrying.'
};

function rejectionMessage(result) {
    if (result.code === 'provider_already_exists') return 'This provider ID is already registered. Use a different disposable provider ID or load the existing provider.';
    if (result.code === 'offering_already_exists') return 'This offering ID is already registered. Choose a different offering ID for this provider.';
    return 'Registration was rejected. Review the feedback and validate again before submitting.';
}

export function RegistrationOutcome({ result, onCheck, busy }) {
    if (!result || result.kind === 'unvalidated') return null;
    const { identity, receipt } = result;
    const accepted = result.kind === 'accepted';
    const uncertain = result.kind === 'uncertain';
    const message = accepted ? 'Provider registered successfully. Manufacturing information has been saved.'
        : uncertain ? 'Registration outcome could not be confirmed. Check the provider before trying again.'
            : rejectionMessage(result);
    return (
        <Card>
            <div className="flex flex-column gap-3" aria-live="polite">
                <Message severity={accepted ? 'success' : uncertain ? 'warn' : 'error'} text={message}
                    className="w-full justify-content-start" />
                {result.message && <div>{result.message}</div>}
                {result.messages?.map((text) => <div key={text}>{text}</div>)}
                <dl className="m-0 grid">
                    <div className="col-12 md:col-6"><dt className="font-medium">Provider ID</dt><dd className="m-0">{identity.providerId}</dd></div>
                    <div className="col-12 md:col-6"><dt className="font-medium">Offering ID</dt><dd className="m-0">{identity.offeringId}</dd></div>
                    {receipt.publicationId && (
                        <div className="col-12"><dt className="font-medium">Publication receipt</dt><dd className="m-0">{receipt.publicationId}</dd></div>
                    )}
                    {receipt.publicationStatus && (
                        <div className="col-12 md:col-6"><dt className="font-medium">Publication status</dt><dd className="m-0">{receipt.publicationStatus}</dd></div>
                    )}
                    {receipt.syncStatus && (
                        <div className="col-12 md:col-6"><dt className="font-medium">Synchronization status</dt><dd className="m-0">{receipt.syncStatus}</dd></div>
                    )}
                </dl>
                {accepted && receipt.syncStatus === 'pending' && (
                    <Message severity="warn" text="Semantic synchronization pending. Search availability is not yet confirmed." />
                )}
                {accepted && result.readBack.kind !== 'matching' && (
                    <Message severity="warn" text="The publication was accepted. Read-back of the submitted provider and offering could not be completed. Use Load provider with the submitted ID above to review the record." />
                )}
                {uncertain && (
                    <>
                        <div>{readBackMessages[result.readBack.kind]}</div>
                        <div><Button label="Check provider again" type="button" outlined disabled={busy} onClick={onCheck} /></div>
                    </>
                )}
            </div>
        </Card>
    );
}

const rowPrefixes = [
    'otherCertifications', 'customOfferingFields', 'additionalMaterials',
    'additionalProcesses', 'customCapabilityFields'
];

export default function ProviderRegistration({ form, onChange, filters, filterError, retryFilters, onBusyChange, onAccepted }) {
    const [runOnce] = useState(createRegistrationRequestGuard);
    const [action, setAction] = useState(null);
    const [validation, setValidation] = useState(null);
    const [outcome, setOutcome] = useState(null);
    const [attemptedValidation, setAttemptedValidation] = useState(false);
    const [serviceCollapsed, setServiceCollapsed] = useState(true);
    const [technicalCollapsed, setTechnicalCollapsed] = useState(true);
    const { payload, errors } = buildRegistrationPayload(form, filters);
    const payloadKey = registrationPayloadKey(payload);
    const locallyInvalid = Object.keys(errors).length > 0;
    const busy = Boolean(action);
    const retryBlocked = registrationRetryBlocked(outcome, payload);
    const ready = filters && !locallyInvalid && !retryBlocked && isCurrentRegistrationValidation(validation, payloadKey);

    const shownErrors = {
        ...(validation?.payloadKey === payloadKey && validation.errors),
        ...(outcome?.payloadKey === payloadKey && outcome.errors),
        ...Object.fromEntries(Object.entries(errors).filter(([field]) => (
            attemptedValidation || rowPrefixes.some((prefix) => field.startsWith(prefix + '.'))
        )))
    };
    if (retryBlocked && outcome?.kind === 'rejected') {
        if (outcome.code === 'offering_already_exists') shownErrors.offeringId = 'This offering ID is already registered.';
        else shownErrors.providerId = 'This provider ID is already registered.';
    }

    const reveal = (fieldErrors) => {
        const fields = Object.keys(fieldErrors);
        if (fields.some((name) => name.startsWith('customOfferingFields')
            || ['productionMode', 'industriesServed', 'otherServiceInformation'].includes(name))) setServiceCollapsed(false);
        if (fields.some((name) => name.startsWith('customCapabilityFields'))) setTechnicalCollapsed(false);
    };

    const changeDraft = (next) => {
        if (next === form || busy) return;
        if (validation) {
            const nextKey = registrationPayloadKey(buildRegistrationPayload(next, filters).payload);
            setValidation((current) => invalidateRegistrationValidation(current, nextKey));
        }
        onChange(next);
    };

    const run = (label, operation) => runOnce(async () => {
        setAction(label);
        onBusyChange(true);
        try {
            await operation();
        } finally {
            setAction(null);
            onBusyChange(false);
        }
    });

    const handleValidation = (event) => {
        event.preventDefault();
        if (busy || !filters || retryBlocked) return;
        setAttemptedValidation(true);
        if (locallyInvalid) {
            reveal(errors);
            setValidation(null);
            return;
        }
        return run('Validating publication…', async () => {
            setValidation(null);
            const result = await validateRegistration(payload, validateProviderPublication);
            reveal(result.errors || {});
            setValidation(result);
        });
    };

    const handleRegistration = () => {
        if (busy || !ready) return;
        return run('Registering provider…', async () => {
            setValidation(null);
            const result = await submitRegistration(payload, validation, services);
            if (result.kind === 'accepted') onAccepted(result);
            else {
                reveal(result.errors || {});
                setOutcome({ ...result, payloadKey });
            }
        });
    };

    const checkProvider = () => run('Checking provider…', async () => {
        const readBack = await readBackRegistration(outcome.identity, services);
        setOutcome({ ...outcome, readBack });
    });

    return (
        <form className="mdc-provider-registration flex flex-column gap-4" noValidate aria-busy={busy} onSubmit={handleValidation}>
            {!filters && !filterError && <Message severity="info" text="Loading catalogue options…" />}
            {filterError && (
                <div className="flex flex-wrap align-items-center gap-2">
                    <Message severity="error" text="The catalogue options could not be loaded." />
                    <Button type="button" label="Retry catalogue" outlined disabled={busy} onClick={retryFilters} />
                </div>
            )}
            <fieldset disabled={busy} className="flex flex-column gap-4 border-none p-0 m-0">
                <ProviderRegistrationFields form={form} filters={filters} errors={shownErrors} onChange={changeDraft}
                    disabled={busy}
                    serviceCollapsed={serviceCollapsed} setServiceCollapsed={setServiceCollapsed}
                    technicalCollapsed={technicalCollapsed} setTechnicalCollapsed={setTechnicalCollapsed} />
            </fieldset>
            <div className="flex flex-wrap align-items-center gap-2">
                <Button label="Validate publication" icon="pi pi-eye" type="submit" disabled={busy || !filters || retryBlocked} />
                <Button label="Register provider" icon="pi pi-plus" type="button" outlined disabled={busy || !ready}
                    onClick={handleRegistration} />
                {action && <span role="status">{action}</span>}
            </div>
            <ValidationFeedback result={validation} locallyInvalid={attemptedValidation && locallyInvalid} />
            <RegistrationOutcome result={outcome} onCheck={checkProvider} busy={busy} />
        </form>
    );
}
