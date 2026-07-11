import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { DroneRecord } from '../models/drone-record.model';

@Injectable({
  providedIn: 'root'
})
export class DroneApiService {
  private readonly apiUrl = 'http://localhost:8000/api/drones';

  constructor(private readonly http: HttpClient) {}

  getDrones(): Observable<DroneRecord[]> {
    return this.http.get<DroneRecord[]>(this.apiUrl);
  }
}