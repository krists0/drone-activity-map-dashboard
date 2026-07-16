import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommonModule } from '@angular/common';
import { PipelineRunsTable } from './pipeline-runs-table';

describe('PipelineRunsTable', () => {
  let component: PipelineRunsTable;
  let fixture: ComponentFixture<PipelineRunsTable>;

  function getMockRuns() {
    return [
      {
        id: 2,
        status: 'completed',
        total_records: 6,
        valid_records: 4,
        invalid_records: 2,
        started_at: '2026-06-28T10:30:00Z'
      },
      {
        id: 1,
        status: 'failed',
        total_records: 3,
        valid_records: 0,
        invalid_records: 3,
        started_at: '2026-06-27T09:00:00Z'
      }
    ];
  }

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PipelineRunsTable, CommonModule]
    }).compileComponents();

    fixture = TestBed.createComponent(PipelineRunsTable);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create the component', () => {
    expect(component).toBeTruthy();
  });

  it('should default pipelineRuns to an empty array', () => {
    expect(component.pipelineRuns).toEqual([]);
  });

  it('should show the empty state message when there are no runs', () => {
    fixture.componentRef.setInput('pipelineRuns', []);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const emptyState = compiled.querySelector('.empty-state');

    expect(emptyState).not.toBeNull();
    expect(emptyState?.textContent?.trim()).toBe('No runs yet.');
    expect(compiled.querySelector('.runs-table')).toBeNull();
  });

  it('should render one table row per pipeline run', () => {
    fixture.componentRef.setInput('pipelineRuns', getMockRuns());
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const rows = compiled.querySelectorAll('.runs-table tbody tr');

    expect(rows.length).toBe(2);
  });

  it('should display valid and invalid counts per run', () => {
    fixture.componentRef.setInput('pipelineRuns', getMockRuns());
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const firstRow = compiled.querySelector('.runs-table tbody tr') as HTMLElement | null;

  
    if (!firstRow) {
      console.log('DEBUG - actual DOM:', compiled.innerHTML);
    }

    expect(firstRow).not.toBeNull();
    expect(firstRow?.querySelector('.success-txt')?.textContent?.trim()).toBe('4');
    expect(firstRow?.querySelector('.fail-txt')?.textContent?.trim()).toBe('2');
  });

  it('should apply the correct status class to the badge', () => {
    fixture.componentRef.setInput('pipelineRuns', getMockRuns());
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const badge = compiled.querySelector('.status-badge') as HTMLElement | null;

    if (!badge) {
      console.log('DEBUG - actual DOM:', compiled.innerHTML);
    }

    expect(badge).not.toBeNull();
    expect(badge?.classList).toContain('completed');
    expect(badge?.textContent?.trim()).toBe('completed');
  });

  it('should emit pipelineTriggered when the run button is clicked', () => {
    let emitted = false;
    component.pipelineTriggered.subscribe(() => (emitted = true));

    const compiled = fixture.nativeElement as HTMLElement;
    const runButton = compiled.querySelector('.btn-run-pipeline') as HTMLButtonElement;

    expect(runButton).not.toBeNull();
    runButton.click();

    expect(emitted).toBe(true);
  });
  it('should apply the failed class to the second run badge', () => {
    fixture.componentRef.setInput('pipelineRuns', getMockRuns());
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const badges = compiled.querySelectorAll('.status-badge');

    expect(badges[1].classList).toContain('failed');
    expect(badges[1].textContent?.trim()).toBe('failed');
  });

  it('should not show the empty state message when there are runs', () => {
    fixture.componentRef.setInput('pipelineRuns', getMockRuns());
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.empty-state')).toBeNull();
  });

  it('should render a non-empty formatted date for each run', () => {
    fixture.componentRef.setInput('pipelineRuns', getMockRuns());
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const firstDateCell = compiled.querySelector('.runs-table tbody tr td') as HTMLElement;

    expect(firstDateCell.textContent?.trim().length).toBeGreaterThan(0);
  });
});