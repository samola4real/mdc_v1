import React, { useState } from 'react';
import Button from './MaaSAIButton';
import { Card } from 'primereact/card';
import { Column } from 'primereact/column';
import { DataTable } from 'primereact/datatable';
import { InputText } from 'primereact/inputtext';
import { Message } from 'primereact/message';
import { Panel } from 'primereact/panel';
import ProviderActionResult, { DeletionReview } from './ProviderActionResult';
import ProviderRegistrationFields from './ProviderRegistrationFields';
import { catalogueLabel, offeringEditor, providerEditor } from './providerManagementDraft';
import { isDisposableOfferingRow, strongEtag } from './providerManagementFlow';

function OfferingsTable({ model, filters }) {
    const provider = model.provider?.resource.data;
    const values = (options, records, key) => (records || []).map((item) => catalogueLabel(options, item[key])).join(', ');
    const rows = model.offerings.map((offering) => ({
        id: offering.offering_id,
        provider: provider.provider_name,
        offering: offering.offering_name,
        category: catalogueLabel(filters?.serviceCategories, offering.service_category),
        family: catalogueLabel(filters?.partFamilies, offering.part_family),
        parts: values(filters?.partTypes[offering.part_family], offering.supported_part_types, 'part_type'),
        materials: values(filters?.materials, offering.generic_capabilities?.materials, 'material'),
        processes: values(filters?.processes, offering.generic_capabilities?.processes, 'process'),
        canDelete: isDisposableOfferingRow(provider.provider_id, offering)
    }));
    return (
        <DataTable value={rows} dataKey="id" paginator={rows.length > 3} rows={3}
            selectionMode={model.busy ? undefined : 'single'} selection={rows.find(({ id }) => id === model.selection) || null}
            onSelectionChange={(event) => model.chooseOffering(event.value?.id)}
            responsiveLayout="scroll" stripedRows emptyMessage="No offerings loaded">
            <Column field="provider" header="Provider" sortable />
            <Column field="offering" header="Offering" sortable />
            <Column field="category" header="Service category" sortable />
            <Column field="family" header="Part family" sortable />
            <Column field="parts" header="Supported part types" />
            <Column field="materials" header="Materials" />
            <Column field="processes" header="Processes" />
            <Column header="Actions" body={(row) => row.canDelete && (
                <Button type="button" icon="pi pi-trash" severity="danger" text size="small" tooltip="Delete offering"
                    aria-label={'Delete offering ' + row.offering + ' (' + row.id + ')'}
                    disabled={model.offeringDeleteDisabled(row.id)}
                    onKeyDown={(event) => {
                        if (event.key === 'Enter' || event.key === ' ') event.stopPropagation();
                    }}
                    onClick={(event) => {
                        event.stopPropagation();
                        model.removeOffering(row.id);
                    }} />
            )} />
        </DataTable>
    );
}

export function ManagedFields({ entity, form, filters, errors = {}, idPrefix, ...props }) {
    const [serviceCollapsed, setServiceCollapsed] = useState(true);
    const [technicalCollapsed, setTechnicalCollapsed] = useState(true);
    const fieldsWithErrors = Object.keys(errors);
    return (
        <ProviderRegistrationFields mode={entity === 'add' ? 'add' : 'update'} form={form} filters={filters} errors={errors}
            showProvider={entity === 'provider'} showOffering={entity !== 'provider'} idPrefix={idPrefix || 'manage-' + entity}
            serviceCollapsed={serviceCollapsed && !fieldsWithErrors.some((field) => field.startsWith('customOfferingFields')
                || ['productionMode', 'industriesServed', 'otherServiceInformation'].includes(field))}
            technicalCollapsed={technicalCollapsed && !fieldsWithErrors.some((field) => field.startsWith('customCapabilityFields'))}
            setServiceCollapsed={setServiceCollapsed} setTechnicalCollapsed={setTechnicalCollapsed} {...props} />
    );
}

