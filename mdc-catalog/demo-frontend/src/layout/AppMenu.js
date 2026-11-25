import React from 'react';
import AppMenuitem from './AppMenuitem';
import { MenuProvider } from './context/menucontext';
import { useAuth } from './context/AuthContext';
import { canAccessRoute } from '@/config/routes';
import { getDemoRolesFromKeycloak, useSelectedDemoRole } from '@/components/mdc/demoAuth';

const MENU_MODEL = [
    {
        label: 'Home',
        items: [
            { label: 'Home', icon: 'pi pi-fw pi-home', to: '/' },
            { label: 'Contact', icon: 'pi pi-fw pi-envelope', to: '/home/Contact' },
            { label: 'Help', icon: 'pi pi-fw pi-question-circle', to: '/home/Help' }
        ]
    },
    {
        label: 'MaaS Dynamic Catalogue',
        items: [
            { label: 'Dashboard', icon: 'pi pi-fw pi-th-large', to: '/demo' },
            { label: 'Provider Area', icon: 'pi pi-fw pi-building', to: '/demo/provider', demoRoles: ['provider', 'admin'] },
            { label: 'Service Discovery', icon: 'pi pi-fw pi-search', to: '/demo/consumer-search', demoRoles: ['consumer', 'admin'] },
            { label: 'Demo Admin', icon: 'pi pi-fw pi-shield', to: '/demo/admin-audit', demoRoles: ['admin'] }
        ]
    }
];

const AppMenu = () => {
    const { authenticated, isInitialized, isLoading, keycloak, roles } = useAuth();
    const signedIn = isInitialized && !isLoading && authenticated;
    const demoRoles = getDemoRolesFromKeycloak(keycloak, roles);
    const selectedDemoRole = useSelectedDemoRole();
    const canUseSelectedRole = demoRoles.includes(selectedDemoRole) || demoRoles.includes('admin');

    // Filter each section: drop items the current user cannot access,
    // then drop empty sections.
    const model = MENU_MODEL
        .map((section) => ({
            ...section,
            items: section.items.filter((item) =>
                canAccessRoute(item.to, { authenticated: signedIn, roles })
                && (!item.demoRoles || (canUseSelectedRole && item.demoRoles.includes(selectedDemoRole)))
            )
        }))
        .filter((section) => section.items.length > 0);

    return (
        <MenuProvider>
            <ul className="layout-menu">
                {model.map((item, i) => {
                    if (item.separator) {
                        return <li key={`separator-${i}`} className="menu-separator"></li>;
                    }
                    return (
                        <AppMenuitem
                            item={item}
                            root={true}
                            index={i}
                            key={item.label}
                            authenticated={signedIn}
                        />
                    );
                })}
            </ul>
        </MenuProvider>
    );
};

export default AppMenu;
