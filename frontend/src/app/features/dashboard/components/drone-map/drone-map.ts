import {
  AfterViewInit,
  Component,
  ElementRef,
  OnDestroy,
  PLATFORM_ID,
  ViewChild,
  inject,
  ChangeDetectorRef
} from '@angular/core';

import { isPlatformBrowser } from '@angular/common';
import * as maplibregl from 'maplibre-gl';
import { HttpErrorResponse } from '@angular/common/http';
import { DroneRecord } from '../../../../core/models/drone-record.model';
import { DroneApiService } from '../../../../core/services/drone-api.service';
@Component({
  selector: 'app-drone-map',
  standalone: true,
  templateUrl: './drone-map.html',
  styleUrls: ['./drone-map.scss']
})
export class DroneMapComponent implements AfterViewInit, OnDestroy {

  @ViewChild('mapContainer')
  mapContainer!: ElementRef<HTMLDivElement>;

  currentUtcTime = '';

  private map?: maplibregl.Map;
  private timer?: ReturnType<typeof setInterval>;

  private platformId = inject(PLATFORM_ID);
  private cdr = inject(ChangeDetectorRef);


  private readonly droneApiService: DroneApiService = inject(DroneApiService);

  droneList: DroneRecord[] = [];
 
  ngAfterViewInit(): void {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }
    this.updateUtcTime();
    this.timer = setInterval(() => {
      this.updateUtcTime();
    }, 1000);

    //map dashboard
    this.map = new maplibregl.Map({
      container: this.mapContainer.nativeElement,
      style: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
      center: [34.7818, 32.0853],
      zoom: 11
    });

    this.map.on('load', () => {
      this.map?.resize();
      this.loadDronesFromBackend();
    });

    this.map.addControl(
      new maplibregl.NavigationControl(),
      'bottom-right'
    );
  }

  

  private loadDronesFromBackend(): void {
  this.droneApiService.getDrones().subscribe({
    next: (drones: DroneRecord[]) => {
      this.droneList = drones;
      this.renderDrones();
    },
    error: (err: HttpErrorResponse) => {
      console.error('Failed to load drones from backend', err.message);
    }
  });
  }

  //[4]displays drone records on a map. Clicking a marker should open a popup 

  private renderDrones(): void {
    if (!this.map) return;

    this.droneList.forEach(drone => {
      const imgElement = document.createElement('img');
      imgElement.src = 'drone-icon-pin.png';
      imgElement.style.width = '32px'; 
      imgElement.style.height = '32px';
      imgElement.style.cursor = 'pointer';
    

      new maplibregl.Marker({
        element: imgElement,
        anchor: 'center', 
        offset: [0, 0]
      })
      .setLngLat([drone.longitude, drone.latitude])
      .setPopup(
        new maplibregl.Popup({ 
          offset: 25,
          closeButton: true,
          maxWidth: '260px' 
        }).setHTML(this.getDronePopupHTML(drone))
      )
      .addTo(this.map!);
    });

   
  }

  getDronePopupHTML(drone: DroneRecord) {
    // Check for critical battery or active status to apply adaptive colors
    const isLowBattery = drone.battery_percent < 20;
    const isActiveStatus = drone.status.toLowerCase() === 'active';
    
    const batteryColor = isLowBattery ? '#e53e3e' : '#38a169';
    const statusColor = isActiveStatus ? '#38a169' : '#e53e3e';

    return `
      <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 12px; line-height: 1.6; text-align: left; direction: ltr; background: #ffffff;">
        
        <!-- Header Section: Drone ID -->
        <div style="border-bottom: 2px solid #eef2f5; padding-bottom: 8px; margin-bottom: 10px;">
          <span style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: #8898aa; font-weight: bold; display: block; margin-bottom: 2px;">
            Drone Identifier
          </span>
          <strong style="font-size: 16px; color: #1a73e8; font-weight: 700; letter-spacing: -0.3px;">
            ${drone.drone_id}
          </strong>
        </div>
        
        <!-- Content Section -->
        <div style="font-size: 13px; color: #4a5568;">
          
          <!-- Drone Specifications -->
          <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
            <span style="color: #718096;">Type:</span>
            <span style="font-weight: 600; color: #2d3748;">${drone.drone_type}</span>
          </div>
          
          <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
            <span style="color: #718096;">Operator:</span>
            <span style="font-weight: 600; color: #2d3748; font-family: monospace;">${drone.operator_id}</span>
          </div>
          
          <div style="border-top: 1px dashed #e2e8f0; margin: 8px 0;"></div>
          
          <!-- Telemetry Data -->
          <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
            <div><span style="color: #718096;">Altitude:</span> <strong style="color: #2d3748;">${drone.altitude_m} m</strong></div>
            <div><span style="color: #718096;">Speed:</span> <strong style="color: #2d3748;">${drone.speed_kmh} km/h</strong></div>
          </div>
          
          <div style="border-top: 1px dashed #e2e8f0; margin: 8px 0;"></div>
          
          <!-- Key Metrics Cards -->
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px;">
            
            <!-- Battery Widget -->
            <div style="background: #f7fafc; padding: 6px 8px; border-radius: 6px; border: 1px solid #edf2f7; text-align: center;">
              <span style="font-size: 11px; color: #718096; display: block; margin-bottom: 2px;">Battery</span>
              <span style="color: ${batteryColor}; font-weight: 700; font-size: 14px;">
                ${drone.battery_percent}%
              </span>
            </div>
            
            <!-- Status Widget -->
            <div style="background: #f7fafc; padding: 6px 8px; border-radius: 6px; border: 1px solid #edf2f7; text-align: center;">
              <span style="font-size: 11px; color: #718096; display: block; margin-bottom: 2px;">Status</span>
              <span style="color: ${statusColor}; font-weight: 700; font-size: 12px; text-transform: uppercase;">
                ${drone.status}
              </span>
            </div>
            
          </div>

          <!-- Footer: Timestamp -->
          <div style="font-size: 10px; color: #a0aec0; margin-top: 12px; text-align: center; border-top: 1px solid #edf2f7; padding-top: 6px;">
            Last Update: ${drone.timestamp}
          </div>
          
        </div>
      </div>
    `;
  }


  private updateUtcTime(): void {
    const now = new Date();
    this.currentUtcTime = now.toLocaleString('en-GB', {
      timeZone: 'UTC',
      day: '2-digit',
      month: 'short',
      year: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit', 
      hour12: false
    }) + ' UTC';

  
    this.cdr.detectChanges(); 
  }

  ngOnDestroy(): void {
    this.map?.remove();
    if (this.timer) {
      clearInterval(this.timer);
    }
  }
}
