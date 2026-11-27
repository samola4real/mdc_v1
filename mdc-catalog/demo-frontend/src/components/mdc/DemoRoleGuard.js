import React from 'react';
import Button from './MaaSAIButton';
import { Card } from 'primereact/card';
import { Message } from 'primereact/message';
import { useAuth } from '@/layout/context/AuthContext';
import {
    canAccessDemoRole,
    getDemoRolesFromKeycloak,
    getPrimaryDemoRole,
    roleLabel,
    useSelectedDemoRole
} from './demoAuth';

const LoginPrompt = ({ login }) => (
    <Card>
        <div className="flex flex-column gap-3">
            <div>
                <h2 className="mt-0 mb-2 text-900">Sign in to MaaS Dynamic Catalogue</h2>
                <p className="text-600 line-height-3 mb-0">
                    Sign in with your MaaSAI account to continue.
                </p>
            </div>
            <Button label="Sign in" icon="pi pi-sign-in" onClick={() => login?.()} className="w-fit" />
        </div>
    </Card>
);

const DemoRoleGuard = ({ allowedRoles = [], children, pageLabel }) => {
    const { authenticated, isInitialized, isLoading, keycloak, roles, login } = useAuth();
    const demoRoles = getDemoRolesFromKeycloak(keycloak, roles);
    const primaryRole = getPrimaryDemoRole(demoRoles);
    const selectedRole = useSelectedDemoRole();
    const canUseSelectedRole = selectedRole && (demoRoles.includes(selectedRole) || demoRoles.includes('admin'));
    const allowed = canUseSelectedRole && canAccessDemoRole([selectedRole], allowedRoles);

    if (!isInitialized || isLoading) {
        return <Message severity="info" text="Checking sign-in status..." className="w-full justify-content-start" />;
    }

    if (!authenticated) {
        return <LoginPrompt login={login} />;
    }

    if (!primaryRole) {
        return (
            <Message
                severity="warn"
                text="Your account needs a Provider, Consumer or Admin role to use the catalogue."
                className="w-full justify-content-start"
            />
        );
    }

    if (!selectedRole) {
        return (
            <Message
                severity="info"
                text="Choose a role on the Dashboard before opening this page."
                className="w-full justify-content-start"
            />
        );
    }

    if (!canUseSelectedRole) {
        return (
            <Message
                severity="warn"
                text={`Your account cannot use the ${roleLabel(selectedRole)} role. Switch role on the Dashboard.`}
                className="w-full justify-content-start"
            />
        );
    }

    if (!allowed) {
        const labels = allowedRoles.map(roleLabel).join(' / ');
        return (
            <Message
                severity="warn"
                text={`This page requires the ${pageLabel || labels} role. Your selected role is ${roleLabel(selectedRole)}.`}
                className="w-full justify-content-start"
            />
        );
    }

    return children;
};

export default DemoRoleGuard;
