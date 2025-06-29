import React, { useState, useEffect, useRef } from 'react';
import useChannelsStore from '../../store/channels';
import API from '../../api';
import useStreamProfilesStore from '../../store/streamProfiles';
import ChannelGroupForm from './ChannelGroup';
import {
  Box,
  Button,
  Modal,
  TextInput,
  Text,
  Group,
  ActionIcon,
  Flex,
  Select,
  Stack,
  useMantineTheme,
  Popover,
  ScrollArea,
  Tooltip,
  UnstyledButton,
  Center,
} from '@mantine/core';
import { ListOrdered, SquarePlus, SquareX, X } from 'lucide-react';
import { FixedSizeList as List } from 'react-window';
import { useForm } from '@mantine/form';
import { USER_LEVELS, USER_LEVEL_LABELS } from '../../constants';

const ChannelBatchForm = ({ channelIds, isOpen, onClose }) => {
  const theme = useMantineTheme();

  const groupListRef = useRef(null);

  const channelGroups = useChannelsStore((s) => s.channelGroups);
  const streamProfiles = useStreamProfilesStore((s) => s.profiles);

  const [channelGroupModelOpen, setChannelGroupModalOpen] = useState(false);
  const [selectedChannelGroup, setSelectedChannelGroup] = useState('');

  const [groupPopoverOpened, setGroupPopoverOpened] = useState(false);
  const [groupFilter, setGroupFilter] = useState('');
  const groupOptions = Object.values(channelGroups);

  const form = useForm({
    mode: 'uncontrolled',
    initialValues: {
      channel_group: '',
      stream_profile_id: '0',
      user_level: '-1',
    },
  });

  const onSubmit = async () => {
    const values = {
      ...form.getValues(),
      channel_group_id: selectedChannelGroup,
    };

    if (!values.stream_profile_id || values.stream_profile_id === '0') {
      values.stream_profile_id = null;
    }

    if (!values.channel_group_id) {
      delete values.channel_group_id;
    }

    if (values.user_level == '-1') {
      delete values.user_level;
    }

    await API.batchUpdateChannels({
      ids: channelIds,
      values,
    });
  };

  // useEffect(() => {
  //   // const sameStreamProfile = channels.every(
  //   //   (channel) => channel.stream_profile_id == channels[0].stream_profile_id
  //   // );
  //   // const sameChannelGroup = channels.every(
  //   //   (channel) => channel.channel_group_id == channels[0].channel_group_id
  //   // );
  //   // const sameUserLevel = channels.every(
  //   //   (channel) => channel.user_level == channels[0].user_level
  //   // );
  //   // form.setValues({
  //   //   ...(sameStreamProfile && {
  //   //     stream_profile_id: `${channels[0].stream_profile_id}`,
  //   //   }),
  //   //   ...(sameChannelGroup && {
  //   //     channel_group_id: `${channels[0].channel_group_id}`,
  //   //   }),
  //   //   ...(sameUserLevel && {
  //   //     user_level: `${channels[0].user_level}`,
  //   //   }),
  //   // });
  // }, [channelIds, streamProfiles, channelGroups]);

  const handleChannelGroupModalClose = (newGroup) => {
    setChannelGroupModalOpen(false);

    if (newGroup && newGroup.id) {
      setSelectedChannelGroup(newGroup.id);
      form.setValues({
        channel_group: `${newGroup.name}`,
      });
    }
  };

  const filteredGroups = groupOptions.filter((group) =>
    group.name.toLowerCase().includes(groupFilter.toLowerCase())
  );

  if (!isOpen) {
    return <></>;
  }

  return (
    <>
      <Modal
        opened={isOpen}
        onClose={onClose}
        size="xs"
        title={
          <Group gap="5">
            <ListOrdered size="20" />
            <Text>Channels</Text>
          </Group>
        }
        styles={{ hannontent: { '--mantine-color-body': '#27272A' } }}
      >
        <form onSubmit={form.onSubmit(onSubmit)}>
          <Group justify="space-between" align="top">
            <Stack gap="5" style={{ flex: 1 }}>
              <Popover
                opened={groupPopoverOpened}
                onChange={setGroupPopoverOpened}
                // position="bottom-start"
                withArrow
              >
                <Popover.Target>
                  <Group style={{ width: '100%' }} align="flex-end">
                    <TextInput
                      id="channel_group"
                      name="channel_group"
                      label="Channel Group"
                      readOnly
                      {...form.getInputProps('channel_group')}
                      key={form.key('channel_group')}
                      onClick={() => setGroupPopoverOpened(true)}
                      size="xs"
                      style={{ flex: 1 }}
                    />

                    <ActionIcon
                      color={theme.tailwind.green[5]}
                      onClick={() => setChannelGroupModalOpen(true)}
                      title="Create new group"
                      size="small"
                      variant="transparent"
                      style={{ marginBottom: 5 }}
                    >
                      <SquarePlus size="20" />
                    </ActionIcon>
                  </Group>
                </Popover.Target>

                <Popover.Dropdown onMouseDown={(e) => e.stopPropagation()}>
                  <Group style={{ width: '100%' }} spacing="xs">
                    <TextInput
                      placeholder="Filter"
                      value={groupFilter}
                      onChange={(event) =>
                        setGroupFilter(event.currentTarget.value)
                      }
                      mb="xs"
                      size="xs"
                      style={{ flex: 1 }}
                    />

                    <ActionIcon
                      color={theme.tailwind.green[5]}
                      onClick={() => setChannelGroupModalOpen(true)}
                      title="Create new group"
                      size="small"
                      variant="transparent"
                      style={{ marginBottom: 5 }}
                    >
                      <SquarePlus size="20" />
                    </ActionIcon>
                  </Group>

                  <ScrollArea style={{ height: 200 }}>
                    <List
                      height={200} // Set max height for visible items
                      itemCount={filteredGroups.length}
                      itemSize={20} // Adjust row height for each item
                      width={200}
                      ref={groupListRef}
                    >
                      {({ index, style }) => (
                        <Box
                          style={{ ...style, height: 20, overflow: 'hidden' }}
                        >
                          <Tooltip
                            openDelay={500}
                            label={filteredGroups[index].name}
                            size="xs"
                          >
                            <UnstyledButton
                              onClick={() => {
                                setSelectedChannelGroup(
                                  filteredGroups[index].id
                                );
                                form.setValues({
                                  channel_group: filteredGroups[index].name,
                                });
                                setGroupPopoverOpened(false);
                              }}
                            >
                              <Text
                                size="xs"
                                style={{
                                  whiteSpace: 'nowrap',
                                  overflow: 'hidden',
                                  textOverflow: 'ellipsis',
                                }}
                              >
                                {filteredGroups[index].name}
                              </Text>
                            </UnstyledButton>
                          </Tooltip>
                        </Box>
                      )}
                    </List>
                  </ScrollArea>
                </Popover.Dropdown>
              </Popover>

              <Select
                id="stream_profile_id"
                label="Stream Profile"
                name="stream_profile_id"
                {...form.getInputProps('stream_profile_id')}
                key={form.key('stream_profile_id')}
                data={[{ value: '0', label: '(use default)' }].concat(
                  streamProfiles.map((option) => ({
                    value: `${option.id}`,
                    label: option.name,
                  }))
                )}
                size="xs"
              />

              <Select
                size="xs"
                label="User Level Access"
                {...form.getInputProps('user_level')}
                key={form.key('user_level')}
                data={[
                  {
                    value: '-1',
                    label: '(no change)',
                  },
                ].concat(
                  Object.entries(USER_LEVELS).map(([label, value]) => {
                    return {
                      label: USER_LEVEL_LABELS[value],
                      value: `${value}`,
                    };
                  })
                )}
              />
            </Stack>
          </Group>

          <Flex mih={50} gap="xs" justify="flex-end" align="flex-end">
            <Button type="submit" variant="default" disabled={form.submitting}>
              Submit
            </Button>
          </Flex>
        </form>
      </Modal>

      <ChannelGroupForm
        isOpen={channelGroupModelOpen}
        onClose={handleChannelGroupModalClose}
      />
    </>
  );
};

export default ChannelBatchForm;
