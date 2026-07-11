import { Component, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-filter-panel',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './filter-panel.html',
  styleUrls: ['./filter-panel.scss']
})
export class FilterPanelComponent {

  @Output() filtersChanged = new EventEmitter<any>();

  
  localFilters = {
    drone_type: '',
    status: '',
    operator_id: '',
    min_battery: null as number | null, 
    from: '',
    to: ''
  };

 
  applyFilters(): void {
    this.filtersChanged.emit({ ...this.localFilters });
  }

 
  resetFilters(): void {
    this.localFilters = {
      drone_type: '',
      status: '',
      operator_id: '',
      min_battery: null,
      from: '',
      to: ''
    };
   
    this.filtersChanged.emit({ ...this.localFilters });
  }
}
