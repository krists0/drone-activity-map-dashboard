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
  current_page = 1;
  current_page_pipeline = 1;
  page_size_pipeline= 10;
  hasNextPagePipeline = true;
  private droneApiService = inject(DroneApiService);
  private pipelineApiService = inject(PipelineService);
  private cdr = inject(ChangeDetectorRef);
  clearCounter = 0;
  drones: DroneRecord[] = [];
  pipelineRuns: any[] = [];


  ngOnInit(): void {
    this.loadDronesFromBackend();
    this.loadLatestPipelineRunLog();
  }

  onFiltersChanged(activeFilters: any): void {
    const backendFilters: any = {
      drone_type: activeFilters.drone_type,
      status: activeFilters.status,
      operator_id: activeFilters.operator_id,
      min_battery: activeFilters.min_battery,
      max_battery: activeFilters.max_battery
    };

    if (activeFilters.from_date && activeFilters.from_date !== '') {
      backendFilters.from_date = `${activeFilters.from_date}T00:00:00Z`;
    }

    if (activeFilters.to_date && activeFilters.to_date !== '') {
      backendFilters.to_date = `${activeFilters.to_date}T23:59:59Z`;
    }

    this.loadDronesFromBackend(backendFilters);
  }

  private loadDronesFromBackend(filters: any = {}): void {
    this.droneApiService.getDrones(filters).subscribe({
      next: (data: DroneRecord[]) => {
        this.drones = [...data];
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Network Error: Failed to fetch filtered drones from Python backend', err);
      }
    });
  }

  onPipelineTriggered(): void {
    this.pipelineApiService.triggerPipeline().subscribe({
      next: (response: any) => {
        console.log('Pipeline executed successfully via UI button request!', response);
        this.current_page_pipeline = 1;
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

  private loadLatestPipelineRunLog(): void {
    this.pipelineApiService.getPipelineRuns().subscribe({
      next: (runs: any[]) => {
        this.pipelineRuns = runs;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Failed to load pipeline runs log', err);
      }
    });
  }

  
 
  
  nextPage(): void {
    this.current_page += 1;
    this.loadDronesFromBackend({ page: this.current_page });
  }

  previousPage(): void {
    if (this.current_page > 1) {
      this.current_page -= 1;
      this.loadDronesFromBackend({ page: this.current_page });
  }
  }
  onPageChangedPipeline(newPage: number): void {
    this.current_page_pipeline = newPage;
    this.loadPipelineRuns();
  }
  private loadPipelineRuns(): void {
    this.pipelineApiService
      .getPipelineRuns(this.current_page_pipeline, this.page_size_pipeline)
      .subscribe({
        next: (runs: any[]) => {
          this.pipelineRuns = runs;
          this.hasNextPagePipeline = runs.length === this.page_size_pipeline;
          this.cdr.detectChanges();
        },
        error: (err) => {
          console.error('Failed to load pipeline runs log', err);
        }
      });
  }
}