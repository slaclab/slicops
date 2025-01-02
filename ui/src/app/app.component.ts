import { Component } from '@angular/core';
import { AppDataService } from './app-data.service';

@Component({
    selector: 'app-root',
    template: `
<app-profile-monitor></app-profile-monitor>
    `,
    styles: [],
})
export class AppComponent {
    title = 'screen';

    oldHeatmapData: number[][] = [
        [0, 4, 0, 0],
        [1, 8, 10, 0],
        [0, 10, 20, 11],
        [0, 0, 12, 2],
    ];

    lineData: number[][] = [
        [0, 5.3443e-3],
        [1.0, 6.055e-3],
        [1.1, 5.964e-3],
        [2.1, 3.554e-3],
        [2.2, 3.401e-3],
        [3.2, 2.746e-3],
    ];

    heatmapData: number[][];

    constructor(dataService: AppDataService) {
        this.heatmapData = dataService.heatmapData;
    }
}
