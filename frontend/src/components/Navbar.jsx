import React from 'react';
import { Link } from 'react-router-dom';
import { IconHome, IconSettings, IconDownload } from '@tabler/icons-react';

const Navbar = () => {
    const navLinks = [
        {
            link: '/',
            label: 'Home',
            icon: IconHome,
        },
        {
            link: '/settings',
            label: 'Settings',
            icon: IconSettings,
        },
        {
            link: '/downloads',
            label: 'Downloads',
            icon: IconDownload,
        },
    ];

    return (
        <nav>
            <ul>
                {navLinks.map((navLink) => (
                    <li key={navLink.link}>
                        <Link to={navLink.link}>
                            <navLink.icon />
                            {navLink.label}
                        </Link>
                    </li>
                ))}
            </ul>
        </nav>
    );
};

export default Navbar;