
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommonModule } from '@angular/common';
import { DroneMapComponent } from './drone-map';
import { DroneRecord } from '../../../../core/models/drone-record.model';

describe('DroneMapComponent Automation Tests', () => {

  let component: DroneMapComponent;
  let fixture: ComponentFixture<DroneMapComponent>;

  const mockDrone: DroneRecord = {
    id: 1,
    drone_id: 'DRONE-001',
    drone_type: 'VTOL',
    operator_id: 'OP-001',
    latitude: 32.0853,
    longitude: 34.7818,
    altitude_m: 150,
    speed_kmh: 65,
    battery_percent: 80,
    timestamp: '2026-06-28T10:30:00Z',
    status: 'active' 
  };


  beforeEach(async () => {

    // Disable MapLibre initialization during unit tests
    DroneMapComponent.prototype.ngAfterViewInit = function () {};

    await TestBed.configureTestingModule({
      imports: [
        DroneMapComponent,
        CommonModule
      ]
    }).compileComponents();


    fixture = TestBed.createComponent(DroneMapComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });


  //SANITY CHECK
  it('should create drone map component successfully', () => {
    expect(component).toBeTruthy();
  });


  // DEFAULT INPUT STATE
  it('should initialize droneList with an empty collection', () => {
    expect(component.droneList).toEqual([]);
  });


  // INPUT BINDING
  it('should accept drone list input correctly', async () => {

    fixture.componentRef.setInput(
      'droneList',
      [mockDrone]
    );

    expect(component.droneList.length)
      .toBe(1);

    expect(component.droneList[0].drone_id)
      .toBe('DRONE-001');
  });


  // POPUP HTML CONTENT
  it('should generate popup HTML containing all telemetry fields', () => {

    const html =
      component.getDronePopupHTML(mockDrone);


    expect(html).toContain('DRONE-001');
    expect(html).toContain('VTOL');
    expect(html).toContain('OP-001');
    expect(html).toContain('150 m');
    expect(html).toContain('65 km/h');
    expect(html).toContain('80%');
    expect(html).toContain('Last Update');
  });


  // LOW BATTERY LOGIC
  it('should mark battery as critical when battery level is below 20 percent', () => {

    const lowBatteryDrone: DroneRecord = {
      ...mockDrone,
      battery_percent: 10
    };


    const html =
      component.getDronePopupHTML(lowBatteryDrone);


    expect(html).toContain('10%');
    expect(html).toContain('#e53e3e');
  });


  // NORMAL BATTERY LOGIC
  it('should mark battery as healthy when battery level is above 20 percent', () => {

    const html =
      component.getDronePopupHTML(mockDrone);


    expect(html).toContain('80%');
    expect(html).toContain('#38a169');
  });


  // ACTIVE STATUS LOGIC
  it('should render active drone status correctly', () => {

    const html =component.getDronePopupHTML(mockDrone);

    expect(html).toContain('active');
    expect(html).toContain('#38a169');
    });

  


  // EMPTY TIMESTAMP HANDLING
  it('should display N/A when timestamp is missing', () => {

    const droneWithoutTimestamp: DroneRecord = {
      ...mockDrone,
      timestamp: ''
    };


    const html =
      component.getDronePopupHTML(droneWithoutTimestamp);

    expect(html).toContain('Last Update');
    expect(html).toContain('N/A');
  });



});