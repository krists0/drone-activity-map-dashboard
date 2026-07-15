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

  runPipeline(): void {
    this.pipelineTriggered.emit();
  }
}