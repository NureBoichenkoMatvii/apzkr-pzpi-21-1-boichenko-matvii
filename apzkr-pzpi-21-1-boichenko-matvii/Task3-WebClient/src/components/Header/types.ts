import { UserRole } from "@api/client";

export enum NavbarItemAuthRequirement {
    AuthRequired,
    NoAuthRequired
}

export interface NavbarItem {
    label: string;
    iconPath?: string;
    children?: Array<NavbarItem>;
    href?: string;
    isAuthRequired?: boolean;
    roles?: UserRole[];
}

export interface DeviceSpecificNavbarProps {
    navbarItems: Array<NavbarItem>
}
