import React from 'react';
import Link from 'next/link';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { Divider } from 'primereact/divider';
import { Message } from 'primereact/message';
import { Tag } from 'primereact/tag';
import { useAuth } from '@/layout/context/AuthContext';
import {
    clearStoredDemoRole,
    getDemoRolesFromKeycloak,
    getPrimaryDemoRole,
    roleLabel,
    setStoredDemoRole,
    useSelectedDemoRole
} from '@/components/mdc/demoAuth';

const ROLE_OPTIONS = [
    {
        role: 'provider',
        label: 'Provider',
        icon: 'pi pi-building',
        description: 'Register providers and manage manufacturing capabilities.'
    },
    {
        role: 'consumer',
        label: 'Consumer',
        icon: 'pi pi-search',
        description: 'Search for suitable MaaS providers.'
    },
    {
        role: 'admin',
        label: 'Admin',
        icon: 'pi pi-shield',
        description: 'Review demo status and backend checks.'
    }
];

const WORKFLOW_CARDS = [
    {
        key: 'provider',
        title: 'Provider Area',
        icon: 'pi pi-building',
        description: 'Register a new provider or update existing provider capabilities.',
        action: 'Open Provider Area',
        href: '/demo/provider',
        roles: ['provider', 'admin']
    },
    {
        key: 'consumer',
        title: 'Service Discovery',
        icon: 'pi pi-search',
        description: 'Search for suitable providers and view catalogue or demo-overlay results.',
        action: 'Open Service Discovery',
        href: '/demo/consumer-search',
        roles: ['consumer', 'admin']
    },
    {
        key: 'admin',
        title: 'Demo Admin',
        icon: 'pi pi-shield',
        description: 'Review demo status and technical backend checks.',
        action: 'Open Demo Admin',
        href: '/demo/admin-audit',
        roles: ['admin']
    }
];

const RoleActions = ({ role }) => {
    if (role === 'admin') {
        return (
            <div className="flex flex-wrap gap-2">
                <Link href="/demo/provider"><Button label="Open Provider Area" icon="pi pi-building" /></Link>
                <Link href="/demo/consumer-search"><Button label="Open Service Discovery" icon="pi pi-search" outlined /></Link>
                <Link href="/demo/admin-audit"><Button label="Open Demo Admin" icon="pi pi-shield" outlined /></Link>
            </div>
        );
    }

    if (role === 'provider') {
        return (
            <Link href="/demo/provider">
                <Button label="Open Provider Area" icon="pi pi-building" />
            </Link>
        );
    }

    if (role === 'consumer') {
        return (
            <Link href="/demo/consumer-search">
                <Button label="Open Service Discovery" icon="pi pi-search" />
            </Link>
        );
    }

    return null;
};

