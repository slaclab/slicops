<!--
 -->
<template>
    <figure>
        <div
            :style="{ position: 'absolute', marginTop: margin.top + 'px', marginLeft: margin.left + 'px', zIndex: -1 }"
        >
            <VHeatmapCanvas
                v-if="canvasWidth > 1"
                :width="canvasWidth"
                :height="canvasHeight"
                :plot="props.plot"
                :zoomOffsets="zoomOffsets"
                :colorMap="props.colorMap"
            />
        </div>
        <div style="position: absolute; height: 0px">
            <div
                :style="{
                        transform: 'rotate(270deg)',
                        position: 'relative',
                        left: margin.left + canvasWidth + lineoutSize + margin.right - canvasHeight / 2 - 14 + 'px',
                        top: canvasHeight / 2 + 'px',
                        width: canvasHeight + 'px',
                        }">
                <div class="slicops-y-axis-label text-center">{{ yLabel }}</div>
            </div>
        </div>
        <svg
            :width="margin.left + canvasWidth + lineoutSize + margin.right"
            :height="margin.top + canvasHeight + lineoutSize + margin.bottom"
        >
            <g :transform="SVG.translate(margin.left, margin.top)">
                <g class="slicops-y-overlay" :transform="SVG.translate(canvasWidth + lineoutPad, 0)">
                    <defs>
                        <clipPath :id="SVG.clipPathId(lineoutSize, canvasHeight)">
                            <rect :width="lineoutSize" :height="canvasHeight"></rect>
                        </clipPath>
                    </defs>
                    <g :['clip-path']="SVG.clipPathURL(lineoutSize, canvasHeight)">
                        <path class="slicops-y-path"></path>
                        <path class="slicops-y-fit-path"></path>
                    </g>
                </g>
                <g :transform="SVG.translate(0, canvasHeight + lineoutPad)" class="slicops-x-overlay">
                    <defs>
                        <clipPath :id="SVG.clipPathId(canvasWidth, lineoutSize)">
                            <rect :width="canvasWidth" :height="lineoutSize"></rect>
                        </clipPath>
                    </defs>
                    <g :['clip-path']="SVG.clipPathURL(canvasWidth, lineoutSize)">
                        <path class="slicops-x-path"></path>
                        <path class="slicops-x-fit-path"></path>
                    </g>
                </g>
                <g class="slicops-x-axis" :transform="SVG.translate(0, canvasHeight + lineoutSize)"></g>
                <g class="slicops-x-axis-grid" :transform="SVG.translate(0, canvasHeight + lineoutSize)"></g>
                <g :transform="SVG.translate(canvasWidth + lineoutSize, 0)">
                    <g class="slicops-y-axis"></g>
                    <g class="slicops-y-axis-grid"></g>
                </g>
                <g :transform="SVG.translate(canvasWidth + lineoutPad, canvasHeight)">
                    <g class="slicops-yx-axis"></g>
                </g>
                <g :transform="SVG.translate(0, canvasHeight + lineoutPad)">
                    <g class="slicops-xy-axis"></g>
                </g>
                <rect class="slicops-mouse-rect-xy slicops-mouse-zoom" :width="canvasWidth"
                      :height="canvasHeight"></rect>
                <rect class="slicops-mouse-rect-y slicops-mouse-zoom" :x="canvasWidth" :width="lineoutSize"
                      :height="canvasHeight"></rect>
                <rect class="slicops-mouse-rect-x slicops-mouse-zoom" :y="canvasHeight"
                      :width="canvasWidth" :height="lineoutSize"></rect>
            </g>
        </svg>
        <div
            class="slicops-x-axis-label text-center"
            :style="{
                    width: canvasWidth + 'px',
                    marginLeft: margin.left + 'px',
                    }">
            {{ xLabel }}
        </div>
    </figure>
</template>

