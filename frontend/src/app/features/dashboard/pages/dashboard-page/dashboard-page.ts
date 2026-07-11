
import { CommonModule } from '@angular/common';
import { DroneMapComponent } from '../../components/drone-map/drone-map';
import { FilterPanelComponent } from '../../components/filter-panel/filter-panel';
import { DroneApiService } from '../../../../core/services/drone-api.service';
import { DroneRecord } from '../../../../core/models/drone-record.model';
import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [
    CommonModule, 
    DroneMapComponent, 
    FilterPanelComponent
  ],
  templateUrl: './dashboard-page.html',
  styleUrls: ['./dashboard-page.scss']
})
export class DashboardPageComponent implements OnInit {
  
  private droneApiService = inject(DroneApiService);
  private cdr = inject(ChangeDetectorRef);
  drones: DroneRecord[] = [];

  ngOnInit(): void {
    this.loadDronesFromBackend();
  }


  /**
   * Listens directly to the filter submission outputs emitted from the child panel component.
   * Fires a fresh tailored HTTP network payload request every single time Apply Filters is clicked.
   * @param activeFilters Lowercase parameter tokens mapped directly from the filter form controls
   */
  onFiltersChanged(activeFilters: any): void {
    this.loadDronesFromBackend(activeFilters);
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
}
