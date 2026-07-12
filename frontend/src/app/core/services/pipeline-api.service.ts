import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PipelineService {
 
  private http = inject(HttpClient);
  
  private readonly apiUrl = 'http://localhost:8000/api/pipeline';

  /**
   * Dispatches a POST instruction to activate the raw JSON data ingestion pipeline runner [3.4, 4.3].
   */
  triggerPipeline(): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/run`, {});
  }

  /**
   * Connects to GET /api/pipeline/runs to fetch historical ingestion metrics cycles logs [4].
   */
  getPipelineRuns(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/runs`);
  }
}
