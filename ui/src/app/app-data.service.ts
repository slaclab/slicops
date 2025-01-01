import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AppDataService {

    public xheatmapData: number[][] = [
        [0, 4, 0, 0],
        [1, 8, 10, 0],
        [0, 10, 20, 11],
        [0, 0, 12, 2],
    ];

    public heatmapData: number[][] =  Array.from({ length: 10 }, () => Array(10).fill(0.0));

    constructor() {}
}
