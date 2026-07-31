// Built-in sample datasets, bundled with the frontend so the Samples tab
// works instantly even when the backend is asleep or unreachable.
// Mirrors backend/app/core/constants.py.

import type { SampleDatasetResponse } from './types'

export const SAMPLE_DATASETS: SampleDatasetResponse[] = [
  {
    id: 'spring',
    name: 'Spring Load Test',
    description: 'Extension of a steel spring under increasing load. Near-perfect linear behavior.',
    model: 'linear',
    n: 12,
    x: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    y: [2.9, 5.1, 6.8, 9.2, 10.9, 13.1, 14.8, 17.2, 18.9, 21.1, 22.8, 25.2],
  },
  {
    id: 'projectile',
    name: 'Projectile Arc',
    description: 'Height of a projectile sampled over time. Classic quadratic trajectory.',
    model: 'polynomial',
    n: 11,
    x: [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5],
    y: [1.2, 5.6, 9.1, 11.4, 12.9, 13.2, 12.6, 10.8, 8.2, 4.5, 0.1],
  },
  {
    id: 'bacteria',
    name: 'Bacterial Growth',
    description: 'Colony population measured hourly. Textbook exponential growth curve.',
    model: 'exponential',
    n: 11,
    x: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    y: [12.1, 16.4, 22.0, 30.1, 40.4, 54.6, 73.9, 99.2, 134.6, 181.1, 245.0],
  },
]
