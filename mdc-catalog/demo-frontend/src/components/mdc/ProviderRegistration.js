import React, { useState } from 'react';
import Button from './MaaSAIButton';
import { Message } from 'primereact/message';
import {
    getOffering, getProvider, listProviderOfferings, registerProvider, validateProviderPublication
} from '@/services/mdc/provider.service';
import ProviderRegistrationFields from './ProviderRegistrationFields';
import ProviderActionResult from './ProviderActionResult';
import { registrationFeedback } from './providerActionFeedback';
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
        <div className="text-sm line-height-3" role="status">
            <Message severity={severity} text={message} />
            {result?.message && <p className="m-0">{result.message}</p>}
            {result?.messages?.map((text) => <p className="m-0" key={text}>{text}</p>)}
        </div>
    );
}

export function RegistrationOutcome({ result, onCheck, busy }) {
    return (
        <>
            <ProviderActionResult result={result} feedback={registrationFeedback(result)} label="Registration result" />
            {result?.kind === 'uncertain' && (
                <div><Button label="Check provider again" type="button" outlined disabled={busy} onClick={onCheck} /></div>
            )}
        </>
    );
}

const rowPrefixes = [
    'otherCertifications', 'customOfferingFields', 'additionalMaterials',
    'additionalProcesses', 'customCapabilityFields'
];

export default function ProviderRegistration({ form, onChange, filters, filterError, retryFilters, onBusyChange, onAccepted, onActionResult }) {
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
            onActionResult(result);
            if (result.kind === 'accepted') onAccepted(result);
            else {
                reveal(result.errors || {});
                setOutcome({ ...result, payloadKey });
            }
        });
    };

    const checkProvider = () => run('Checking provider…', async () => {
        const readBack = await readBackRegistration(outcome.identity, services);
        const result = { ...outcome, readBack };
        setOutcome(result);
        onActionResult(result);
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
