import {
    AfterViewInit,
    ChangeDetectorRef,
    Component,
    ElementRef,
    HostListener,
    Input,
    OnChanges,
    OnDestroy,
    ViewChild,
} from '@angular/core';
import { Subject, debounceTime } from 'rxjs';
import * as d3 from 'd3';

class SVG {
    static clipPathId(width: number, height: number): string {
        return `sr-clippath-${width}-${height}`;
    }

    static clipPathURL(width: number, height: number): string {
        return `url(#${SVG.clipPathId(width, height)})`;
    }

    static translate(x: number, y: number): string {
        return `translate(${x}, ${y})`;
    }
}

@Component({
    selector: 'app-heatmap-with-lineouts',
    template: `
<h2 style="text-align: center">OTRS:LI21:291</h2>
<figure #figure>
  <div [ngStyle]="{
    position: 'absolute',
    'marginTop.px': margin.top,
    'marginLeft.px': margin.left,
    zIndex: -1,
  }">
    <app-heatmap-canvas
      [width]="canvasWidth"
      [height]="canvasHeight"
      [intensity]="data"
      [zoomOffsets]="zoomOffsets"
      [colorMap]="colorMap"
    ></app-heatmap-canvas>
  </div>
  <div style="position: absolute; height: 0px">
    <div [ngStyle]="{
      transform: 'rotate(270deg)',
      position: 'relative',
      'left.px': margin.left + canvasWidth + lineoutSize + margin.right - canvasHeight / 2 - 14,
      'top.px': canvasHeight / 2,
      'width.px': canvasHeight,
    }">
      <div class="sr-y-axis-label text-center">{{ yLabel }}</div>
    </div>
  </div>
  <svg
    [attr.width]="margin.left + canvasWidth + lineoutSize + margin.right"
    [attr.height]="margin.top + canvasHeight + lineoutSize + margin.bottom"
  >
    <g [attr.transform]="SVG.translate(margin.left, margin.top)">
      <g class="sr-y-overlay" [attr.transform]="SVG.translate(canvasWidth + lineoutPad, 0)">
        <defs>
          <clipPath [attr.id]="SVG.clipPathId(lineoutSize, canvasHeight)">
            <rect [attr.width]="lineoutSize" [attr.height]="canvasHeight"></rect>
          </clipPath>
        </defs>
        <g [attr.clip-path]="SVG.clipPathURL(lineoutSize, canvasHeight)">
          <path></path>
        </g>
      </g>
      <g [attr.transform]="SVG.translate(0, canvasHeight + lineoutPad)" class="sr-x-overlay">
        <defs>
          <clipPath [attr.id]="SVG.clipPathId(canvasWidth, lineoutSize)">
            <rect [attr.width]="canvasWidth" [attr.height]="lineoutSize"></rect>
          </clipPath>
        </defs>
        <g [attr.clip-path]="SVG.clipPathURL(canvasWidth, lineoutSize)">
          <path></path>
        </g>
      </g>
      <g class="sr-x-axis" [attr.transform]="SVG.translate(0, canvasHeight + lineoutSize)"></g>
      <g class="sr-x-axis-grid" [attr.transform]="SVG.translate(0, canvasHeight + lineoutSize)"></g>
      <g [attr.transform]="SVG.translate(canvasWidth + lineoutSize, 0)">
        <g class="sr-y-axis"></g>
        <g class="sr-y-axis-grid"></g>
      </g>
      <g [attr.transform]="SVG.translate(canvasWidth + lineoutPad, canvasHeight)">
        <g class="sr-yx-axis"></g>
      </g>
      <g [attr.transform]="SVG.translate(0, canvasHeight + lineoutPad)">
        <g class="sr-xy-axis"></g>
      </g>
      <rect class="sr-mouse-rect-xy sr-mouse-zoom" [attr.width]="canvasWidth"
        [attr.height]="canvasHeight"></rect>
      <rect class="sr-mouse-rect-y sr-mouse-zoom" [attr.x]="canvasWidth" [attr.width]="lineoutSize"
        [attr.height]="canvasHeight"></rect>
      <rect class="sr-mouse-rect-x sr-mouse-zoom" [attr.y]="canvasHeight"
        [attr.width]="canvasWidth" [attr.height]="lineoutSize"></rect>
    </g>
  </svg>
  <div class="sr-x-axis-label text-center" [ngStyle]="{
    'width.px': canvasWidth,
    'marginLeft.px': margin.left
  }">{{ xLabel }}</div>
</figure>
    `,
    styles: [
        `
.sr-x-overlay path, .sr-y-overlay path {
    fill: none;
    stroke: steelblue;
    stroke-width: 2;
}
        `,
    ],
})
export class HeatmapWithLineoutsComponent {
    @ViewChild('figure') el!:ElementRef;

