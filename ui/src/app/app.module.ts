import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { LineChartComponent } from './line-chart/line-chart.component';
import { HeatmapComponent } from './heatmap/heatmap.component';
import { HeatmapWithLineoutsComponent } from './heatmap-with-lineouts/heatmap-with-lineouts.component';
import { HeatmapCanvasComponent } from './heatmap-with-lineouts/heatmap-canvas.component';
import { ProfileMonitorComponent } from './profile-monitor/profile-monitor.component';

@NgModule({
    declarations: [
        AppComponent,
        LineChartComponent,
        HeatmapComponent,
        HeatmapWithLineoutsComponent,
        HeatmapCanvasComponent,
        ProfileMonitorComponent
    ],
    imports: [
        BrowserModule,
        AppRoutingModule,
        NgbModule
    ],
    providers: [],
    bootstrap: [AppComponent]
})
export class AppModule { }
