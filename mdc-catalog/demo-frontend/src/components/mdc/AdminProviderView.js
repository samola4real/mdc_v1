import React, { useEffect, useState } from 'react';
import { Dialog } from 'primereact/dialog';
import { Dropdown } from 'primereact/dropdown';
import { Message } from 'primereact/message';
import { getOffering, getProvider, listProviderOfferings } from '@/services/mdc/provider.service';
import { ManagedFields } from './ProviderManagement';
import { offeringEditor, providerEditor } from './providerManagementDraft';
import { exactOffering, loadManagementSnapshot } from './providerManagementFlow';

const services = { getOffering, getProvider, listProviderOfferings };

function ProviderDetails({ providerId, filters }) {
    const [view, setView] = useState(null);
    const [requestedId, setRequestedId] = useState(null);
    const [selected, setSelected] = useState(null);
    const snapshot = view?.snapshot;
    const offeringId = requestedId ?? snapshot?.offering?.data.offering_id;

    useEffect(() => {
        let active = true;
        loadManagementSnapshot(providerId, undefined, services)
            .then((result) => { if (active) setView({ snapshot: result }); })
            .catch(() => { if (active) setView({ failed: true }); });
        return () => { active = false; };
    }, [providerId]);

    useEffect(() => {
        if (!requestedId) return undefined;
        let active = true;
        exactOffering(providerId, requestedId, services)
            .then((resource) => { if (active) setSelected({ id: requestedId, resource }); })
            .catch(() => { if (active) setSelected({ id: requestedId, failed: true }); });
        return () => { active = false; };
    }, [providerId, requestedId]);

    if (!view) return <p role="status">Loading provider details…</p>;
    if (view.failed) return <Message severity="error" text="The provider details could not be loaded. Close this view and load the provider again." />;

    const offeringResult = requestedId
        ? (selected?.id === requestedId ? selected : null) : { resource: snapshot.offering };
    const provider = providerEditor(snapshot.provider);
    const offering = offeringResult?.resource && offeringEditor(offeringResult.resource);
    const options = snapshot.list.offerings.map((row) => ({ value: row.offering_id, label: row.offering_name || row.offering_id }));
    const selectOffering = (id) => {
        if (id === offeringId || !options.some((option) => option.value === id)) return;
        setSelected(null);
        setRequestedId(id);
    };

    return (
        <div className="mdc-provider-registration mdc-admin-view-details">
            <ManagedFields entity="provider" form={provider.draft} filters={filters} readOnly locked={provider.locked}
                idPrefix="admin-view-provider" />
            {options.length > 0 ? (
                <div className="mdc-admin-view-offering">
                    <label htmlFor="adminProviderViewOffering">Offering to view</label>
                    <Dropdown inputId="adminProviderViewOffering" value={offeringId} options={options}
                        onChange={(event) => selectOffering(event.value)} appendTo="self" />
                </div>
            ) : <p className="m-0">This provider has no offerings.</p>}
            {offeringId && !offeringResult && <p role="status">Loading offering details…</p>}
            {offeringResult?.failed && <Message severity="error" text="The selected offering could not be loaded." />}
            {offering && <ManagedFields key={offeringId} entity="offering" form={offering.draft} filters={filters}
                readOnly locked={offering.locked} idPrefix="admin-view-offering" />}
        </div>
    );
}

export default function AdminProviderView({ providerId, filters, visible, onHide }) {
    return (
        <Dialog id="adminProviderDetails" className="mdc-admin-provider-view" header="Provider details" visible={visible} modal
            draggable={false} resizable={false} onHide={onHide}>
            {visible && <ProviderDetails key={providerId} providerId={providerId} filters={filters} />}
        </Dialog>
    );
}
