import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PipelineControl } from './pipeline-control';

describe('PipelineControl', () => {
  let component: PipelineControl;
  let fixture: ComponentFixture<PipelineControl>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PipelineControl],
    }).compileComponents();

    fixture = TestBed.createComponent(PipelineControl);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
