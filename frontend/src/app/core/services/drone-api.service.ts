import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { DroneRecord } from '../models/drone-record.model';

@Injectable({
  providedIn: 'root'
})
export class DroneApiService {
  private readonly apiUrl = 'http://localhost:8000/api/drones';

  constructor(private readonly http: HttpClient) {}

//   getDrones(): Observable<DroneRecord[]> {
//     return this.http.get<DroneRecord[]>(this.apiUrl);
//   }
getDrones(filters: any = {}): Observable<DroneRecord[]> {
    let params = new HttpParams();

    // Map each existing active field directly to server parameter keys safely
    if (filters.drone_type) {
      params = params.set('drone_type', filters.drone_type);
    }
    if (filters.status) {
      params = params.set('status', filters.status);
    }
    if (filters.operator_id) {
      params = params.set('operator_id', filters.operator_id);
    }
    if (filters.min_battery) {
      params = params.set('min_battery', filters.min_battery.toString());
    }
    if (filters.from_date) {
      params = params.set('from_date', filters.from_date);
    }
    if (filters.to_date) {
      params = params.set('to_date', filters.to_date);
    }

    // Sends the payload over the wire: GET /api/drones?status=active&min_battery=50
    return this.http.get<DroneRecord[]>(this.apiUrl, { params });
  }
}