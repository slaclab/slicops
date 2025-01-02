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
    selector: 'app-line-chart',
    template: `
<h2>Line Chart</h2>
<figure #figure>
  <div style="position: absolute; height: 0">
    <div [ngStyle]="{'transform': 'rotate(-90deg)', 'position': 'relative', 'left': -height / 2 + 6 + 'px', 'top': height / 2 + margin.top - 10 + 'px', 'width': height + 'px'}">
      <div class="sr-y-axis-label text-center">{{ yLabel }}</div>
    </div>
  </div>
  <svg [attr.width]="width + margin.left + margin.right" [attr.height]="height + margin.top + margin.bottom">
    <g [attr.transform]="'translate(' + margin.left + ',' + margin.top + ')'">
      <g class="sr-overlay"><path></path></g>
      <g class="sr-x-axis" [attr.transform]="'translate(0,' + height + ')'"></g>
      <g class="sr-x-axis-grid" [attr.transform]="'translate(0,' + height + ')'"></g>
      <g class="sr-y-axis"></g>
      <g class="sr-y-axis-grid"></g>
    </g>
  </svg>
  <div style="position: absolute">
    <div [ngStyle]="{'position': 'relative', 'left': margin.left + 'px', 'width': width + 'px'}">
      <div class="sr-x-axis-label text-center">{{ xLabel }}</div>
    </div>
  </div>
</figure>
`,
    styles: [
        `
.sr-overlay path {
    fill: none;
    stroke: #ffab00;
    stroke-width: 3;
}
`
    ],
})
export class LineChartComponent {
    @ViewChild('figure') el!:ElementRef;
    @Input() data: number[][] = [];
    resize = new Subject<void>;
    margin = {
        left: 65,
        right: 20,
        top: 0,
        bottom: 30,
    };
    width = 0;
    height = 0;
    xScale = d3.scaleLinear();
    yScale = d3.scaleLinear();
    xLabel = "x [µm]";
    yLabel = "y [µm]";

    constructor(private cdRef: ChangeDetectorRef) {}

    select(selector?: string) : any {
        const s = d3.select(this.el.nativeElement);
        return selector ? s.select(selector) : s;
    }

    max(axisIndex: number) : any {
        return d3.max(this.data, (d: number[]) => d[axisIndex]);
    }
    
    min(axisIndex: number) : any {
        return d3.min(this.data, (d: number[]) => d[axisIndex]);
    }

    domain(axisIndex: number) : number[] {
        return [this.min(axisIndex), this.max(axisIndex)];
    }
    
    refresh() {
        const w = parseInt(this.select().style('width'));
        if (isNaN(w)) {
            return;
        }
        this.width = w - this.margin.left - this.margin.right;
        this.height = this.width * 1 / 4;
        this.xScale
            .range([0, this.width])
            .domain(this.domain(0));
        this.select('.sr-x-axis').call(d3.axisBottom(this.xScale).ticks(5));
        this.select('.sr-x-axis-grid').call(d3.axisBottom(this.xScale).ticks(5).tickSize(-this.height));
        this.yScale
            .domain(this.domain(1))
            .range([this.height, 0])
            .nice();
        this.select('.sr-y-axis').call(d3.axisLeft(this.yScale).ticks(5));
        this.select('.sr-y-axis-grid').call(d3.axisLeft(this.yScale).ticks(5).tickSize(-this.width));
        const line = d3.line()
              .x((d) => this.xScale(d[0]))
              .y((d) => this.yScale(d[1]));
        this.select('.sr-overlay path').datum(this.data).attr('d', line);
    }

    ngAfterViewInit() {
        this.resize.asObservable().pipe(debounceTime(350)).subscribe(() => this.refresh());
        this.refresh();
        // required because drawBars changes view values
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
