import { create } from 'zustand';
import api from '../api';

const useEPGsStore = create((set) => ({
  epgs: {},
  tvgs: [],
  tvgsById: {},
  isLoading: false,
  error: null,

  fetchEPGs: async () => {
    set({ isLoading: true, error: null });
    try {
      const epgs = await api.getEPGs();
      set({
        epgs: epgs.reduce((acc, epg) => {
          acc[epg.id] = epg;
          return acc;
        }, {}),
        isLoading: false,
      });
    } catch (error) {
      console.error('Failed to fetch epgs:', error);
      set({ error: 'Failed to load epgs.', isLoading: false });
    }
  },

  fetchEPGData: async () => {
    set({ isLoading: true, error: null });
    try {
      const tvgs = await api.getEPGData();

      // Check if tvgs is actually an array
      if (!Array.isArray(tvgs)) {
        console.error('Expected TVGs to be an array but got:', typeof tvgs, tvgs);
        set({
          tvgs: [],
          tvgsById: {},
          isLoading: false,
          error: 'Invalid EPG data format received from server'
        });
        return;
      }

      set({
        tvgs: tvgs,
        tvgsById: tvgs.reduce((acc, tvg) => {
          acc[tvg.id] = tvg;
          return acc;
        }, {}),
        isLoading: false,
      });
    } catch (error) {
      console.error('Failed to fetch tvgs:', error);
      set({
        tvgs: [],
        tvgsById: {},
        isLoading: false,
        error: 'Failed to load EPG data.'
      });
    }
  },

  addEPG: (epg) =>
    set((state) => ({
      epgs: { ...state.epgs, [epg.id]: epg },
    })),

  updateEPG: (epg) =>
    set((state) => ({
      epgs: { ...state.epgs, [epg.id]: epg },
    })),

  removeEPGs: (epgIds) =>
    set((state) => {
      const updatedEPGs = { ...state.epgs };
      for (const id of epgIds) {
        delete updatedEPGs[id];
      }

      return { epgs: updatedEPGs };
    }),
}));

export default useEPGsStore;
