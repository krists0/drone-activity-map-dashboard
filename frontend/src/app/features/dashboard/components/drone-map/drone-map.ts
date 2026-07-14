
import {
  AfterViewInit,
  Component,
  ElementRef,
  OnDestroy,
  PLATFORM_ID,
  ViewChild,
  inject,
  ChangeDetectorRef,
  Input,
  OnChanges,
  SimpleChanges
} from '@angular/core';

import { isPlatformBrowser } from '@angular/common';
import * as maplibregl from 'maplibre-gl';
import { DroneRecord } from '../../../../core/models/drone-record.model';

@Component({
  selector: 'app-drone-map',
  standalone: true,
  templateUrl: './drone-map.html',
  styleUrls: ['./drone-map.scss'] // 
})
export class DroneMapComponent implements AfterViewInit, OnChanges, OnDestroy {

  @ViewChild('mapContainer') mapContainer!: ElementRef<HTMLDivElement>;
  
  @Input() droneList: DroneRecord[] = []; 

  private mapReady = false;
  currentUtcTime = '';

  private map?: maplibregl.Map;
  private clockTimer?: ReturnType<typeof setInterval>;
  private markers: maplibregl.Marker[] = []; 

  private platformId = inject(PLATFORM_ID);
  private cdr = inject(ChangeDetectorRef);

  
  ngAfterViewInit(): void {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }
    
    // Start the live dashboard UTC clock tracker
    this.startClock();

    this.map = new maplibregl.Map({
      container: this.mapContainer.nativeElement,
      style: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
      center: [34.7818, 32.0853],
      zoom: 11
    });

    this.map.on('load', () => {
      this.mapReady = true;
      this.map?.resize();
      this.renderDronesIfReady();
    });

    this.map.addControl(
      new maplibregl.NavigationControl(),
      'bottom-right'
    );
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['droneList']) {
      this.renderDronesIfReady();
    }
  }
  private renderDronesIfReady(): void {
    if (!this.mapReady || !this.map) {
      return;
    }
    this.renderDrones();
  }

  private renderDrones(): void {
    if (!this.map) return;

    this.clearMarkers();

    this.droneList.forEach(drone => {
      const imgElement = document.createElement('img');
      imgElement.src = 'drone-icon-pin.png'; 
      imgElement.style.width = '32px'; 
      imgElement.style.height = '32px';
      imgElement.style.cursor = 'pointer';

      const marker = new maplibregl.Marker({
        element: imgElement,
        anchor: 'center'
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

      this.markers.push(marker);
    });
  }

  private clearMarkers(): void {
    this.markers.forEach(m => m.remove());
    this.markers = [];
  }

  private startClock(): void {
    this.clockTimer = setInterval(() => {
      const now = new Date();
      this.currentUtcTime = now.toLocaleString('en-GB', {
        timeZone: 'UTC', day: '2-digit', month: 'short', year: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
      }) + ' UTC';
      this.cdr.detectChanges();
    }, 1000);
  }

  getDronePopupHTML(drone: DroneRecord): string {
    const isLowBattery = drone.battery_percent < 20;
    const isActiveStatus = drone.status.toLowerCase() === 'active';
    const formattedTime = drone.timestamp ? new Date(drone.timestamp).toLocaleString('en-GB') : 'N/A';

    const batteryColor = isLowBattery ? '#e53e3e' : '#38a169';
    const statusColor = isActiveStatus ? '#38a169' : '#e53e3e';

    return `
      <div style="font-family: sans-serif; padding: 12px; line-height: 1.6; text-align: left; background: #ffffff;">
        <div style="border-bottom: 2px solid #eef2f5; padding-bottom: 8px; margin-bottom: 10px;">
          <strong style="font-size: 16px; color: #1a73e8; font-weight: 700;">${drone.drone_id}</strong>
        </div>
        <div style="font-size: 13px; color: #4a5568;">
          <div>Type: <b>${drone.drone_type}</b></div>
          <div>Operator: <b>${drone.operator_id}</b></div>
          <hr style="border:none; border-top:1px dashed #e2e8f0; margin:8px 0;"/>
          <div>Altitude: <b>${drone.altitude_m} m</b></div>
          <div>Speed: <b>${drone.speed_kmh} km/h</b></div>
          <hr style="border:none; border-top:1px dashed #e2e8f0; margin:8px 0;"/>
          <div style="display: flex; gap: 10px;">
            <div style="background:#f7fafc; padding:5px; border-radius:4px; flex:1; text-align:center;">
              <span style="font-size:11px;color:#718096;display:block;">Battery</span>
              <b style="color:${batteryColor}; font-size:14px;">${drone.battery_percent}%</b>
            </div>
            <div style="background:#f7fafc; padding:5px; border-radius:4px; flex:1; text-align:center;">
              <span style="font-size:11px;color:#718096;display:block;">Status</span>
              <b style="color:${statusColor}; font-size:12px; text-transform:uppercase;">${drone.status}</b>
            </div>
            
          </div>
          <div style="font-size: 11px; color: #a0aec0; margin-top: 14px; text-align: center; border-top: 1px solid #edf2f7; padding-top: 8px;">
              <strong>Last Update:</strong> ${formattedTime}
            </div>
        </div>
      </div>
    `;
  }

  ngOnDestroy(): void {
    this.clearMarkers();
    this.map?.remove();
    if (this.clockTimer) {
      clearInterval(this.clockTimer);
    }
  }
}
