import React from 'react';
import { Button } from 'primereact/button';
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
                <h2 className="mt-0 mb-2 text-900">MDC Demo Console</h2>
                <p className="text-600 line-height-3 mb-0">
                    Please login to continue as Provider or Consumer.
                </p>
            </div>
            <Button label="Login" icon="pi pi-sign-in" onClick={() => login?.()} className="w-fit" />
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
        return <Message severity="info" text="Checking login status..." className="w-full justify-content-start" />;
    }

    if (!authenticated) {
        return <LoginPrompt login={login} />;
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

    if (!selectedRole) {
        return (
            <Message
                severity="info"
                text="Choose Provider, Consumer or Admin on the MDC Demo Console before opening this demo page."
                className="w-full justify-content-start"
            />
        );
    }

    if (!canUseSelectedRole) {
        return (
            <Message
                severity="warn"
                text={`Your selected demo role (${roleLabel(selectedRole)}) is not available for this Keycloak user. Switch role on the MDC Demo Console.`}
                className="w-full justify-content-start"
            />
        );
    }

    if (!allowed) {
        const labels = allowedRoles.map(roleLabel).join(' / ');
        return (
            <Message
                severity="warn"
                text={`This page is for ${pageLabel || labels}. Your selected MDC demo role is ${roleLabel(selectedRole)}.`}
                className="w-full justify-content-start"
            />
        );
    }

    return children;
};

export default DemoRoleGuard;
