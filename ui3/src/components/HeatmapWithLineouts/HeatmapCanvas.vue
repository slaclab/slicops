<template>
  <canvas ref="canvas"></canvas>
</template>

<script>
import * as d3 from 'd3';

export default {
  name: 'HeatmapCanvas',
  props: {
    width: {
      type: Number,
      default: 0
    },
    height: {
      type: Number,
      default: 0
    },
    intensity: {
      type: Array,
      default: () => []
    },
    zoomOffsets: {
      type: Array,
      default: () => []
    },
    colorMap: {
      type: String,
      default: "Viridis"
    }
  },
  data() {
    return {
      ctx: null,
      cacheCanvas: null,
      colorScale: null,
      previousValues: {}
    };
  },
  mounted() {
    this.colorScale = d3.scaleSequential(d3["interpolate" + this.colorMap]);
    this.ctx = this.$refs.canvas.getContext('2d', { willReadFrequently: true });
    this.cacheCanvas = document.createElement('canvas');
    this.initImage();
  },
  methods: {
    initImage() {
      this.cacheCanvas.width = this.intensity[0].length;
      this.cacheCanvas.height = this.intensity.length;
      this.colorScale.domain([this.min(), this.max()]);
      const imageData = this.ctx.getImageData(0, 0, this.cacheCanvas.width, this.cacheCanvas.height);
      const xSize = this.intensity[0].length;
      const ySize = this.intensity.length;
      
      for (let yi = 0, p = -1; yi < ySize; ++yi) {
        for (let xi = 0; xi < xSize; ++xi) {
          const c = d3.rgb(this.colorScale(this.intensity[yi][xi]));
          imageData.data[++p] = c.r;
          imageData.data[++p] = c.g;
          imageData.data[++p] = c.b;
          imageData.data[++p] = 255;
        }
      }
      
      this.cacheCanvas.getContext('2d').putImageData(imageData, 0, 0);
      this.previousValues.intensity = this.intensity;
      this.previousValues.colorMap = this.colorMap;
    },
    
    max() {
      return d3.max(this.intensity, (row) => {
        return d3.max(row);
      });
    },
    
    min() {
      return d3.min(this.intensity, (row) => {
        return d3.min(row);
      });
    },
    
    refresh() {
      this.$refs.canvas.width = this.width;
      this.$refs.canvas.height = this.height;
      this.ctx.imageSmoothingEnabled = false;
      this.ctx.drawImage(this.cacheCanvas, ...this.zoomOffsets);
    }
  },
  watch: {
    intensity: {
      handler(newVal, oldVal) {
        if (this.cacheCanvas && 
            (this.previousValues.intensity !== newVal || 
             this.previousValues.colorMap !== this.colorMap)) {
          this.colorScale = d3.scaleSequential(d3["interpolate" + this.colorMap]);
          this.initImage();
        }
        this.refresh();
      },
      deep: true
    },
    colorMap() {
      if (this.cacheCanvas && this.previousValues.colorMap !== this.colorMap) {
        this.colorScale = d3.scaleSequential(d3["interpolate" + this.colorMap]);
        this.initImage();
        this.refresh();
      }
    },
    width() {
      this.refresh();
    },
    height() {
      this.refresh();
    },
    zoomOffsets: {
      handler() {
        this.refresh();
      },
      deep: true
    }
  }
}
</script>
