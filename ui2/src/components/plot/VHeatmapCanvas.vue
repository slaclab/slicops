<!--
   The HTML CANVAS part of a heatmap.
 -->
<template>
    <canvas></canvas>
</template>

<script setup>
 import * as d3 from 'd3';
 import { onMounted, watch } from 'vue';

 const props = defineProps({
     width: Number,
     height: Number,
     intensity: Object,
     zoomOffsets: Object,
     colorMap: String,
 });

 let ctx = null;
 let cacheCanvas = null;
 let colorScale = null;
 let previousValues = {};

 const initImage = () => {
     cacheCanvas.width = props.intensity[0].length;
     cacheCanvas.height = props.intensity.length;
     colorScale.domain([min(), max()]);
     const imageData = ctx.getImageData(0, 0, cacheCanvas.width, cacheCanvas.height);
     const xSize = props.intensity[0].length;
     const ySize = props.intensity.length;
     for (let yi = 0, p = -1; yi < ySize; ++yi) {
         for (let xi = 0; xi < xSize; ++xi) {
             const c = d3.rgb(colorScale(props.intensity[yi][xi]));
             imageData.data[++p] = c.r;
             imageData.data[++p] = c.g;
             imageData.data[++p] = c.b;
             imageData.data[++p] = 255;
         }
     }
     cacheCanvas.getContext('2d').putImageData(imageData, 0, 0);
     previousValues.intensity = props.intensity;
     previousValues.colorMap = props.colorMap;
 };

 const max = () => d3.max(props.intensity, (row) => d3.max(row));

 const min = () => d3.min(props.intensity, (row) => d3.min(row));

 const refresh = () => {
     const c = d3.select('canvas').node();
     c.width = props.width;
     c.height = props.height;
     ctx.imageSmoothingEnabled = false;
     ctx.drawImage(cacheCanvas, ...props.zoomOffsets);
 };

 onMounted(() => {
     colorScale = d3.scaleSequential(d3["interpolate" + props.colorMap]);
     ctx = d3.select('canvas').node().getContext('2d', { willReadFrequently: true });
     cacheCanvas = document.createElement('canvas');
     initImage();
     refresh();
 });

 watch(props, () => {
     if (cacheCanvas) {
         if (
             previousValues.intensity != props.intensity
             || previousValues.colorMap != props.colorMap
         ) {
             colorScale = d3.scaleSequential(d3["interpolate" + props.colorMap]);
             initImage();
         }
         refresh();
     }
 });
</script>