function RevisionReview({ entity, model, filters }) {
    const editor = model[entity];
    const recovery = editor?.recovery;
    if (!recovery && !editor?.previousDraft) return null;
    const label = entity === 'provider' ? 'provider' : 'offering';
    const latest = recovery?.observed?.resource;
    const published = recovery?.kind === 'accepted';
    const canContinueAdd = entity === 'add' && recovery?.kind === 'uncertain'
        && (recovery.observed?.kind === 'present' || (recovery.observed?.kind === 'absent' && !recovery.receipt?.publicationId));
    const toEditor = label === 'provider' ? providerEditor : offeringEditor;
    const latestEditor = latest && toEditor(latest);
    return (
        <>
            {recovery && (
                <Panel header={'Review current ' + label} className="mdc-registration-subsection">
                    <div className="flex flex-column gap-3">
                        <Message severity="warn" text={published
                            ? 'The write was accepted. Verify the current record to continue.'
                            : 'Your draft is preserved. Review the current record before trying another write.'} />
                        {recovery.observed?.kind === 'absent' && <p className="m-0">The requested record is absent on read-back.</p>}
                        {recovery.observed?.kind === 'unknown' && <p className="m-0">The current record could not be verified.</p>}
                        {latestEditor && (
                            <ManagedFields entity={label} form={latestEditor.draft} filters={filters} readOnly locked={latestEditor.locked}
                                idPrefix={'latest-' + label} />
                        )}
                        <div className="flex flex-wrap gap-2">
                            <Button type="button" label={'Check latest ' + label} icon="pi pi-refresh" outlined
                                disabled={Boolean(model.busy)} onClick={() => model.checkLatest(entity)} />
                            {entity !== 'add' && latest && (
                                <Button type="button" label={'Edit the latest ' + label + ' revision'}
                                    disabled={Boolean(model.busy) || !strongEtag(latest.etag)} onClick={() => model.useLatest(entity)} />
                            )}
                            {canContinueAdd && (
                                <Button type="button" label={latest ? 'Continue with a different offering ID' : 'Return to the offering draft'}
                                    disabled={Boolean(model.busy)} onClick={model.continueAdd} />
                            )}
                        </div>
                        {entity !== 'add' && latest && (
                            <p className="m-0 text-600">The latest revision becomes your editable draft. You can refer to your attempted edits while making changes.</p>
                        )}
                    </div>
                </Panel>
            )}
            {editor.previousDraft && (
                <Panel header={'Your attempted ' + label + ' edits'} className="mdc-registration-subsection" toggleable collapsed>
                    <div className="flex flex-column gap-3">
                        <ManagedFields entity={label} form={editor.previousDraft} filters={filters} readOnly locked={editor.previousLocked}
                            idPrefix={'attempted-' + label} />
                        <div>
                            <Button type="button" label="Dismiss attempted edits" outlined disabled={Boolean(model.busy)}
                                onClick={() => model.dismissAttempt(entity)} />
                        </div>
                    </div>
                </Panel>
            )}
        </>
    );
}

function SaveButton({ label, enabled, onClick }) {
    return <Button type="button" label={label} icon="pi pi-save" disabled={!enabled} onClick={onClick} />;
}