    //TODO: input should be a structure
    //  rows
    //  xLabel
    //  yLabel
    //  xDomain
    //  yDomain
    //  colormap

    @Input() data: number[][] = [];
    SVG = SVG;

    xScale = d3.scaleLinear();
    xZoomScale = this.xScale;
    xyScale = d3.scaleLinear();
    xLabel = "x [mm]";
    xZoom: any;

    yScale = d3.scaleLinear();
    yZoomScale = this.yScale;
    yxScale = d3.scaleLinear();
    yLabel = "y [mm]";
    yZoom: any;
    zoomOffsets: number[] = [];
    colorMap = "interpolateInferno";

    xyZoom: any;
    prevXYZoom = d3.zoomIdentity;
    canvasWidth = 1;
    canvasHeight = 1;

    margin = {
        left: 65,
        right: 65,
        top: 10,
        bottom: 30,
    };
    lineoutPad = 12;
    lineoutSize = 0;

    resize = new Subject<void>;

    constructor(private cdRef: ChangeDetectorRef) {
    }

    select(selector?: string) : any {
        const s = d3.select(this.el.nativeElement);
        return selector ? s.select(selector) : s;
    }

    center(event: any, target: any) {
        if (event.sourceEvent) {
            const p = d3.pointers(event, target);
            return [d3.mean(p, d => d[0]), d3.mean(p, d => d[1])];
        }
        return [this.canvasWidth / 2, this.canvasHeight / 2];
    }

    domain(axisIndex: number) : number[] {
        //TODO(pjm): from input
        if (axisIndex === 0) {
            return [-4, 4];
        }
        return [0, 4];
    }

    handleZoom(event: any) {
        const t = event.transform;
        const k = t.k / this.prevXYZoom.k;
        if (k === 1) {
            // pan
            this.select('.sr-mouse-rect-x').call(
                this.xZoom.translateBy,
                (t.x - this.prevXYZoom.x) / d3.zoomTransform(this.select('.sr-mouse-rect-x').node()).k,
                0,
            );
            //TODO(pjm): consolidate this with above
            this.select('.sr-mouse-rect-y').call(
                this.yZoom.translateBy,
                0,
                (t.y - this.prevXYZoom.y) / d3.zoomTransform(this.select('.sr-mouse-rect-y').node()).k,
            );
        }
        else {
            // zoom
            const p = this.center(event, this.select('.sr-mouse-rect-xy').node());
            this.select('.sr-mouse-rect-x').call(this.xZoom.scaleBy, k, p);
            this.select('.sr-mouse-rect-y').call(this.yZoom.scaleBy, k, p);
        }
        this.prevXYZoom = t;
        this.refresh();
    }

    handleZoomX(t: any) {
        if (t.k < 1) {
            t.k = 1;
        }
        if (t.x > 0) {
            t.x = 0;
        }
        else if (t.x < 0) {
            const r = this.xZoomScale.range()[1];
            if (t.k * r - r + t.x < 0) {
                t.x = -(t.k * r - r);
            }
        }
        this.xZoomScale = t.rescaleX(this.xScale);
        this.refresh();
    }

    handleZoomY(t: any) {
        //TODO(pjm): consolidate with handleZoomX
        if (t.k < 1) {
            t.k = 1;
        }
        if (t.y > 0) {
            t.y = 0;
        }
        else if (t.y < 0) {
            const r = this.yZoomScale.range()[0];
            if (t.k * r - r + t.y < 0) {
                t.y = -(t.k * r - r);
            }
        }
        this.yZoomScale = t.rescaleY(this.yScale);
        this.refresh();
    }

