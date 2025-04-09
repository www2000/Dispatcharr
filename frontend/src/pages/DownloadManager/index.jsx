import React, { useState, useEffect } from 'react';
import {
    Container,
    Group,
    Title,
    Table,
    Button,
    Text,
    Badge,
    ActionIcon,
    Modal,
    TextInput,
    Select,
    NumberInput,
    Stack,
    Switch,
    Tooltip,
    ScrollArea,
    Menu,
    rem,
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';
import {
    IconPlus,
    IconDownload,
    IconEdit,
    IconTrash,
    IconRefresh,
    IconDotsVertical,
    IconClock
} from '@tabler/icons-react';
import { useWebSocket } from '../../WebSocket';
import API from '../../api';
import { formatFileSize, formatDate } from '../../utils/formatters';

// Format download speed
const formatSpeed = (speedBps) => {
    if (!speedBps) return 'N/A';

    const units = ['B/s', 'KB/s', 'MB/s', 'GB/s'];
    let speed = speedBps;
    let unitIndex = 0;

    while (speed >= 1024 && unitIndex < units.length - 1) {
        speed /= 1024;
        unitIndex++;
    }

    return `${speed.toFixed(2)} ${units[unitIndex]}`;
};

// Status badge component
const StatusBadge = ({ status, speed }) => {
    const colorMap = {
        idle: 'blue',
        scheduled: 'yellow',
        downloading: 'green',
        success: 'teal',
        failed: 'red',
    };

    let content = status;
    if (status === 'downloading' && speed) {
        content = `Downloading (${formatSpeed(speed)})`;
    }

    return (
        <Badge color={colorMap[status] || 'gray'}>
            {content}
        </Badge>
    );
};

export default function DownloadManager() {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [modalOpened, { open: openModal, close: closeModal }] = useDisclosure(false);
    const [currentTask, setCurrentTask] = useState(null);
    const [formValues, setFormValues] = useState({
        name: '',
        url: '',
        download_type: 'epg',
        frequency: 'daily',
        hour: 0,
        minute: 0,
        day_of_week: 0,
        day_of_month: 1,
        custom_filename: '',
        is_active: true,
        user_agent: '',
    });

    const { wsMessages } = useWebSocket();

    // Handle WebSocket messages
    useEffect(() => {
        if (wsMessages && wsMessages.type === 'download_status') {
            const { task_id, status, progress, speed, error } = wsMessages;

            // Update task status
            setTasks(prevTasks =>
                prevTasks.map(task =>
                    task.id === task_id
                        ? {
                            ...task,
                            status,
                            latest_history: {
                                ...task.latest_history,
                                status,
                                download_speed: speed || task.latest_history?.download_speed,
                                error_message: error || task.latest_history?.error_message
                            }
                        }
                        : task
                )
            );

            // Show notification for completed downloads
            if (status === 'success' || status === 'failed') {
                const task = tasks.find(t => t.id === task_id);
                if (task) {
                    notifications.show({
                        title: status === 'success' ? 'Download Complete' : 'Download Failed',
                        message: status === 'success'
                            ? `Successfully downloaded ${task.name}`
                            : `Failed to download ${task.name}: ${error}`,
                        color: status === 'success' ? 'green' : 'red',
                    });
                }
            }
        }
    }, [wsMessages]);

    // Fetch download tasks
    const fetchTasks = async () => {
        try {
            setLoading(true);
            const data = await API.getDownloadTasks();
            setTasks(data);
        } catch (error) {
            console.error('Error fetching download tasks:', error);
            notifications.show({
                title: 'Error',
                message: 'Failed to load download tasks',
                color: 'red',
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTasks();
    }, []);

    // Form submission handler
    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            // Log the form values for debugging
            console.log("Form submission values:", formValues);

            // Ensure numeric values are actually numbers, not strings
            const formattedValues = {
                ...formValues,
                hour: Number(formValues.hour),
                minute: Number(formValues.minute),
                day_of_week: formValues.day_of_week !== null ? Number(formValues.day_of_week) : null,
                day_of_month: formValues.day_of_month !== null ? Number(formValues.day_of_month) : null,
                // Make sure other fields are properly formatted
                is_active: Boolean(formValues.is_active),
                custom_headers: formValues.custom_headers || {},
            };

            console.log("Formatted values:", formattedValues);

            if (currentTask) {
                await API.updateDownloadTask(currentTask.id, formattedValues);
                notifications.show({
                    title: 'Success',
                    message: 'Download task updated successfully',
                    color: 'green',
                });
            } else {
                await API.createDownloadTask(formattedValues);
                notifications.show({
                    title: 'Success',
                    message: 'Download task created successfully',
                    color: 'green',
                });
            }

            closeModal();
            fetchTasks();
        } catch (error) {
            console.error('Error saving download task:', error);

            // Create a more user-friendly error message
            const errorMessage = error.message || 'Unknown error occurred';

            notifications.show({
                title: 'Error',
                message: errorMessage,
                color: 'red',
                autoClose: false,
            });
        }
    };

    // Edit task handler
    const handleEditTask = (task) => {
        setCurrentTask(task);
        setFormValues({
            name: task.name,
            url: task.url,
            download_type: task.download_type,
            frequency: task.frequency,
            hour: task.hour,
            minute: task.minute,
            day_of_week: task.day_of_week || 0,
            day_of_month: task.day_of_month || 1,
            custom_filename: task.custom_filename || '',
            is_active: task.is_active,
            user_agent: task.user_agent || '',
        });
        openModal();
    };

    // Add new task handler
    const handleAddTask = () => {
        setCurrentTask(null);
        setFormValues({
            name: '',
            url: '',
            download_type: 'epg',
            frequency: 'daily',
            hour: 0,
            minute: 0,
            day_of_week: 0,
            day_of_month: 1,
            custom_filename: '',
            is_active: true,
            user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        });
        openModal();
    };

    // Trigger download handler
    const handleTriggerDownload = async (id) => {
        try {
            await API.triggerDownload(id);
            notifications.show({
                title: 'Download Scheduled',
                message: 'Download has been triggered',
                color: 'blue',
            });
            fetchTasks();
        } catch (error) {
            console.error('Error triggering download:', error);
            notifications.show({
                title: 'Error',
                message: 'Failed to trigger download',
                color: 'red',
            });
        }
    };

    // Delete task handler
    const handleDeleteTask = async (id) => {
        if (!confirm('Are you sure you want to delete this download task?')) {
            return;
        }

        try {
            await API.deleteDownloadTask(id);
            notifications.show({
                title: 'Success',
                message: 'Download task deleted successfully',
                color: 'green',
            });
            fetchTasks();
        } catch (error) {
            console.error('Error deleting download task:', error);
            notifications.show({
                title: 'Error',
                message: 'Failed to delete download task',
                color: 'red',
            });
        }
    };

    // Debug function to check logs (you can add a debug button for this)
    const checkServerLogs = async () => {
        try {
            const response = await fetch(`${API.host}/api/debug/logs/`, {
                headers: {
                    Authorization: `Bearer ${await API.getAuthToken()}`,
                },
            });

            const logs = await response.text();
            console.log("Server logs:", logs);

            // You could display these in a modal if needed
        } catch (error) {
            console.error("Failed to fetch logs:", error);
        }
    };

    // Render frequency options based on selection
    const renderFrequencyOptions = () => {
        switch (formValues.frequency) {
            case 'weekly':
                return (
                    <Group grow>
                        <Select
                            label="Day of Week"
                            value={formValues.day_of_week.toString()}
                            onChange={(value) => setFormValues({ ...formValues, day_of_week: parseInt(value) })}
                            data={[
                                { value: '0', label: 'Monday' },
                                { value: '1', label: 'Tuesday' },
                                { value: '2', label: 'Wednesday' },
                                { value: '3', label: 'Thursday' },
                                { value: '4', label: 'Friday' },
                                { value: '5', label: 'Saturday' },
                                { value: '6', label: 'Sunday' },
                            ]}
                        />
                        <NumberInput
                            label="Hour (0-23)"
                            min={0}
                            max={23}
                            value={formValues.hour}
                            onChange={(value) => setFormValues({ ...formValues, hour: value })}
                        />
                        <NumberInput
                            label="Minute (0-59)"
                            min={0}
                            max={59}
                            value={formValues.minute}
                            onChange={(value) => setFormValues({ ...formValues, minute: value })}
                        />
                    </Group>
                );
            case 'monthly':
                return (
                    <Group grow>
                        <NumberInput
                            label="Day of Month (1-31)"
                            min={1}
                            max={31}
                            value={formValues.day_of_month}
                            onChange={(value) => setFormValues({ ...formValues, day_of_month: value })}
                        />
                        <NumberInput
                            label="Hour (0-23)"
                            min={0}
                            max={23}
                            value={formValues.hour}
                            onChange={(value) => setFormValues({ ...formValues, hour: value })}
                        />
                        <NumberInput
                            label="Minute (0-59)"
                            min={0}
                            max={59}
                            value={formValues.minute}
                            onChange={(value) => setFormValues({ ...formValues, minute: value })}
                        />
                    </Group>
                );
            case 'hourly':
                return (
                    <Group grow>
                        <NumberInput
                            label="Minute (0-59)"
                            min={0}
                            max={59}
                            value={formValues.minute}
                            onChange={(value) => setFormValues({ ...formValues, minute: value })}
                        />
                    </Group>
                );
            case 'daily':
            default:
                return (
                    <Group grow>
                        <NumberInput
                            label="Hour (0-23)"
                            min={0}
                            max={23}
                            value={formValues.hour}
                            onChange={(value) => setFormValues({ ...formValues, hour: value })}
                        />
                        <NumberInput
                            label="Minute (0-59)"
                            min={0}
                            max={59}
                            value={formValues.minute}
                            onChange={(value) => setFormValues({ ...formValues, minute: value })}
                        />
                    </Group>
                );
        }
    };

    return (
        <Container size="xl">
            <Group position="apart" mb="md">
                <Title order={2}>Download Manager</Title>
                <Button
                    leftIcon={<IconPlus size={16} />}
                    onClick={handleAddTask}
                >
                    Add Download
                </Button>
            </Group>

            <ScrollArea>
                <Table striped highlightOnHover>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Frequency</th>
                            <th>Status</th>
                            <th>Last Download</th>
                            <th>Next Download</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {tasks.length === 0 && !loading ? (
                            <tr>
                                <td colSpan={7} style={{ textAlign: 'center', padding: '20px' }}>
                                    <Text color="dimmed">No download tasks found. Click "Add Download" to create one.</Text>
                                </td>
                            </tr>
                        ) : (
                            tasks.map((task) => (
                                <tr key={task.id}>
                                    <td>{task.name}</td>
                                    <td>
                                        <Badge color={
                                            task.download_type === 'epg' ? 'blue' :
                                                task.download_type === 'm3u' ? 'green' : 'grape'
                                        }>
                                            {task.download_type.toUpperCase()}
                                        </Badge>
                                    </td>
                                    <td>
                                        <Group spacing="xs">
                                            <Text size="sm">{task.frequency}</Text>
                                            <Tooltip label={`${task.hour}:${task.minute.toString().padStart(2, '0')}`}>
                                                <ActionIcon size="xs" variant="subtle">
                                                    <IconClock stroke={1.5} />
                                                </ActionIcon>
                                            </Tooltip>
                                        </Group>
                                    </td>
                                    <td>
                                        <StatusBadge
                                            status={task.status}
                                            speed={task.latest_history?.download_speed}
                                        />
                                    </td>
                                    <td>
                                        {task.last_run ? (
                                            <Tooltip label={formatDate(task.last_run, true)}>
                                                <Text size="sm">{formatDate(task.last_run)}</Text>
                                            </Tooltip>
                                        ) : (
                                            <Text size="sm" color="dimmed">Never</Text>
                                        )}
                                    </td>
                                    <td>
                                        {task.next_run ? (
                                            <Tooltip label={formatDate(task.next_run, true)}>
                                                <Text size="sm">{formatDate(task.next_run)}</Text>
                                            </Tooltip>
                                        ) : (
                                            <Text size="sm" color="dimmed">Not scheduled</Text>
                                        )}
                                    </td>
                                    <td>
                                        <Group spacing={0} position="right">
                                            <ActionIcon
                                                color="blue"
                                                onClick={() => handleTriggerDownload(task.id)}
                                                disabled={task.status === 'downloading'}
                                            >
                                                <IconDownload size="1.125rem" />
                                            </ActionIcon>
                                            <Menu>
                                                <Menu.Target>
                                                    <ActionIcon>
                                                        <IconDotsVertical size="1.125rem" />
                                                    </ActionIcon>
                                                </Menu.Target>
                                                <Menu.Dropdown>
                                                    <Menu.Item
                                                        icon={<IconEdit size={rem(14)} />}
                                                        onClick={() => handleEditTask(task)}
                                                    >
                                                        Edit
                                                    </Menu.Item>
                                                    <Menu.Item
                                                        icon={<IconRefresh size={rem(14)} />}
                                                        onClick={() => handleTriggerDownload(task.id)}
                                                        disabled={task.status === 'downloading'}
                                                    >
                                                        Download now
                                                    </Menu.Item>
                                                    <Menu.Divider />
                                                    <Menu.Item
                                                        color="red"
                                                        icon={<IconTrash size={rem(14)} />}
                                                        onClick={() => handleDeleteTask(task.id)}
                                                    >
                                                        Delete
                                                    </Menu.Item>
                                                </Menu.Dropdown>
                                            </Menu>
                                        </Group>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </Table>
            </ScrollArea>

            {/* Add/Edit Task Modal */}
            <Modal
                opened={modalOpened}
                onClose={closeModal}
                title={currentTask ? 'Edit Download Task' : 'Add Download Task'}
                size="lg"
            >
                <form onSubmit={handleSubmit}>
                    <Stack spacing="md">
                        <TextInput
                            label="Name"
                            placeholder="Enter a name for this download task"
                            value={formValues.name}
                            onChange={(e) => setFormValues({ ...formValues, name: e.target.value })}
                            required
                        />
                        <TextInput
                            label="URL"
                            placeholder="Enter the download URL"
                            value={formValues.url}
                            onChange={(e) => setFormValues({ ...formValues, url: e.target.value })}
                            required
                        />
                        <Select
                            label="Download Type"
                            value={formValues.download_type}
                            onChange={(value) => setFormValues({ ...formValues, download_type: value })}
                            data={[
                                { value: 'epg', label: 'EPG (XMLTV)' },
                                { value: 'm3u', label: 'M3U Playlist' },
                                { value: 'custom', label: 'Custom File' },
                            ]}
                            required
                        />
                        <Select
                            label="Frequency"
                            value={formValues.frequency}
                            onChange={(value) => setFormValues({ ...formValues, frequency: value })}
                            data={[
                                { value: 'hourly', label: 'Hourly' },
                                { value: 'daily', label: 'Daily' },
                                { value: 'weekly', label: 'Weekly' },
                                { value: 'monthly', label: 'Monthly' },
                            ]}
                            required
                        />
                        {renderFrequencyOptions()}
                        <TextInput
                            label="Custom Filename (Optional)"
                            placeholder="Leave blank to use original filename"
                            value={formValues.custom_filename}
                            onChange={(e) => setFormValues({ ...formValues, custom_filename: e.target.value })}
                        />
                        <TextInput
                            label="User Agent (Optional)"
                            placeholder="Custom user agent string"
                            value={formValues.user_agent}
                            onChange={(e) => setFormValues({ ...formValues, user_agent: e.target.value })}
                        />
                        <Switch
                            label="Active"
                            checked={formValues.is_active}
                            onChange={(e) => setFormValues({ ...formValues, is_active: e.currentTarget.checked })}
                        />
                        <Group position="right">
                            <Button variant="default" onClick={closeModal}>Cancel</Button>
                            <Button type="submit">{currentTask ? 'Update' : 'Create'}</Button>
                        </Group>
                    </Stack>
                </form>
            </Modal>
        </Container>
    );
}