<script setup>
 import * as d3 from 'd3';
 import { onMounted, onUnmounted, ref, watch } from 'vue';
 import VHeatmapCanvas from '@/components/plot/VHeatmapCanvas.vue';

 const props = defineProps({
     plot: Function,
     colorMap: String,
 });

 class SVG {
     static clipPathId(width, height) {
         return `slicops-clippath-${width}-${height}`;
     }

     static clipPathURL(width, height) {
         return `url(#${SVG.clipPathId(width, height)})`;
     }

     static translate(x, y) {
         return `translate(${x}, ${y})`;
     }
 }

 const xScale = d3.scaleLinear();
 let xZoomScale = xScale;
 const xyScale = d3.scaleLinear();
 const xLabel = "x [mm]";
 let xZoom = null;

 const yScale = d3.scaleLinear();
 let yZoomScale = yScale;
 const yxScale = d3.scaleLinear();
 const yLabel = "y [mm]";
 let yZoom = null;
 const zoomOffsets = ref([]);

 let xyZoom = null;
 let prevXYZoom = d3.zoomIdentity;
 const canvasWidth = ref(1);
 const canvasHeight = ref(1);

 let margin = {
     left: 65,
     right: 65,
     top: 10,
     bottom: 30,
 };
 const lineoutPad = 12;
 const lineoutSize = ref(0);

 const axisDomain = (axis) => {
     //TODO(pjm): from input
     if (axis === 'x') {
         return [-4, 4];
     }
     return [0, 4];
 };

 const center = (event, target) => {
     if (event.sourceEvent) {
         const p = d3.pointers(event, target);
         return [d3.mean(p, d => d[0]), d3.mean(p, d => d[1])];
     }
     return [canvasWidth.value / 2, canvasHeight.value / 2];
 };

 const handleZoom = (event) => {
     const t = event.transform;
     const k = t.k / prevXYZoom.k;
     if (k === 1) {
         // pan
         select('.slicops-mouse-rect-x').call(
             xZoom.translateBy,
             (t.x - prevXYZoom.x) / d3.zoomTransform(select('.slicops-mouse-rect-x').node()).k,
             0,
         );
         //TODO(pjm): consolidate this with above
         select('.slicops-mouse-rect-y').call(
             yZoom.translateBy,
             0,
             (t.y - prevXYZoom.y) / d3.zoomTransform(select('.slicops-mouse-rect-y').node()).k,
         );
     }
     else {
         // zoom
         const p = center(event, select('.slicops-mouse-rect-xy').node());
         select('.slicops-mouse-rect-x').call(xZoom.scaleBy, k, p);
         select('.slicops-mouse-rect-y').call(yZoom.scaleBy, k, p);
     }
     prevXYZoom = t;
     refresh();
 };

 const handleZoomX = (t) => {
     if (t.k < 1) {
         t.k = 1;
     }
     if (t.x > 0) {
         t.x = 0;
     }
     else if (t.x < 0) {
         const r = xZoomScale.range()[1];
         if (t.k * r - r + t.x < 0) {
             t.x = -(t.k * r - r);
         }
     }
     xZoomScale = t.rescaleX(xScale);
     refresh();
 };

 const handleZoomY = (t) => {
     //TODO(pjm): consolidate with handleZoomX
     if (t.k < 1) {
         t.k = 1;
     }
     if (t.y > 0) {
         t.y = 0;
     }
     else if (t.y < 0) {
         const r = yZoomScale.range()[0];
         if (t.k * r - r + t.y < 0) {
             t.y = -(t.k * r - r);
         }
     }
     yZoomScale = t.rescaleY(yScale);
     refresh();
 };

 const refresh = () => {
     const w = parseInt(select().style('width'));
     if (isNaN(w)) {
         return;
     }
     const d = props.plot();
     const prevSize = [canvasWidth.value, canvasHeight.value];
     lineoutSize.value = Math.floor((w - (margin.left + margin.right)) / 4);
     canvasWidth.value = w - (margin.left + lineoutSize.value + margin.right);
     canvasHeight.value = Math.floor(canvasWidth.value * (d.raw_pixels.length / d.raw_pixels[0].length));
     xScale.range([0, canvasWidth.value]);
     xZoomScale.range([0, canvasWidth.value]);

     if (
         (prevSize[0] && prevSize[0] != canvasWidth.value)
         || (prevSize[1] && prevSize[1] != canvasHeight.value)
     ) {
         //TODO(pjm): see if this is update-able via a call()
         let t = d3.zoomTransform(select('.slicops-mouse-rect-x').node());
         t.x *= canvasWidth.value / prevSize[0];
         t = d3.zoomTransform(select('.slicops-mouse-rect-y').node());
         t.y *= canvasHeight.value / prevSize[1];
     }

     //TODO(pjm): could keep axis as instance variable
     select('.slicops-x-axis').call(d3.axisBottom(xZoomScale).ticks(5));
     select('.slicops-x-axis-grid').call(d3.axisBottom(xZoomScale).ticks(5).tickSize(-(canvasHeight.value + lineoutSize.value)));
     yScale.range([canvasHeight.value, 0]);
     yZoomScale.range([canvasHeight.value, 0]);
     select('.slicops-y-axis').call(d3.axisRight(yZoomScale).ticks(5));
     select('.slicops-y-axis-grid').call(d3.axisRight(yZoomScale).ticks(5).tickSize(-(canvasWidth.value + lineoutSize.value)));

     const xLineout = d.x.lineout;
     const yLineout = d.y.lineout;

     yxScale
         .domain([
             d3.min(yLineout),
             Math.max(
                 d3.max(yLineout),
                 d3.max(d.y.fit.fit_line),
             ),
         ])
         .range([lineoutSize.value - lineoutPad, 0]);
     select('.slicops-yx-axis').call(d3.axisBottom(yxScale).ticks(3).tickFormat(d3.format('.1e')));

     xyScale
         .domain([
             d3.min(xLineout),
             Math.max(
                 d3.max(xLineout),
                 d3.max(d.x.fit.fit_line),
             ),
         ])
         .range([lineoutSize.value - lineoutPad, 0]);
     select('.slicops-xy-axis').call(d3.axisLeft(xyScale).ticks(5).tickFormat(d3.format('.1e')));


     const xd = axisDomain('x');
     // offset by half pixel width
     const xoff = (xd[1] - xd[0]) / d.raw_pixels[0].length / 2;
     const xdata = xLineout.map((v, idx) => {
         return [
             xd[0] + (idx / d.raw_pixels[0].length) * (xd[1] - xd[0]),
             v,
         ];
     });
     const xdata2 = (d.x.fit.fit_line).map((v, idx) => {
         return [
             xd[0] + (idx / d.raw_pixels[0].length) * (xd[1] - xd[0]),
             v,
         ];
     });
     const xline = d3.line()
                     .x((d) => xZoomScale(d[0] + xoff))
                     .y((d) => xyScale(d[1]));
     select('.slicops-x-overlay path.slicops-x-path').datum(xdata).attr('d', xline);
     select('.slicops-x-overlay path.slicops-x-fit-path').datum(xdata2).attr('d', xline);

     //TODO(pjm): consolidate with x above
     const yd = axisDomain('y');
     const yoff = (yd[1] - yd[0]) / d.raw_pixels.length / 2;
     const ydata = yLineout.map((v, idx) => {
         return [
             yd[0] + (idx / d.raw_pixels.length) * (yd[1] - yd[0]),
             v,
         ];
     });
     const ydata2 = (d.y.fit.fit_line).map((v, idx) => {
         return [
             yd[0] + (idx / d.raw_pixels.length) * (yd[1] - yd[0]),
             v,
         ];
     });
     const yline = d3.line()
                     .x((d) => yxScale(d[1]))
                     .y((d) => yZoomScale(d[0] + yoff));
     select('.slicops-y-overlay path.slicops-y-path').datum(ydata).attr('d', yline);
     select('.slicops-y-overlay path.slicops-y-fit-path').datum(ydata2).attr('d', yline);

     const xZoomDomain = xZoomScale.domain();
     const xDomain = xScale.domain();
     const yZoomDomain = yZoomScale.domain();
     const yDomain = yScale.domain();
     const zoomWidth = xZoomDomain[1] - xZoomDomain[0];
     const zoomHeight = yZoomDomain[1] - yZoomDomain[0];
     zoomOffsets.value = [
            -(xZoomDomain[0] - xDomain[0]) / zoomWidth * canvasWidth.value,
            -(yDomain[1] - yZoomDomain[1]) / zoomHeight * canvasHeight.value,
         (xDomain[1] - xDomain[0]) / zoomWidth * canvasWidth.value,
         (yDomain[1] - yDomain[0]) / zoomHeight * canvasHeight.value,
     ];
 };

 const select = (selector) => {
     //TODO(pjm): need unique id
     const s = d3.select('figure');
     return selector ? s.select(selector) : s;
 };

 onMounted(() => {
     //TODO(pjm): debounce refresh call if needed
     window.addEventListener('resize', refresh);
     xZoom = d3.zoom().on('zoom', (event) => { handleZoomX(event.transform) });
     select('.slicops-mouse-rect-x').call(xZoom);
     yZoom = d3.zoom().on('zoom', (event) => { handleZoomY(event.transform) });
     select('.slicops-mouse-rect-y').call(yZoom);
     xyZoom = d3.zoom().on('zoom', (event) => { handleZoom(event) });
     select('.slicops-mouse-rect-xy').call(xyZoom);

     xScale.domain(axisDomain('x'));
     yScale.domain(axisDomain('y'));

     refresh();
 });

 onUnmounted(() => {
     window.removeEventListener('resize', refresh);
     for (const z of [xZoom, yZoom, xyZoom]) {
         z.on('zoom', null);
     }
 });

 watch(() => props.plot, refresh, {
     flush: true,
 });

</script>

<style scoped>
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
</style>
