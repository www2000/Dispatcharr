import React, { useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  ListOrdered,
  Play,
  Database,
  SlidersHorizontal,
  LayoutGrid,
  Settings as LucideSettings,
  Copy,
  ChartLine,
  Video,
  Download,
} from 'lucide-react';
import {
  Avatar,
  AppShell,
  Group,
  Stack,
  Box,
  Text,
  UnstyledButton,
  TextInput,
  ActionIcon,
} from '@mantine/core';
import logo from '../images/logo.png';
import useChannelsStore from '../store/channels';
import './sidebar.css';
import useSettingsStore from '../store/settings';

const NavLink = ({ item, isActive, collapsed }) => {
  return (
    <UnstyledButton
      key={item.path}
      component={Link}
      to={item.path}
      className={`navlink ${isActive ? 'navlink-active' : ''} ${collapsed ? 'navlink-collapsed' : ''}`}
    >
      {item.icon}
      {!collapsed && (
        <Text
          sx={{
            opacity: collapsed ? 0 : 1,
            transition: 'opacity 0.2s ease-in-out',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            minWidth: collapsed ? 0 : 150,
          }}
        >
          {item.label}
        </Text>
      )}
      {!collapsed && item.badge && (
        <Text size="sm" style={{ color: '#D4D4D8', whiteSpace: 'nowrap' }}>
          {item.badge}
        </Text>
      )}
    </UnstyledButton>
  );
};

const Sidebar = ({ collapsed, toggleDrawer, drawerWidth, miniDrawerWidth }) => {
  const location = useLocation();
  const { channels } = useChannelsStore();
  const { environment } = useSettingsStore();
  const publicIPRef = useRef(null);

  // Navigation Items
  const navItems = [
    {
      label: 'Channels',
      icon: <ListOrdered size={20} />,
      path: '/channels',
      badge: `(${Object.keys(channels).length})`,
    },
    { label: 'M3U', icon: <Play size={20} />, path: '/m3u' },
    { label: 'EPG', icon: <Database size={20} />, path: '/epg' },
    {
      label: 'Stream Profiles',
      icon: <SlidersHorizontal size={20} />,
      path: '/stream-profiles',
    },
    { label: 'TV Guide', icon: <LayoutGrid size={20} />, path: '/guide' },
    { label: 'DVR', icon: <Video size={20} />, path: '/dvr' },
    { label: 'Stats', icon: <ChartLine size={20} />, path: '/stats' },
    {
      label: 'Settings',
      icon: <LucideSettings size={20} />,
      path: '/settings',
    },
    { label: 'Downloads', icon: <Download size={20} />, path: '/downloads' },
  ];

  const copyPublicIP = async () => {
    try {
      await navigator.clipboard.writeText(environment.public_ip);
    } catch (err) {
      const inputElement = publicIPRef.current; // Get the actual input
      console.log(inputElement);

      if (inputElement) {
        inputElement.focus();
        inputElement.select();

        // For older browsers
        document.execCommand('copy');
      }
    }
  };

  return (
    <AppShell.Navbar
      width={{ base: collapsed ? miniDrawerWidth : drawerWidth }}
      p="xs"
      style={{
        backgroundColor: '#1A1A1E',
        // transition: 'width 0.3s ease',
        borderRight: '1px solid #2A2A2E',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Brand - Click to Toggle */}
      <Group
        onClick={toggleDrawer}
        spacing="sm"
        style={{
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          padding: '16px 12px',
          fontSize: 18,
          fontWeight: 600,
          color: '#FFFFFF',
          justifyContent: collapsed ? 'center' : 'flex-start',
          whiteSpace: 'nowrap',
        }}
      >
        {/* <ListOrdered size={24} /> */}
        <img width={30} src={logo} />
        {!collapsed && (
          <Text
            sx={{
              opacity: collapsed ? 0 : 1,
              transition: 'opacity 0.2s ease-in-out',
              whiteSpace: 'nowrap', // Ensures text never wraps
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              minWidth: collapsed ? 0 : 150, // Prevents reflow
            }}
          >
            Dispatcharr
          </Text>
        )}
      </Group>

      {/* Navigation Links */}
      <Stack gap="xs" mt="lg">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;

          return (
            <NavLink item={item} collapsed={collapsed} isActive={isActive} />
          );
        })}
      </Stack>

      {/* Profile Section */}
      <Box
        style={{
          marginTop: 'auto',
          padding: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          borderTop: '1px solid #2A2A2E',
          justifyContent: collapsed ? 'center' : 'flex-start',
        }}
      >
        <Group>
          {!collapsed && (
            <TextInput
              label="Public IP"
              ref={publicIPRef}
              value={environment.public_ip}
              leftSection={
                environment.country_code && (
                  <img
                    src={`https://flagcdn.com/16x12/${environment.country_code.toLowerCase()}.png`}
                    alt={environment.country_name || environment.country_code}
                    title={environment.country_name || environment.country_code}
                  />
                )
              }
              rightSection={
                <ActionIcon
                  variant="transparent"
                  color="gray.9"
                  onClick={copyPublicIP}
                >
                  <Copy />
                </ActionIcon>
              }
            />
          )}

          <Avatar src="https://via.placeholder.com/40" radius="xl" />
          {!collapsed && (
            <Group
              style={{
                flex: 1,
                justifyContent: 'space-between',
                whiteSpace: 'nowrap',
              }}
            >
              <Text size="sm" color="white">
                John Doe
              </Text>
              <Text size="sm" color="white">
                •••
              </Text>
            </Group>
          )}
        </Group>
      </Box>
    </AppShell.Navbar>
  );
};

export default Sidebar;
