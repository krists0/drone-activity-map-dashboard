export type DroneStatus = 'active' | 'flying' | 'lost_signal';

export interface DroneRecord {
  id: number;

  drone_id: string;
  drone_type: string;
  operator_id: string;

  latitude: number;
  longitude: number;

  altitude_m: number;
  speed_kmh: number;
  battery_percent: number;

  timestamp: string;
  status: DroneStatus;
}