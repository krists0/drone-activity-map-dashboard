import { Component, Output, EventEmitter, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-pipeline-runs-table',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './pipeline-runs-table.html',
  styleUrl: './pipeline-runs-table.scss',
})
export class PipelineRunsTable {

  @Input() pipelineRuns: any[] = [];

  @Output() pipelineTriggered = new EventEmitter<void>();

  @Input() currentPage: number =1;
  @Input() hasNextPage: boolean= true;
  @Output() pageChanged = new EventEmitter<number>();

  runPipeline(): void {
    this.pipelineTriggered.emit();
  }
  previousPage(): void {
    if (this.currentPage > 1) {
      this.pageChanged.emit(this.currentPage - 1);
    }
  }

  nextPage(): void {
    if (this.hasNextPage) {
      this.pageChanged.emit(this.currentPage + 1);
    }
  }
}