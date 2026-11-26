import { readableCode } from './providerManagementDraft.js';
import { observedWrite } from './providerManagementFlow.js';

const pendingSync = 'Synchronization is pending. Search availability is still unconfirmed.';
const notice = (severity, summary, detail, receipt) => ({
    severity, summary,
    detail: [detail, receipt?.syncStatus === 'pending' && pendingSync].filter(Boolean).join(' ')
});

export function actionToastMessage(feedback) {
    return { ...feedback, life: 5000, sticky: ['warn', 'error'].includes(feedback.severity) };
}

const rejectionHelp = {
    400: 'Review the highlighted information and correct the rejected fields.',
    401: 'Sign in with MaaSAI Keycloak.',
    403: 'Check your verified role and the disposable ID scope.',
    404: 'Load the current record to review its availability.',
    409: 'Choose a different offering ID or load the existing offering to review it.'
};

export function managementFeedback(result) {
    if (!result) return null;
    const { request, receipt, observed } = result;
    if (result.kind === 'readError') return notice('error', 'Record could not be loaded', result.message, receipt);
    if (!request) return notice('info', 'Provider lookup', result.message, receipt);
    const entity = readableCode(request.entity);
    const verified = observedWrite(request, observed);
    if (result.kind === 'conflict') {
        return notice('warn', entity + ' revision changed', verified ? 'The record is absent on read-back.'
            : 'Review the current record before trying again.', receipt);
    }
    if (result.kind === 'accepted') {
        const action = { save: 'saved', create: 'created', delete: 'deleted' }[request.operation];
        return verified ? notice('success', entity + ' ' + action, null, receipt)
            : notice('warn', entity + ' write accepted', 'Check the current record to verify the result.', receipt);
    }
    if (result.kind === 'uncertain') {
        const detail = request.operation === 'delete' ? 'The record is absent on read-back.' : 'The submitted values are present on read-back.';
        return notice('warn', 'Write outcome could not be confirmed', verified
            ? detail + ' A write receipt could not be verified.'
            : 'Check the current record before retrying.', receipt);
    }
    return notice('error', entity + ' action was rejected',
        [result.message, rejectionHelp[result.status]].filter(Boolean).join(' '), receipt);
}

const registrationReadBack = {
    absent: 'The provider ID was absent on read-back. Validate again before choosing to retry.',
    matching: 'Both submitted IDs were found. Load the existing provider to review it.',
    providerOnly: 'The provider exists. Load it to check the submitted offering.',
    unknown: 'Check the provider again before retrying.'
};

export function registrationFeedback(result) {
    if (!result || result.kind === 'unvalidated') return null;
    const { kind, receipt, readBack, code, message } = result;
    if (kind === 'accepted') {
        return readBack.kind === 'matching' ? notice('success', 'Provider registered', null, receipt)
            : notice('warn', 'Registration accepted', 'Use Load provider to verify the submitted provider and offering.', receipt);
    }
    if (kind === 'uncertain') {
        return notice('warn', 'Registration outcome could not be confirmed', registrationReadBack[readBack.kind], receipt);
    }
    const duplicate = {
        provider_already_exists: 'Load the existing provider or use a different disposable provider ID.',
        offering_already_exists: 'Choose a different offering ID for this provider.'
    };
    return notice('error', 'Registration was rejected',
        [duplicate[code] || 'Review the feedback and validate again.', message].filter(Boolean).join(' '), receipt);
}