    refresh() {
        const w = parseInt(this.select().style('width'));
        if (isNaN(w)) {
            return;
        }
        const prevSize = [this.canvasWidth, this.canvasHeight];
        this.lineoutSize = Math.floor((w - (this.margin.left + this.margin.right)) / 4);
        this.canvasWidth = w - (this.margin.left + this.lineoutSize + this.margin.right);
        this.canvasHeight = Math.floor(this.canvasWidth * (this.data.length / this.data[0].length));

        this.xScale.range([0, this.canvasWidth]);
        this.xZoomScale.range([0, this.canvasWidth]);

        if (
            (prevSize[0] && prevSize[0] != this.canvasWidth)
            || (prevSize[1] && prevSize[1] != this.canvasHeight)
        ) {
            //TODO(pjm): see if this is update-able via a call()
            let t = d3.zoomTransform(this.select('.sr-mouse-rect-x').node());
            (t.x as any) *= this.canvasWidth / prevSize[0];
            t = d3.zoomTransform(this.select('.sr-mouse-rect-y').node());
            (t.y as any) *= this.canvasHeight / prevSize[1];
        }

        //TODO(pjm): could keep axis as instance variable
        this.select('.sr-x-axis').call(d3.axisBottom(this.xZoomScale).ticks(5));
        this.select('.sr-x-axis-grid').call(d3.axisBottom(this.xZoomScale).ticks(5).tickSize(-(this.canvasHeight + this.lineoutSize)));
        this.yScale.range([this.canvasHeight, 0]);
        this.yZoomScale.range([this.canvasHeight, 0]);
        this.select('.sr-y-axis').call(d3.axisRight(this.yZoomScale).ticks(5));
        this.select('.sr-y-axis-grid').call(d3.axisRight(this.yZoomScale).ticks(5).tickSize(-(this.canvasWidth + this.lineoutSize)));

        //TODO(pjm): this will move to the server
        const xLineout = [...this.data[0]];
        for (let i = 1; i < this.data.length; i++) {
            for (let j = 0; j < this.data[0].length; j++) {
                xLineout[j] += this.data[i][j];
            }
        }
        const yLineout = this.data.map((r) => r[0]);
        for (let i = 0; i < this.data.length; i++) {
            for (let j = 1; j < this.data[0].length; j++) {
                yLineout[i] += this.data[i][j];
            }
        }

        this.yxScale
        //TODO(pjm): data min/max
            .domain([0, d3.max(yLineout) as number])
            .range([this.lineoutSize - this.lineoutPad, 0]);
        this.select('.sr-yx-axis').call(d3.axisBottom(this.yxScale).ticks(3).tickFormat(d3.format('.1e')));

        this.xyScale
            .domain([0, d3.max(xLineout) as number])
            .range([this.lineoutSize - this.lineoutPad, 0]);
        this.select('.sr-xy-axis').call(d3.axisLeft(this.xyScale).ticks(5).tickFormat(d3.format('.1e')));


        const xd = this.domain(0);
        // offset by half pixel width
        const xoff = (xd[1] - xd[0]) / this.data[0].length / 2;
        const xline = d3.line()
              .x((d) => this.xZoomScale(d[0] + xoff))
              .y((d) => this.xyScale(d[1]));
        //const xdata = this.data[Math.round(this.data.length / 2)].map((v, idx) => {
        const xdata = xLineout.map((v, idx) => {
            return [
                this.domain(0)[0] + (idx / this.data[0].length) * (this.domain(0)[1] - this.domain(0)[0]),
                v,
            ];
        });

        this.select('.sr-x-overlay path').datum(xdata).attr('d', xline);

        //TODO(pjm): consolidate with x above
        const yd = this.domain(1);
        const yoff = (yd[1] - yd[0]) / this.data.length / 2;
        const yline = d3.line()
              .x((d) => this.yxScale(d[1]))
              .y((d) => this.yZoomScale(d[0] + yoff));
        //const ydata = this.data.map((v, idx) => {
        const ydata = yLineout.map((v, idx) => {
            return [
                this.domain(1)[0] + (idx / this.data.length) * (this.domain(1)[1] - this.domain(1)[0]),
                //v[Math.round(v.length / 2)],
                v,
            ];
        });
        this.select('.sr-y-overlay path').datum(ydata).attr('d', yline);

        const xZoomDomain = this.xZoomScale.domain();
        const xDomain = this.xScale.domain();
        const yZoomDomain = this.yZoomScale.domain();
        const yDomain = this.yScale.domain();
        const zoomWidth = xZoomDomain[1] - xZoomDomain[0];
        const zoomHeight = yZoomDomain[1] - yZoomDomain[0];
        this.zoomOffsets = [
            -(xZoomDomain[0] - xDomain[0]) / zoomWidth * this.canvasWidth,
            -(yDomain[1] - yZoomDomain[1]) / zoomHeight * this.canvasHeight,
            (xDomain[1] - xDomain[0]) / zoomWidth * this.canvasWidth,
            (yDomain[1] - yDomain[0]) / zoomHeight * this.canvasHeight,
        ];
    }

    ngOnDestroy() {
        //TODO(pjm): not sure this is required, check for memory leaks
        //this.xZoom.on('zoom', null);
        //this.resize.next();
        //this.resize.complete();
    }

    ngAfterViewInit() {
        this.resize.asObservable().pipe(debounceTime(350)).subscribe(() => {
            this.refresh();
        });

        this.xZoom = d3.zoom().on('zoom', (event) => { this.handleZoomX(event.transform) });
        this.select('.sr-mouse-rect-x').call(this.xZoom);
        this.yZoom = d3.zoom().on('zoom', (event) => { this.handleZoomY(event.transform) });
        this.select('.sr-mouse-rect-y').call(this.yZoom);
        this.xyZoom = d3.zoom().on('zoom', (event) => { this.handleZoom(event) });
        this.select('.sr-mouse-rect-xy').call(this.xyZoom);

        this.xScale.domain(this.domain(0));
        this.yScale.domain(this.domain(1));

        this.refresh();
        // required because refresh() changes view values (element sizes)
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
