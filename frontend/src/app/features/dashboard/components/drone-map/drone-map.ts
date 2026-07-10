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

  ngAfterViewInit(): void {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

  
    this.updateUtcTime();

    this.timer = setInterval(() => {
      this.updateUtcTime();
    }, 1000);

    
    this.map = new maplibregl.Map({
      container: this.mapContainer.nativeElement,
      style: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
      center: [34.7818, 32.0853],
      zoom: 11
    });

    this.map.on('load', () => {
      this.map?.resize();
    });

    this.map.addControl(
      new maplibregl.NavigationControl(),
      'top-right'
    );
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
