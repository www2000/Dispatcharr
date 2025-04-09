// src/api.js (updated)
import useAuthStore from './store/auth';
import useChannelsStore from './store/channels';
import useUserAgentsStore from './store/userAgents';
import usePlaylistsStore from './store/playlists';
import useEPGsStore from './store/epgs';
import useStreamsStore from './store/streams';
import useStreamProfilesStore from './store/streamProfiles';
import useSettingsStore from './store/settings';

// If needed, you can set a base host or keep it empty if relative requests
const host = import.meta.env.DEV
  ? `http://${window.location.hostname}:5656`
  : '';

export default class API {
  /**
   * A static method so we can do:  await API.getAuthToken()
   */
  static async getAuthToken() {
    return await useAuthStore.getState().getToken();
  }

  static async fetchSuperUser() {
    const response = await fetch(`${host}/api/accounts/initialize-superuser/`);
    return await response.json();
  }

  static async createSuperUser({ username, email, password }) {
    const response = await fetch(`${host}/api/accounts/initialize-superuser/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username,
        password,
        email,
      }),
    });

    return await response.json();
  }

  static async login(username, password) {
    const response = await fetch(`${host}/api/accounts/token/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    return await response.json();
  }

  static async refreshToken(refresh) {
    const response = await fetch(`${host}/api/accounts/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });

    const retval = await response.json();
    return retval;
  }

  static async logout() {
    const response = await fetch(`${host}/api/accounts/auth/logout/`, {
      method: 'POST',
    });

    return response.data.data;
  }

  static async getChannels() {
    const response = await fetch(`${host}/api/channels/channels/`, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${await API.getAuthToken()}`,
      },
    });

