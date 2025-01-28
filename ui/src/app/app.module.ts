import { AppComponent, ButtonComponent, SelectComponent, StaticTextComponent, TextComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { BrowserModule } from '@angular/platform-browser';
import { ReactiveFormsModule } from '@angular/forms';
import { HeatmapCanvasComponent } from './heatmap-with-lineouts/heatmap-canvas.component';
import { HeatmapWithLineoutsComponent } from './heatmap-with-lineouts/heatmap-with-lineouts.component';
import { HttpClientModule } from "@angular/common/http";
import { NgModule } from '@angular/core';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { ScreenComponent, LayoutComponent, ColumnsComponent, ButtonsComponent, FieldEditorComponent } from './screen/screen.component';

@NgModule({
    declarations: [
        AppComponent,
        ButtonComponent,
        ButtonsComponent,
        ColumnsComponent,
        FieldEditorComponent,
        HeatmapCanvasComponent,
        HeatmapWithLineoutsComponent,
        LayoutComponent,
        ScreenComponent,
        SelectComponent,
        StaticTextComponent,
        TextComponent,
    ],
    imports: [
        AppRoutingModule,
        BrowserModule,
        HttpClientModule,
        NgbModule,
        ReactiveFormsModule,
    ],
    providers: [],
    bootstrap: [AppComponent]
})
export class AppModule { }