const MdcDemoDashboard = () => {
    const { authenticated, isInitialized, isLoading, keycloak, roles, login, logout } = useAuth();
    const demoRoles = getDemoRolesFromKeycloak(keycloak, roles);
    const primaryRole = getPrimaryDemoRole(demoRoles);
    const selectedRole = useSelectedDemoRole();
    const selectedRoleAvailable = selectedRole && (demoRoles.includes(selectedRole) || demoRoles.includes('admin'));

    const availableRoles = primaryRole === 'admin'
        ? ROLE_OPTIONS
        : ROLE_OPTIONS.filter((option) => demoRoles.includes(option.role));
    const visibleWorkflowCards = selectedRole === 'admin' ? WORKFLOW_CARDS : [];

    const handleLogout = () => {
        clearStoredDemoRole();
        logout?.();
    };

    const renderRoleContent = () => {
        if (!isInitialized || isLoading) {
            return <Message severity="info" text="Checking login status..." className="w-full justify-content-start" />;
        }

        if (!authenticated) {
            return (
                <div className="flex flex-column gap-3">
                    <Message
                        severity="info"
                        text="Please login to continue as Provider or Consumer."
                        className="w-full justify-content-start"
                    />
                    <Button label="Login" icon="pi pi-sign-in" onClick={() => login?.()} className="w-fit" />
                </div>
            );
        }

        if (!primaryRole) {
            return (
                <Message
                    severity="warn"
                    text="You are logged in, but no MDC demo role was found. Please use a Keycloak user with Provider, Consumer or Admin demo role."
                    className="w-full justify-content-start"
                />
            );
        }

        if (selectedRole && !selectedRoleAvailable) {
            return (
                <div className="flex flex-column gap-3">
                    <Message
                        severity="warn"
                        text={`The selected demo role (${roleLabel(selectedRole)}) is not available for this login.`}
                        className="w-full justify-content-start"
                    />
                    <Button
                        label="Switch role"
                        icon="pi pi-refresh"
                        outlined
                        onClick={clearStoredDemoRole}
                        className="w-fit"
                    />
                </div>
            );
        }

        if (!selectedRole) {
            return (
                <div className="flex flex-column gap-3">
                    <div>
                        <h2 className="mt-0 mb-2 text-900">Continue demo as:</h2>
                    </div>
                    <div className="flex flex-column gap-3">
                        {availableRoles.map((option) => (
                            <div
                                key={option.role}
                                className="flex flex-column md:flex-row md:align-items-center justify-content-between gap-3 border-1 surface-border border-round p-3"
                            >
                                <div>
                                    <div className="font-semibold text-900 mb-1">{option.label}</div>
                                    <div className="text-600 line-height-3">{option.description}</div>
                                </div>
                                <Button
                                    label={option.label}
                                    icon={option.icon}
                                    onClick={() => setStoredDemoRole(option.role)}
                                    className="w-full md:w-auto"
                                />
                            </div>
                        ))}
                    </div>
                </div>
            );
        }

        const actionText = selectedRole === 'provider'
            ? 'Register a new provider or update existing manufacturing capabilities in the MaaS Dynamic Catalogue demo.'
            : selectedRole === 'consumer'
                ? 'Search for suitable manufacturing providers using part family, part type, material, process and requirement information.'
                : 'Open the provider, service discovery, or demo admin area.';

        return (
            <div className="flex flex-column gap-3">
                <div className="flex flex-column gap-2">
                    <div className="flex flex-wrap align-items-center gap-2">
                        <span className="text-600">Current demo role:</span>
                        <Tag value={roleLabel(selectedRole)} severity="info" />
                    </div>
                    <h2 className="mt-0 mb-2 text-900">Welcome {roleLabel(selectedRole)}</h2>
                    <p className="text-600 line-height-3 mb-0">{actionText}</p>
                </div>
                {selectedRole === 'admin' ? null : <RoleActions role={selectedRole} />}
                <div className="flex flex-wrap gap-2">
                    <Button
                        label="Switch role"
                        icon="pi pi-refresh"
                        outlined
                        onClick={clearStoredDemoRole}
                    />
                    <Button
                        label="Logout"
                        icon="pi pi-sign-out"
                        severity="secondary"
                        outlined
                        onClick={handleLogout}
                    />
                </div>
            </div>
        );
    };

    return (
        <div className="flex flex-column gap-4">
            <Card>
                <div className="flex flex-column md:flex-row md:align-items-start md:justify-content-between gap-3">
                    <div>
                        <div className="text-sm text-600 mb-2">MaaS Dynamic Catalogue</div>
                        <h1 className="mt-0 mb-2 text-900">MaaS Dynamic Catalogue Demo Console</h1>
                        <p className="text-600 line-height-3 mb-0">
                            Use this demo to show how manufacturing providers register capabilities,
                            how existing provider information can be updated, and how consumers search
                            for suitable MaaS providers.
                        </p>
                    </div>
                </div>
                <Divider />
                {renderRoleContent()}
            </Card>

            <div className="grid">
                {visibleWorkflowCards.map((card) => (
                    <div className="col-12 md:col-4" key={card.key}>
                        <Card>
                            <div className="flex flex-column gap-3 h-full">
                                <div className="flex align-items-center gap-2">
                                    <i className={`${card.icon} text-primary text-xl`} aria-hidden="true" />
                                    <h2 className="m-0 text-900 text-xl">{card.title}</h2>
                                </div>
                                <p className="text-600 line-height-3 m-0 flex-1">{card.description}</p>
                                <Link href={card.href}>
                                    <Button label={card.action} icon="pi pi-arrow-right" outlined className="w-full" />
                                </Link>
                            </div>
                        </Card>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default MdcDemoDashboard;
