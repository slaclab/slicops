import {
    AfterViewInit,
    Component,
    ElementRef,
    Input,
    OnChanges,
    ViewChild,
} from '@angular/core';
import * as d3 from 'd3';


@Component({
    selector: 'app-heatmap-canvas',
    template: `
      <canvas #canvas></canvas>
    `,
    styles: [],
})
export class HeatmapCanvasComponent implements AfterViewInit, OnChanges {
    @ViewChild('canvas') canvas!:ElementRef;
    @Input() width = 0;
    @Input() height = 0;
    @Input() intensity: number[][] = [];
    // zoomOffsets: [dx, dy, dWidth, dHeight]
    @Input() zoomOffsets: number[] = [];
    @Input() colorMap = "interpolateViridis";
    ctx: any;
    cacheCanvas: any;
    colorScale: any;

    initImage() {
        const imageData = this.ctx.getImageData(0, 0, this.cacheCanvas.width, this.cacheCanvas.height);
        const xSize = this.intensity[0].length;
        const ySize = this.intensity.length;
        for (let yi = ySize - 1, p = -1; yi >= 0; --yi) {
            for (let xi = 0; xi < xSize; ++xi) {
                const c = d3.rgb(this.colorScale(this.intensity[yi][xi]));
                imageData.data[++p] = c.r;
                imageData.data[++p] = c.g;
                imageData.data[++p] = c.b;
                imageData.data[++p] = 255;
            }
        }
        this.cacheCanvas.getContext('2d').putImageData(imageData, 0, 0);
    }

    max() : number {
        return d3.max(this.intensity, (row: number[]) => {
            return d3.max(row);
        }) as number;
    }

    min() : number {
        return d3.min(this.intensity, (row: number[]) => {
            return d3.min(row);
        }) as number;
    }

    ngAfterViewInit() {
        this.colorScale = d3.scaleSequential((d3 as any)[this.colorMap]);
        this.ctx = this.canvas.nativeElement.getContext('2d', {});
        this.cacheCanvas = document.createElement('canvas');
        this.cacheCanvas.width = this.intensity[0].length;
        this.cacheCanvas.height = this.intensity.length;
        this.colorScale.domain([this.min(), this.max()]);
        this.initImage();
    }

    ngOnChanges(changes: any) {
        if (this.cacheCanvas) {
            this.refresh();
        }
    }

    refresh() {
        this.canvas.nativeElement.width = this.width;
        this.canvas.nativeElement.height = this.height;
        this.ctx.imageSmoothingEnabled = false;
        this.ctx.drawImage(this.cacheCanvas, ...this.zoomOffsets);
    }
}
