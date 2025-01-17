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
        return `slicops-clippath-${width}-${height}`;
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
      [intensity]="data.raw_pixels"
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
      <div class="slicops-y-axis-label text-center">{{ yLabel }}</div>
    </div>
  </div>
  <svg
    [attr.width]="margin.left + canvasWidth + lineoutSize + margin.right"
    [attr.height]="margin.top + canvasHeight + lineoutSize + margin.bottom"
  >
    <g [attr.transform]="SVG.translate(margin.left, margin.top)">
      <g class="slicops-y-overlay" [attr.transform]="SVG.translate(canvasWidth + lineoutPad, 0)">
        <defs>
          <clipPath [attr.id]="SVG.clipPathId(lineoutSize, canvasHeight)">
            <rect [attr.width]="lineoutSize" [attr.height]="canvasHeight"></rect>
          </clipPath>
        </defs>
        <g [attr.clip-path]="SVG.clipPathURL(lineoutSize, canvasHeight)">
          <path class="slicops-y-path"></path>
          <path class="slicops-y-fit-path"></path>
        </g>
      </g>
      <g [attr.transform]="SVG.translate(0, canvasHeight + lineoutPad)" class="slicops-x-overlay">
        <defs>
          <clipPath [attr.id]="SVG.clipPathId(canvasWidth, lineoutSize)">
            <rect [attr.width]="canvasWidth" [attr.height]="lineoutSize"></rect>
          </clipPath>
        </defs>
        <g [attr.clip-path]="SVG.clipPathURL(canvasWidth, lineoutSize)">
          <path class="slicops-x-path"></path>
          <path class="slicops-x-fit-path"></path>
        </g>
      </g>
      <g class="slicops-x-axis" [attr.transform]="SVG.translate(0, canvasHeight + lineoutSize)"></g>
      <g class="slicops-x-axis-grid" [attr.transform]="SVG.translate(0, canvasHeight + lineoutSize)"></g>
      <g [attr.transform]="SVG.translate(canvasWidth + lineoutSize, 0)">
        <g class="slicops-y-axis"></g>
        <g class="slicops-y-axis-grid"></g>
      </g>
      <g [attr.transform]="SVG.translate(canvasWidth + lineoutPad, canvasHeight)">
        <g class="slicops-yx-axis"></g>
      </g>
      <g [attr.transform]="SVG.translate(0, canvasHeight + lineoutPad)">
        <g class="slicops-xy-axis"></g>
      </g>
      <rect class="slicops-mouse-rect-xy slicops-mouse-zoom" [attr.width]="canvasWidth"
        [attr.height]="canvasHeight"></rect>
      <rect class="slicops-mouse-rect-y slicops-mouse-zoom" [attr.x]="canvasWidth" [attr.width]="lineoutSize"
        [attr.height]="canvasHeight"></rect>
      <rect class="slicops-mouse-rect-x slicops-mouse-zoom" [attr.y]="canvasHeight"
        [attr.width]="canvasWidth" [attr.height]="lineoutSize"></rect>
    </g>
  </svg>
  <div class="slicops-x-axis-label text-center" [ngStyle]="{
    'width.px': canvasWidth,
    'marginLeft.px': margin.left
  }">{{ xLabel }}</div>
</figure>
    `,
    styles: [
        `
