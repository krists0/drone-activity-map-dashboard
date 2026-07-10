
import { Component } from '@angular/core';
import { DroneMapComponent } from './features/dashboard/components/drone-map/drone-map';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [DroneMapComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {}