export default function ProviderManagement({ model, filters, filterError, retryFilters, registrationContext }) {
    const { provider, offering, add, manageable, busy } = model;
    const pending = Boolean(busy);
    const rejected = model.result?.kind === 'rejected' ? model.result : null;
    const errorsFor = (entity, changes) => ({
        ...(rejected?.request.operation === (entity === 'add' ? 'create' : 'save')
            && rejected.request.entity === (entity === 'add' ? 'offering' : entity) && rejected.errors),
        ...changes?.errors
    });
    const addErrors = errorsFor('add', model.newOffering);
    if (add?.duplicateId && add.duplicateId === model.newOffering.payload.offering_id) {
        addErrors.offeringId = 'This offering ID is already registered for a record. Choose a different ID.';
    }
    const providerData = provider?.resource.data;
    const offeringData = offering?.resource.data;
    return (
        <>
            {filterError && (
                <div className="flex flex-wrap align-items-center gap-2">
                    <Message severity="warn" text="The catalogue options could not be loaded." />
                    <Button type="button" label="Retry catalogue" disabled={pending} outlined onClick={retryFilters} />
                </div>
            )}
            <Card title="Update Existing Provider">
                <form className="flex flex-wrap align-items-end gap-2 mb-3" onSubmit={(event) => { event.preventDefault(); model.lookup(); }}>
                    <div className="flex flex-column gap-2">
                        <label htmlFor="providerLookup" className="font-medium">Provider ID to look up</label>
                        <InputText id="providerLookup" value={model.lookupId} disabled={pending} onChange={(event) => model.setLookupId(event.target.value)} />
                    </div>
                    <Button type="submit" label="Load provider" icon="pi pi-search" outlined disabled={pending || !model.lookupId.trim()} />
                    {manageable && !add && (
                        <Button type="button" label="Add offering" icon="pi pi-plus" outlined disabled={pending || !filters}
                            onClick={model.startAdd} />
                    )}
                </form>
                {providerData && <p className="mt-0"><strong>Loaded provider</strong> {providerData.provider_name} ({providerData.provider_id})</p>}
                {provider && !manageable && (
                    <Message severity="info" text="This provider is read-only. Changes are available for designated test records only." className="w-full mb-3" />
                )}
                <OfferingsTable model={model} filters={filters} />
                {offeringData && !add && <p className="mt-3 mb-0"><strong>Selected offering</strong> {offeringData.offering_name}</p>}
                {pending && <div role="status">{busy}…</div>}
                {registrationContext}
                <ProviderActionResult result={model.result} />
                {Object.entries(model.offeringDeletions).map(([id, recovery]) => (
                    <DeletionReview key={id} recovery={recovery} busy={pending}
                        onCheck={() => model.checkOfferingDeletion(id)} onResume={() => model.resumeOfferingActions(id)} />
                ))}
            </Card>

            {provider && (
                <fieldset disabled={pending} className="mdc-provider-registration flex flex-column gap-4 border-none p-0 m-0" aria-busy={pending}>
                    {manageable && !model.providerEditable && (
                        <Message severity="warn" text="Load a current provider revision to make edits." />
                    )}
                    <ManagedFields key={providerData.provider_id} entity="provider" form={provider.draft} filters={filters}
                        disabled={pending} readOnly={!model.providerEditable || Boolean(provider.recovery)} locked={provider.locked}
                        onChange={(draft) => model.change('provider', draft)} errors={errorsFor('provider', model.providerChanges)}
                        providerAction={model.providerEditable && (
                            <SaveButton label="Save provider" enabled={model.canSaveProvider} onClick={model.saveProvider} />
                        )} />
                    <RevisionReview entity="provider" model={model} filters={filters} />
                    {add && (
                        <>
                            <h2 className="my-0">Add offering</h2>
                            <ManagedFields entity="add" form={add.draft} filters={filters} errors={addErrors}
                                disabled={pending} readOnly={Boolean(add.recovery)} onChange={(draft) => model.change('add', draft)}
                                offeringAction={(
                                    <div className="flex flex-wrap gap-2">
                                        <Button type="button" label="Create offering" icon="pi pi-plus" disabled={!model.canCreate} onClick={model.addOffering} />
                                        <Button type="button" label="Cancel add offering" outlined disabled={pending} onClick={model.cancelAdd} />
                                    </div>
                                )} />
                            <RevisionReview entity="add" model={model} filters={filters} />
                        </>
                    )}
                    {offering && !add && (
                        <>
                            {model.manageableOffering && !model.offeringEditable && (
                                <Message severity="warn" text="Load a current offering revision to make edits." />
                            )}
                            <ManagedFields key={offeringData.offering_id} entity="offering" form={offering.draft} filters={filters}
                                disabled={pending} readOnly={!model.offeringEditable || Boolean(offering.recovery)} locked={offering.locked}
                                errors={errorsFor('offering', model.offeringChanges)} onChange={(draft) => model.change('offering', draft)}
                                offeringAction={model.offeringEditable && (
                                    <div><SaveButton label="Save offering" enabled={model.canSaveOffering} onClick={model.saveOffering} /></div>
                                )} />
                            <RevisionReview entity="offering" model={model} filters={filters} />
                        </>
                    )}
                </fieldset>
            )}
        </>
    );
}
