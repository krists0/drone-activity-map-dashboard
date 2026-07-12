
import { CommonModule } from '@angular/common';
import { DroneMapComponent } from '../../components/drone-map/drone-map';
import { FilterPanelComponent } from '../../components/filter-panel/filter-panel';
import { DroneApiService } from '../../../../core/services/drone-api.service';
import { DroneRecord } from '../../../../core/models/drone-record.model';
import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { PipelineRunsTable } from '../../components/pipeline-runs-table/pipeline-runs-table';
import { PipelineService } from '../../../../core/services/pipeline-api.service';

@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [
    CommonModule, 
    DroneMapComponent, 
    FilterPanelComponent,
    PipelineRunsTable
  ],
  templateUrl: './dashboard-page.html',
  styleUrls: ['./dashboard-page.scss']
})
export class DashboardPageComponent implements OnInit {
  
  private droneApiService = inject(DroneApiService);
  private pipelineApiService = inject(PipelineService);
  private cdr = inject(ChangeDetectorRef);
  drones: DroneRecord[] = [];
  latestRun: any = null;
  ngOnInit(): void {
    this.loadDronesFromBackend();
  }


  /**
   * Listens directly to the filter submission outputs emitted from the child panel component.
   * Fires a fresh tailored HTTP network payload request every single time Apply Filters is clicked.
   * @param activeFilters Lowercase parameter tokens mapped directly from the filter form controls
   */
  onFiltersChanged(activeFilters: any): void {
  
    const backendFilters: any = {
      drone_type: activeFilters.drone_type,
      status: activeFilters.status,
      operator_id: activeFilters.operator_id,
      min_battery: activeFilters.min_battery
    };

    if (activeFilters.from_date && activeFilters.from_date !== '') {
      backendFilters.from_date = `${activeFilters.from_date}T00:00:00Z`;
    }

    if (activeFilters.to_date && activeFilters.to_date !== '') {
      backendFilters.to_date = `${activeFilters.to_date}T23:59:59Z`;
    }

    // Trigger the official HTTP request stream with the remapped parameter configurations [4.2]
    this.loadDronesFromBackend(backendFilters);
  }

  
  private loadDronesFromBackend(filters: any = {}): void {
    this.droneApiService.getDrones(filters).subscribe({
      next: (data: DroneRecord[]) => {
        this.drones = [...data];
        // Forces Angular to push the new input into DroneMapComponent immediately
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Network Error: Failed to fetch filtered drones from Python backend', err);
      }
    });
  }

  onPipelineTriggered(): void {
    // We call the post ingestion router engine from your API service layer
    this.pipelineApiService.triggerPipeline().subscribe({
      next: (response: any) => {
        console.log('Pipeline executed successfully via UI button request!', response);
        // Refresh both the map markers list data indices and pipeline run counter displays [4.3]
        this.refreshDashboardData();
      },
      error: (err: any) => {
        console.error('Pipeline Trigger Failed: Backend server integration error', err);
      }
    });
  }

  private refreshDashboardData(): void {
    this.loadDronesFromBackend();
    this.loadLatestPipelineRunLog();
  }

  /**
   * Queries historical telemetry processing cycles to populate UI tracking tables [4.3]
   */
  private loadLatestPipelineRunLog(): void {
    this.pipelineApiService.getPipelineRuns().subscribe({
      next: (runs: any[]) => {
        //Extract the first array item securely INSIDE the network subscribe event block [4.3]
        if (runs && runs.length > 0) {
          this.latestRun = runs[0];
          this.cdr.detectChanges();
        }
      },
      error: (err) => {
        console.error('Failed to load pipeline runs log', err);
      }
    });
  }
}
