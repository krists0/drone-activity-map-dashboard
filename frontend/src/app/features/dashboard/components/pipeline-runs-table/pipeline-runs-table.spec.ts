import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PipelineRunsTable } from './pipeline-runs-table';

describe('PipelineRunsTable', () => {
  let component: PipelineRunsTable;
  let fixture: ComponentFixture<PipelineRunsTable>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PipelineRunsTable],
    }).compileComponents();

    fixture = TestBed.createComponent(PipelineRunsTable);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
