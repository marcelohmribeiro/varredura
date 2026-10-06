import { create } from 'zustand'

const useScrapingStore = create((set, get) => ({
  jobs: [],

  addJobs: (newJobs) =>
    set((state) => ({ jobs: [...newJobs, ...state.jobs] })),

  updateJob: (jobId, patch) =>
    set((state) => ({
      jobs: state.jobs.map((j) => (j.jobId === jobId ? { ...j, ...patch } : j)),
    })),

  updateJobByKey: (key, patch) =>
    set((state) => ({
      jobs: state.jobs.map((j) => (j._key === key ? { ...j, ...patch } : j)),
    })),

  clearDone: () =>
    set((state) => ({
      jobs: state.jobs.filter((j) => j.status !== 'done' && j.status !== 'error'),
    })),
}))

export default useScrapingStore