    const retval = await response.json();
    return retval;
  }

  static async getChannelGroups() {
    const response = await fetch(`${host}/api/channels/groups/`, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${await API.getAuthToken()}`,
      },
    });

    const retval = await response.json();
    return retval;
  }

  static async addChannelGroup(values) {
    const response = await fetch(`${host}/api/channels/groups/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(values),
    });

    const retval = await response.json();
    if (retval.id) {
      useChannelsStore.getState().addChannelGroup(retval);
    }

    return retval;
  }

  static async updateChannelGroup(values) {
    const { id, ...payload } = values;
    const response = await fetch(`${host}/api/channels/groups/${id}/`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const retval = await response.json();
    if (retval.id) {
      useChannelsStore.getState().updateChannelGroup(retval);
    }

    return retval;
  }

  static async addChannel(channel) {
    let body = null;
    if (channel.logo_file) {
      // Must send FormData for file upload
      body = new FormData();
      for (const prop in channel) {
        body.append(prop, channel[prop]);
      }
    } else {
      body = { ...channel };
      delete body.logo_file;
      body = JSON.stringify(body);
    }

    const response = await fetch(`${host}/api/channels/channels/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        ...(channel.logo_file
          ? {}
          : {
            'Content-Type': 'application/json',
          }),
      },
      body: body,
    });

    const retval = await response.json();
    if (retval.id) {
      useChannelsStore.getState().addChannel(retval);
    }

    return retval;
  }

  static async deleteChannel(id) {
    const response = await fetch(`${host}/api/channels/channels/${id}/`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    useChannelsStore.getState().removeChannels([id]);
  }

  // @TODO: the bulk delete endpoint is currently broken
  static async deleteChannels(channel_ids) {
    const response = await fetch(`${host}/api/channels/channels/bulk-delete/`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ channel_ids }),
    });

    useChannelsStore.getState().removeChannels(channel_ids);
  }

  static async updateChannel(values) {
    const { id, ...payload } = values;

    let body = null;
    if (values.logo_file) {
      // Must send FormData for file upload
      body = new FormData();
      for (const prop in values) {
        body.append(prop, values[prop]);
      }
    } else {
      body = { ...values };
      delete body.logo_file;
      body = JSON.stringify(body);
    }

    console.log(body);

    const response = await fetch(`${host}/api/channels/channels/${id}/`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        ...(values.logo_file
          ? {}
          : {
            'Content-Type': 'application/json',
          }),
      },
      body: body,
    });

    const retval = await response.json();
    if (retval.id) {
      useChannelsStore.getState().updateChannel(retval);
    }

    return retval;
  }

  static async assignChannelNumbers(channelIds) {
    // Make the request
    const response = await fetch(`${host}/api/channels/channels/assign/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ channel_order: channelIds }),
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Assign channels failed: ${response.status} => ${text}`);
    }

    const retval = await response.json();

    // Optionally refresh the channel list in Zustand
    await useChannelsStore.getState().fetchChannels();

    return retval;
  }

  static async createChannelFromStream(values) {
    const response = await fetch(`${host}/api/channels/channels/from-stream/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(values),
    });

    const retval = await response.json();
    if (retval.id) {
      useChannelsStore.getState().addChannel(retval);
    }

    return retval;
  }

  static async createChannelsFromStreams(values) {
    const response = await fetch(
      `${host}/api/channels/channels/from-stream/bulk/`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${await API.getAuthToken()}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      }
    );

    const retval = await response.json();
    if (retval.created.length > 0) {
      useChannelsStore.getState().addChannels(retval.created);
    }

    return retval;
  }

  static async getStreams() {
    const response = await fetch(`${host}/api/channels/streams/`, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${await API.getAuthToken()}`,
      },
    });

    const retval = await response.json();
    return retval;
  }

  static async queryStreams(params) {
    const response = await fetch(
      `${host}/api/channels/streams/?${params.toString()}`,
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${await API.getAuthToken()}`,
        },
      }
    );

    const retval = await response.json();
    return retval;
  }

  static async getAllStreamIds(params) {
    const response = await fetch(
      `${host}/api/channels/streams/ids/?${params.toString()}`,
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${await API.getAuthToken()}`,
        },
      }
    );

    const retval = await response.json();
    return retval;
  }

  static async getStreamGroups() {
    const response = await fetch(`${host}/api/channels/streams/groups/`, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${await API.getAuthToken()}`,
      },
    });

    const retval = await response.json();
    return retval;
  }

  static async addStream(values) {
    const response = await fetch(`${host}/api/channels/streams/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(values),
    });

    const retval = await response.json();
    if (retval.id) {
      useStreamsStore.getState().addStream(retval);
    }

    return retval;
  }

  static async updateStream(values) {
    const { id, ...payload } = values;
    const response = await fetch(`${host}/api/channels/streams/${id}/`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const retval = await response.json();
    if (retval.id) {
      useStreamsStore.getState().updateStream(retval);
    }

    return retval;
  }

  static async deleteStream(id) {
    const response = await fetch(`${host}/api/channels/streams/${id}/`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    useStreamsStore.getState().removeStreams([id]);
  }

  static async deleteStreams(ids) {
    const response = await fetch(`${host}/api/channels/streams/bulk-delete/`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ stream_ids: ids }),
    });

    useStreamsStore.getState().removeStreams(ids);
  }

  static async getUserAgents() {
    const response = await fetch(`${host}/api/core/useragents/`, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${await API.getAuthToken()}`,
      },
    });

    const retval = await response.json();
    return retval;
  }

  static async addUserAgent(values) {
    const response = await fetch(`${host}/api/core/useragents/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(values),
    });

    const retval = await response.json();
    if (retval.id) {
      useUserAgentsStore.getState().addUserAgent(retval);
    }

    return retval;
  }

  static async updateUserAgent(values) {
    const { id, ...payload } = values;
    const response = await fetch(`${host}/api/core/useragents/${id}/`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const retval = await response.json();
    if (retval.id) {
      useUserAgentsStore.getState().updateUserAgent(retval);
    }

    return retval;
  }

  static async deleteUserAgent(id) {
    const response = await fetch(`${host}/api/core/useragents/${id}/`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    useUserAgentsStore.getState().removeUserAgents([id]);
  }

  static async getPlaylist(id) {
    const response = await fetch(`${host}/api/m3u/accounts/${id}/`, {
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    const retval = await response.json();
    return retval;
  }

  static async getPlaylists() {
    const response = await fetch(`${host}/api/m3u/accounts/`, {
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    const retval = await response.json();
    return retval;
  }

  static async addPlaylist(values) {
    let body = null;
    if (values.file) {
      body = new FormData();
      for (const prop in values) {
        body.append(prop, values[prop]);
      }
    } else {
      body = { ...values };
      delete body.file;
      body = JSON.stringify(body);
    }

    const response = await fetch(`${host}/api/m3u/accounts/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        ...(values.file
          ? {}
          : {
            'Content-Type': 'application/json',
          }),
      },
      body,
    });

    const retval = await response.json();
    if (retval.id) {
      usePlaylistsStore.getState().addPlaylist(retval);
    }

    return retval;
  }

  static async refreshPlaylist(id) {
    const response = await fetch(`${host}/api/m3u/refresh/${id}/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    const retval = await response.json();
    return retval;
  }

  static async refreshAllPlaylist() {
    const response = await fetch(`${host}/api/m3u/refresh/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    const retval = await response.json();
    return retval;
  }

  static async deletePlaylist(id) {
    const response = await fetch(`${host}/api/m3u/accounts/${id}/`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    usePlaylistsStore.getState().removePlaylists([id]);
    // @TODO: MIGHT need to optimize this later if someone has thousands of channels
    // but I'm feeling laze right now
    useChannelsStore.getState().fetchChannels();
  }

  static async updatePlaylist(values) {
    const { id, ...payload } = values;

    let body = null;
    if (payload.file) {
      delete payload.server_url;

      body = new FormData();
      for (const prop in values) {
        body.append(prop, values[prop]);
      }
    } else {
      delete payload.file;
      if (!payload.server_url) {
        delete payload.sever_url;
      }

      body = { ...payload };
      delete body.file;
      body = JSON.stringify(body);
    }

    const response = await fetch(`${host}/api/m3u/accounts/${id}/`, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        ...(values.file
          ? {}
          : {
            'Content-Type': 'application/json',
          }),
      },
      body,
    });

    const retval = await response.json();
    if (retval.id) {
      usePlaylistsStore.getState().updatePlaylist(retval);
    }

    return retval;
  }

  static async getEPGs() {
    const response = await fetch(`${host}/api/epg/sources/`, {
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    const retval = await response.json();
    return retval;
  }

  static async getEPGData() {
    const response = await fetch(`${host}/api/epg/epgdata/`, {
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    const retval = await response.json();
    return retval;
  }

  // Notice there's a duplicated "refreshPlaylist" method above;
  // you might want to rename or remove one if it's not needed.

  static async addEPG(values) {
    let body = null;
    if (values.files) {
      body = new FormData();
      for (const prop in values) {
        body.append(prop, values[prop]);
      }
    } else {
      body = { ...values };
      delete body.file;
      body = JSON.stringify(body);
    }

    const response = await fetch(`${host}/api/epg/sources/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        ...(values.epg_file
          ? {}
          : {
            'Content-Type': 'application/json',
          }),
      },
      body,
    });

    const retval = await response.json();
    if (retval.id) {
      useEPGsStore.getState().addEPG(retval);
    }

    return retval;
  }

  static async updateEPG(values) {
    const { id, ...payload } = values;

    let body = null;
    if (payload.files) {
      body = new FormData();
      for (const prop in payload) {
        if (prop == 'url') {
          continue;
        }
        body.append(prop, payload[prop]);
      }
    } else {
      delete payload.file;
      if (!payload.url) {
        delete payload.url;
      }
      body = JSON.stringify(payload);
    }

    const response = await fetch(`${host}/api/epg/sources/${id}/`, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        ...(values.epg_file
          ? {}
          : {
            'Content-Type': 'application/json',
          }),
      },
      body,
    });

    const retval = await response.json();
    if (retval.id) {
      useEPGsStore.getState().updateEPG(retval);
    }

    return retval;
  }

  static async deleteEPG(id) {
    const response = await fetch(`${host}/api/epg/sources/${id}/`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    useEPGsStore.getState().removeEPGs([id]);
  }

  static async refreshEPG(id) {
    const response = await fetch(`${host}/api/epg/import/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ id }),
    });

    const retval = await response.json();
    return retval;
  }

  static async getStreamProfiles() {
    const response = await fetch(`${host}/api/core/streamprofiles/`, {
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    const retval = await response.json();
    return retval;
  }

  static async addStreamProfile(values) {
    const response = await fetch(`${host}/api/core/streamprofiles/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(values),
    });

    const retval = await response.json();
    if (retval.id) {
      useStreamProfilesStore.getState().addStreamProfile(retval);
    }
    return retval;
  }

  static async updateStreamProfile(values) {
    const { id, ...payload } = values;
    const response = await fetch(`${host}/api/core/streamprofiles/${id}/`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const retval = await response.json();
    if (retval.id) {
      useStreamProfilesStore.getState().updateStreamProfile(retval);
    }

    return retval;
  }

  static async deleteStreamProfile(id) {
    const response = await fetch(`${host}/api/core/streamprofiles/${id}/`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    useStreamProfilesStore.getState().removeStreamProfiles([id]);
  }

  static async getGrid() {
    const response = await fetch(`${host}/api/epg/grid/`, {
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    const retval = await response.json();
    return retval.data;
  }

  static async addM3UProfile(accountId, values) {
    const response = await fetch(
      `${host}/api/m3u/accounts/${accountId}/profiles/`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${await API.getAuthToken()}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      }
    );

    const retval = await response.json();
    if (retval.id) {
      // Refresh the playlist
      const playlist = await API.getPlaylist(accountId);
      usePlaylistsStore
        .getState()
        .updateProfiles(playlist.id, playlist.profiles);
    }

    return retval;
  }

  static async deleteM3UProfile(accountId, id) {
    const response = await fetch(
      `${host}/api/m3u/accounts/${accountId}/profiles/${id}/`,
      {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${await API.getAuthToken()}`,
          'Content-Type': 'application/json',
        },
      }
    );

    const playlist = await API.getPlaylist(accountId);
    usePlaylistsStore.getState().updatePlaylist(playlist);
  }

  static async updateM3UProfile(accountId, values) {
    const { id, ...payload } = values;
    const response = await fetch(
      `${host}/api/m3u/accounts/${accountId}/profiles/${id}/`,
      {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${await API.getAuthToken()}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      }
    );

    const playlist = await API.getPlaylist(accountId);
    usePlaylistsStore.getState().updateProfiles(playlist.id, playlist.profiles);
  }

  static async getSettings() {
    const response = await fetch(`${host}/api/core/settings/`, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${await API.getAuthToken()}`,
      },
    });

    const retval = await response.json();
    return retval;
  }

  static async getEnvironmentSettings() {
    const response = await fetch(`${host}/api/core/settings/env/`, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${await API.getAuthToken()}`,
      },
    });

    const retval = await response.json();
    return retval;
  }

  static async updateSetting(values) {
    const { id, ...payload } = values;
    const response = await fetch(`${host}/api/core/settings/${id}/`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const retval = await response.json();
    if (retval.id) {
      useSettingsStore.getState().updateSetting(retval);
    }

    return retval;
  }

  static async getChannelStats(uuid = null) {
    const response = await fetch(`${host}/proxy/ts/status`, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${await API.getAuthToken()}`,
      },
    });

    const retval = await response.json();
    return retval;
  }

  static async stopChannel(id) {
    const response = await fetch(`${host}/proxy/ts/stop/${id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${await API.getAuthToken()}`,
      },
    });

    const retval = await response.json();
    return retval;
  }

  static async stopClient(channelId, clientId) {
    const response = await fetch(`${host}/proxy/ts/stop_client/${channelId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${await API.getAuthToken()}`,
      },
      body: JSON.stringify({ client_id: clientId }),
    });

    const retval = await response.json();
    return retval;
  }

  static async matchEpg() {
    const response = await fetch(`${host}/api/channels/channels/match-epg/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${await API.getAuthToken()}`,
      },
    });

    const retval = await response.json();
    return retval;
  }

  static async getLogos() {
    const response = await fetch(`${host}/api/channels/logos/`, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${await API.getAuthToken()}`,
      },
    });

    const retval = await response.json();
    return retval;
  }

  static async uploadLogo(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${host}/api/channels/logos/upload/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
      },
      body: formData,
    });

    const retval = await response.json();

    useChannelsStore.getState().addLogo(retval);

    return retval;
  }

  static async getChannelProfiles() {
    const response = await fetch(`${host}/api/channels/profiles/`, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${await API.getAuthToken()}`,
      },
    });

    const retval = await response.json();
    return retval;
  }

  static async addChannelProfile(values) {
    const response = await fetch(`${host}/api/channels/profiles/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(values),
    });

    const retval = await response.json();
    if (retval.id) {
      useChannelsStore.getState().addProfile(retval);
    }

    return retval;
  }

  static async updateChannelProfile(values) {
    const { id, ...payload } = values;
    const response = await fetch(`${host}/api/channels/profiles/${id}/`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const retval = await response.json();
    if (retval.id) {
      useChannelsStore.getState().updateProfile(retval);
    }

    return retval;
  }

  static async deleteChannelProfile(id) {
    const response = await fetch(`${host}/api/channels/profiles/${id}/`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    useChannelsStore.getState().removeProfiles([id]);
  }

  static async updateProfileChannel(channelId, profileId, enabled) {
    const response = await fetch(
      `${host}/api/channels/profiles/${profileId}/channels/${channelId}/`,
      {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${await API.getAuthToken()}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enabled }),
      }
    );

    useChannelsStore
      .getState()
      .updateProfileChannels([channelId], profileId, enabled);
  }

  static async updateProfileChannels(channelIds, profileId, enabled) {
    const response = await fetch(
      `${host}/api/channels/profiles/${profileId}/channels/bulk-update/`,
      {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${await API.getAuthToken()}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          channels: channelIds.map((id) => ({
            channel_id: id,
            enabled,
          })),
        }),
      }
    );

    useChannelsStore
      .getState()
      .updateProfileChannels(channelIds, profileId, enabled);
  }

  static async getRecordings() {
    const response = await fetch(`${host}/api/channels/recordings/`, {
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    const retval = await response.json();

    return retval;
  }

  static async createRecording(values) {
    const response = await fetch(`${host}/api/channels/recordings/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(values),
    });

    const retval = await response.json();
    useChannelsStore.getState().fetchRecordings();

    return retval;
  }

  static async deleteRecording(id) {
    const response = await fetch(`${host}/api/channels/recordings/${id}/`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    useChannelsStore.getState().fetchRecordings();
  }

  // Download Manager API methods
  static async getDownloadTasks() {
    const response = await fetch(`${host}/api/downloads/tasks/`, {
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    return await response.json();
  }

  static async getDownloadTask(id) {
    const response = await fetch(`${host}/api/downloads/tasks/${id}/`, {
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    return await response.json();
  }

  static async createDownloadTask(values) {
    const response = await fetch(`${host}/api/downloads/tasks/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(values),
    });

    return await response.json();
  }

  static async updateDownloadTask(id, values) {
    const response = await fetch(`${host}/api/downloads/tasks/${id}/`, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(values),
    });

    return await response.json();
  }

  static async deleteDownloadTask(id) {
    const response = await fetch(`${host}/api/downloads/tasks/${id}/`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
      },
    });

    return response.ok;
  }

  static async triggerDownload(id) {
    const response = await fetch(`${host}/api/downloads/tasks/${id}/trigger/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    return await response.json();
  }

  static async getDownloadTaskHistory(id) {
    const response = await fetch(`${host}/api/downloads/tasks/${id}/history/`, {
      headers: {
        Authorization: `Bearer ${await API.getAuthToken()}`,
        'Content-Type': 'application/json',
      },
    });

    return await response.json();
  }
}
