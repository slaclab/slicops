import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HttpClientModule } from "@angular/common/http";
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { HeatmapWithLineoutsComponent } from './heatmap-with-lineouts/heatmap-with-lineouts.component';
import { HeatmapCanvasComponent } from './heatmap-with-lineouts/heatmap-canvas.component';
import { ScreenComponent } from './screen/screen.component';

@NgModule({
    declarations: [
        AppComponent,
        HeatmapWithLineoutsComponent,
        HeatmapCanvasComponent,
        ScreenComponent
    ],
    imports: [
        BrowserModule,
        AppRoutingModule,
        HttpClientModule,
        NgbModule
    ],
    providers: [],
    bootstrap: [AppComponent]
})
export class AppModule { }