.slicops-x-path, .slicops-y-path {
    fill: none;
    stroke: #1f77b4;
    stroke-width: 2;
}
.slicops-x-fit-path, .slicops-y-fit-path {
    fill: none;
    stroke-dasharray: 5 3;
    stroke: #ff7f0e;
    stroke-width: 3;
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

    @Input() data: any = null;
    @Input() colorMap: any = null;
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

    axisDomain(axis: string) : number[] {
        //TODO(pjm): from input
        if (axis === 'x') {
            return [-4, 4];
        }
        return [0, 4];
    }

    center(event: any, target: any) {
        if (event.sourceEvent) {
            const p = d3.pointers(event, target);
            return [d3.mean(p, d => d[0]), d3.mean(p, d => d[1])];
        }
        return [this.canvasWidth / 2, this.canvasHeight / 2];
    }

    handleZoom(event: any) {
        const t = event.transform;
        const k = t.k / this.prevXYZoom.k;
        if (k === 1) {
            // pan
            this.select('.slicops-mouse-rect-x').call(
                this.xZoom.translateBy,
                (t.x - this.prevXYZoom.x) / d3.zoomTransform(this.select('.slicops-mouse-rect-x').node()).k,
                0,
            );
            //TODO(pjm): consolidate this with above
            this.select('.slicops-mouse-rect-y').call(
                this.yZoom.translateBy,
                0,
                (t.y - this.prevXYZoom.y) / d3.zoomTransform(this.select('.slicops-mouse-rect-y').node()).k,
            );
        }
        else {
            // zoom
            const p = this.center(event, this.select('.slicops-mouse-rect-xy').node());
            this.select('.slicops-mouse-rect-x').call(this.xZoom.scaleBy, k, p);
            this.select('.slicops-mouse-rect-y').call(this.yZoom.scaleBy, k, p);
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
        this.select('.slicops-mouse-rect-x').call(this.xZoom);
        this.yZoom = d3.zoom().on('zoom', (event) => { this.handleZoomY(event.transform) });
        this.select('.slicops-mouse-rect-y').call(this.yZoom);
        this.xyZoom = d3.zoom().on('zoom', (event) => { this.handleZoom(event) });
        this.select('.slicops-mouse-rect-xy').call(this.xyZoom);

        this.xScale.domain(this.axisDomain('x'));
        this.yScale.domain(this.axisDomain('y'));

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

    refresh() {
        const w = parseInt(this.select().style('width'));
        if (isNaN(w)) {
            return;
        }
        const prevSize = [this.canvasWidth, this.canvasHeight];
        this.lineoutSize = Math.floor((w - (this.margin.left + this.margin.right)) / 4);
        this.canvasWidth = w - (this.margin.left + this.lineoutSize + this.margin.right);
        this.canvasHeight = Math.floor(this.canvasWidth * (this.data.raw_pixels.length / this.data.raw_pixels[0].length));

        this.xScale.range([0, this.canvasWidth]);
        this.xZoomScale.range([0, this.canvasWidth]);

        if (
            (prevSize[0] && prevSize[0] != this.canvasWidth)
            || (prevSize[1] && prevSize[1] != this.canvasHeight)
        ) {
            //TODO(pjm): see if this is update-able via a call()
            let t = d3.zoomTransform(this.select('.slicops-mouse-rect-x').node());
            (t.x as any) *= this.canvasWidth / prevSize[0];
            t = d3.zoomTransform(this.select('.slicops-mouse-rect-y').node());
            (t.y as any) *= this.canvasHeight / prevSize[1];
        }

        //TODO(pjm): could keep axis as instance variable
        this.select('.slicops-x-axis').call(d3.axisBottom(this.xZoomScale).ticks(5));
        this.select('.slicops-x-axis-grid').call(d3.axisBottom(this.xZoomScale).ticks(5).tickSize(-(this.canvasHeight + this.lineoutSize)));
        this.yScale.range([this.canvasHeight, 0]);
        this.yZoomScale.range([this.canvasHeight, 0]);
        this.select('.slicops-y-axis').call(d3.axisRight(this.yZoomScale).ticks(5));
        this.select('.slicops-y-axis-grid').call(d3.axisRight(this.yZoomScale).ticks(5).tickSize(-(this.canvasWidth + this.lineoutSize)));

        const xLineout = this.data.x.lineout as number[];
        const yLineout = this.data.y.lineout as number[];

        this.yxScale
            .domain([
                d3.min(yLineout) as number,
                Math.max(
                    d3.max(yLineout) as number,
                    d3.max(this.data.y.fit.fit_line as number[]) as number,
                ),
            ])
            .range([this.lineoutSize - this.lineoutPad, 0]);
        this.select('.slicops-yx-axis').call(d3.axisBottom(this.yxScale).ticks(3).tickFormat(d3.format('.1e')));

        this.xyScale
            .domain([
                d3.min(xLineout) as number,
                Math.max(
                    d3.max(xLineout) as number,
                    d3.max(this.data.x.fit.fit_line as number[]) as number,
                ),
            ])
            .range([this.lineoutSize - this.lineoutPad, 0]);
        this.select('.slicops-xy-axis').call(d3.axisLeft(this.xyScale).ticks(5).tickFormat(d3.format('.1e')));


        const xd = this.axisDomain('x');
        // offset by half pixel width
        const xoff = (xd[1] - xd[0]) / this.data.raw_pixels[0].length / 2;
        const xdata = xLineout.map((v, idx) => {
            return [
                xd[0] + (idx / this.data.raw_pixels[0].length) * (xd[1] - xd[0]),
                v,
            ];
        });
        const xdata2 = (this.data.x.fit.fit_line as number[]).map((v, idx) => {
            return [
                xd[0] + (idx / this.data.raw_pixels[0].length) * (xd[1] - xd[0]),
                v,
            ];
        });
        const xline = d3.line()
              .x((d) => this.xZoomScale(d[0] + xoff))
              .y((d) => this.xyScale(d[1]));
        this.select('.slicops-x-overlay path.slicops-x-path').datum(xdata).attr('d', xline);
        this.select('.slicops-x-overlay path.slicops-x-fit-path').datum(xdata2).attr('d', xline);

        //TODO(pjm): consolidate with x above
        const yd = this.axisDomain('y');
        const yoff = (yd[1] - yd[0]) / this.data.raw_pixels.length / 2;
        const ydata = yLineout.map((v, idx) => {
            return [
                yd[0] + (idx / this.data.raw_pixels.length) * (yd[1] - yd[0]),
                v,
            ];
        });
        const ydata2 = (this.data.y.fit.fit_line as number[]).map((v, idx) => {
            return [
                yd[0] + (idx / this.data.raw_pixels.length) * (yd[1] - yd[0]),
                v,
            ];
        });
        const yline = d3.line()
              .x((d) => this.yxScale(d[1]))
              .y((d) => this.yZoomScale(d[0] + yoff));
        this.select('.slicops-y-overlay path.slicops-y-path').datum(ydata).attr('d', yline);
        this.select('.slicops-y-overlay path.slicops-y-fit-path').datum(ydata2).attr('d', yline);

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

    select(selector?: string) : any {
        const s = d3.select(this.el.nativeElement);
        return selector ? s.select(selector) : s;
    }

}
