
import { Component } from '@angular/core';
import { DashboardPageComponent } from './features/dashboard/pages/dashboard-page/dashboard-page';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [DashboardPageComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss',
  
})
export class App {}
