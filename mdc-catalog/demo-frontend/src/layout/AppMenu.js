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
            { label: 'Help', icon: 'pi pi-fw pi-question-circle', to: '/home/Help' },
            { label: 'Brand', icon: 'pi pi-fw pi-palette', to: '/home/Brand' }
        ]
    },
    {
        label: 'Workspace',
        items: [
            { label: 'Config',     icon: 'pi pi-fw pi-cog',         to: '/home/EmptyPage' },
            { label: 'Charts',     icon: 'pi pi-fw pi-chart-bar',   to: '/workspace/charts' },
            { label: 'Table',      icon: 'pi pi-fw pi-table',       to: '/workspace/crud' },
            { label: 'Agents',     icon: 'pi pi-fw pi-th-large',    to: '/workspace/agents' },
            { label: 'Monitor',    icon: 'pi pi-fw pi-desktop',     to: '/workspace/monitor' },
            { label: 'Scheduler',  icon: 'pi pi-fw pi-calendar',    to: '/workspace/scheduler' },
            { label: 'Analytics',  icon: 'pi pi-fw pi-chart-line',  to: '/workspace/analytics' },
            { label: 'Designer',   icon: 'pi pi-fw pi-sitemap',     to: '/workspace/designer' }
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
    const { authenticated, keycloak, roles } = useAuth();
    const demoRoles = getDemoRolesFromKeycloak(keycloak, roles);
    const selectedDemoRole = useSelectedDemoRole();

    const demoUser = authenticated && demoRoles.length > 0;
    const visibleSections = demoUser
        ? MENU_MODEL.filter((section) => section.label === 'MaaS Dynamic Catalogue')
        : MENU_MODEL;

    const canSeeDemoItem = (item) => {
        if (!item.demoRoles) {
            return true;
        }
        if (!authenticated) {
            return false;
        }
        if (!selectedDemoRole) {
            return false;
        }

        const canUseSelectedRole = demoRoles.includes(selectedDemoRole) || demoRoles.includes('admin');
        return canUseSelectedRole && item.demoRoles.includes(selectedDemoRole);
    };

    // Filter each section: drop items the current user cannot access,
    // then drop empty sections.
    const model = visibleSections
        .map((section) => ({
            ...section,
            items: (section.items || []).filter((item) =>
                canAccessRoute(item.to, { authenticated, roles }) && canSeeDemoItem(item)
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
                            authenticated={authenticated}
                        />
                    );
                })}
            </ul>
        </MenuProvider>
    );
};

export default AppMenu;
