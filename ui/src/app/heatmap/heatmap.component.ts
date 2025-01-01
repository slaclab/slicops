import {
    AfterViewInit,
    ChangeDetectorRef,
    Component,
    ElementRef,
    HostListener,
    Input,
    OnChanges,
    ViewChild,
} from '@angular/core';
import { Subject, debounceTime } from 'rxjs';
import * as d3 from 'd3';

@Component({
    selector: 'app-heatmap',
    template: `
<h2 style="text-align: center">OTRS:LI21:291</h2>
<figure #figure>
  <div style="position: relative">
    <canvas [ngStyle]="{'position': 'absolute', 'left': margin.left + 'px', 'top': margin.top + 'px'}"></canvas>
  </div>
  <div style="position: absolute; height: 0">
    <div [ngStyle]="{'transform': 'rotate(-90deg)', 'position': 'relative', 'left': -(width / aspectRatio / 2) + 'px', 'top': width / aspectRatio / 2 + margin.top - 10 + 'px', 'width': width / aspectRatio + 'px'}">
      <div class="sr-y-axis-label text-center">{{ yLabel }}</div>
    </div>
  </div>
  <svg [attr.width]="width + margin.left + margin.right" [attr.height]="width / aspectRatio + margin.top + margin.bottom">
    <g [attr.transform]="'translate(' + margin.left + ',' + margin.top + ')'">
      <g class="sr-overlay">
      </g>
      <g class="sr-x-axis" [attr.transform]="'translate(0,' + (width / aspectRatio) + ')'"></g>
      <g class="sr-y-axis"></g>
    </g>
  </svg>
  <div style="position: absolute">
    <div [ngStyle]="{'position': 'relative', 'left': margin.left + 'px', 'width': width + 'px'}">
      <div class="sr-x-axis-label text-center">{{ xLabel }}</div>
    </div>
  </div>
</figure>
    `,
    styles: [],
})
export class HeatmapComponent {
    @ViewChild('figure') el!:ElementRef;

    //TODO: input should be a structure
    //  rows
    //  xLabel
    //  yLabel
    //  xDomain
    //  yDomain
    //  colormap

    @Input() data: number[][] = [];
    resize = new Subject<void>;
    margin = {
        left: 65,
        right: 40,
        top: 0,
        bottom: 30,
    };
    width = 0;
    aspectRatio = 1;
    xScale = d3.scaleLinear();
    yScale = d3.scaleLinear();
    //colorScale = d3.scaleSequential(d3.interpolateViridis);
    colorScale = d3.scaleSequential(d3.interpolateInferno);
    xLabel = "x [mm]";
    yLabel = "y [mm]";
    canvas: any;
    ctx: any;
    cacheCanvas: any;
    imageData: any;

    constructor(private cdRef: ChangeDetectorRef) {}

    select(selector?: string) : any {
        const s = d3.select(this.el.nativeElement);
        return selector ? s.select(selector) : s;
    }

    domain(axisIndex: number) : number[] {
        //TODO(pjm): from input
        if (axisIndex === 0) {
            return [(-320 * 5 - 1000) * 1e-3, (320 * 5 - 1000) * 1e-3];
        }
        return [(-240 * 5 - 500) * 1e-3, (240 * 5 - 500) * 1e-3];
    }

    refresh() {
        const w = parseInt(this.select().style('width'));
        if (isNaN(w)) {
            return;
        }
        this.width = w - this.margin.left - this.margin.right;
        this.aspectRatio = this.data[0].length / this.data.length;
        this.xScale
            .range([0, this.width])
            .domain(this.domain(0));
        this.select('.sr-x-axis').call(d3.axisBottom(this.xScale).ticks(5));
        this.yScale
            .domain(this.domain(1))
            .range([Math.round(this.width / this.aspectRatio), 0])
            .nice();
        this.select('.sr-y-axis').call(d3.axisLeft(this.yScale).ticks(5));

        this.canvas.width = this.width;
        this.canvas.height = Math.round(this.width / this.aspectRatio);
        const ctx = this.canvas.getContext('2d');
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(
            this.cacheCanvas,
            0,
            0,
            this.width,
            Math.round(this.width / this.aspectRatio),
        );
    }

    initImage() {
        const xSize = this.data[0].length;
        const ySize = this.data.length;
        for (let yi = ySize - 1, p = -1; yi >= 0; --yi) {
            for (let xi = 0; xi < xSize; ++xi) {
                const c = d3.rgb(this.colorScale(this.data[yi][xi]) as any);
                this.imageData.data[++p] = c.r;
                this.imageData.data[++p] = c.g;
                this.imageData.data[++p] = c.b;
                this.imageData.data[++p] = 255;
            }
        }
        this.cacheCanvas.getContext('2d').putImageData(this.imageData, 0, 0);
    }

    max() : number {
        return d3.max(this.data, (row: number[]) => {
            return d3.max(row);
        }) as number;
    }

    min() : number {
        return d3.min(this.data, (row: number[]) => {
            return d3.min(row);
        }) as number;
    }

    ngAfterViewInit() {
        this.resize.asObservable().pipe(debounceTime(350)).subscribe(() => this.refresh());
        this.canvas = this.select('canvas').node();
        this.ctx = this.canvas.getContext('2d', { willReadFrequently: true });
        this.cacheCanvas = document.createElement('canvas');

        //TODO(pjm): watch input, load data
        this.cacheCanvas.width = this.data[0].length;
        this.cacheCanvas.height = this.data.length;
        this.imageData = this.ctx.getImageData(0, 0, this.cacheCanvas.width, this.cacheCanvas.height);
        this.colorScale.domain([this.min(), this.max()]);
        this.initImage();

        this.refresh();
        // required because refresh changes view values
        this.cdRef.detectChanges();
    }

    ngOnChanges(changes: any) {
        if (this.el) {
            this.refresh();
        }
    }

    @HostListener('window:resize')
    onResize() {
        this.resize.next();
    }
}
