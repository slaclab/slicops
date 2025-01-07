import { Component } from '@angular/core';
import { AppDataService } from './app-data.service';

@Component({
    selector: 'app-root',
    template: `
      <div class="container-fluid">
        <router-outlet></router-outlet>
      </div>
    `,
    styles: [],
})
export class AppComponent {
    title = 'slicops';

    heatmapData: number[][];

    constructor(dataService: AppDataService) {
        this.heatmapData = dataService.heatmapData;
    }
}
