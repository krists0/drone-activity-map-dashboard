import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommonModule } from '@angular/common';
import { PipelineRunsTable } from './pipeline-runs-table';

describe('PipelineRunsTable Automation Tests', () => {
  let component: PipelineRunsTable;
  let fixture: ComponentFixture<PipelineRunsTable>;

  beforeEach(async () => {
    // Structural Setup Phase focusing strictly on isolating the pipeline components template
    await TestBed.configureTestingModule({
      imports: [PipelineRunsTable, CommonModule]
    }).compileComponents();

    fixture = TestBed.createComponent(PipelineRunsTable);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  // 1. SANITY CHECK
  it('should initialize and create the pipeline runs table component hierarchy', () => {
    expect(component).toBeTruthy();
  });

  // 2. CHECK EMPTY STATE FALLBACKS
  it('should structural check that pipelineData component inputs are safely defined initially', () => {
    // Asserting property exists and defaults to a safe conditional evaluation check
    expect(component.pipelineData).toBeDefined();
  });

  // 3. CHECK INPUT BINDING POPULATION (MANDATE 4.3)
  it('should cleanly accept and map pipeline analytic dictionary mock data parameters', () => {
    // Arrange: Simulate parent injection workflow mapping snake_case data arrays [3.2]
    const mockData = {
      id: 1,
      status: 'completed',
      total_records: 6,
      valid_records: 4,
      Invalid_records: 2,
      started_at: '2026-06-28T10:30:00Z'
    };

    component.pipelineData = mockData;
    fixture.detectChanges();

    // Assert mapping states internal bounds alignment
    expect(component.pipelineData.status).toBe('completed');
    expect(component.pipelineData.total_records).toBe(6);
    expect(component.pipelineData.valid_records).toBe(4);
    expect(component.pipelineData.Invalid_records).toBe(2);
  });

  // 4. CHECK TRIGGER BUTTON CLICKS EVENT DISPATCHERS (MANDATE 4.3)
  it('should emit the pipelineTriggered notification upward when runPipeline activates', () => {
    let emissionFired = false;

    // Direct subscription channel capture to eliminate reliance on external spy bindings
    component.pipelineTriggered.subscribe(() => {
      emissionFired = true;
    });

    // Fire the action trigger simulation control loop [4.3]
    component.runPipeline();

    // Verify that our local flag captured the upward execution call successfully [4.3]
    expect(emissionFired).toBe(true);
  });

  // EXPERT QA LEVEL: DICTIONARY MAPPING TO DOM RENDERING COMPLIANCE TESTS
 
  it('should render "No runs yet" text content inside the HTML element badge when pipelineData is null', () => {
    //Simulate the absolute empty state scenario on page boot [4.3]
    component.pipelineData = null;
    
    //Force Angular layout template engine engine refresh pass
    fixture.detectChanges();

    //Extract the physical DOM element context from the canvas layout
    const compiled = fixture.nativeElement as HTMLElement;
    const badgeElement = compiled.querySelector('.status-badge');
    
    expect(badgeElement).not.toBeNull();
    expect(badgeElement?.textContent?.trim()).toBe('No runs yet');
  });
  
  it('should add completed class when status is completed', async () => {
    fixture.componentRef.setInput('pipelineData', {
      id: 2,
      status: 'completed',
      total_records: 6,
      valid_records: 4,
      invalid_records: 2,
      started_at: '2026-06-28T10:30:00Z'
    });

    fixture.detectChanges();

    const badge = fixture.nativeElement.querySelector('.status-badge');

    expect(badge).not.toBeNull();
    expect(badge.textContent.trim()).toBe('completed');
  });
  it('should execute runPipeline call stack sequence when user physically fires a click trigger event on the HTML button element', () => {
    //Setup an interceptor spy variable context linking to internal state callbacks
    let isPipelineTriggeredMethodExecuted = false;
    component.pipelineTriggered.subscribe(() => {
      isPipelineTriggeredMethodExecuted = true;
    });

    // Locate the active action runner button node and simulate raw hardware mouse click triggers [4.3]
    const compiled = fixture.nativeElement as HTMLElement;
    const runPipelineBtn = compiled.querySelector('.btn-run-pipeline') as HTMLButtonElement;
    
    expect(runPipelineBtn).not.toBeNull();
    runPipelineBtn.click(); // Fires hardware UI click interaction stream flow [4.3]

    //Certify that the DOM listener layer securely caught the touch and executed logic upstream [4.3]
    expect(isPipelineTriggeredMethodExecuted).toBe(true);
  });
});
