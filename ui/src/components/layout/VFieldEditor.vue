<!--
   Field editor based on ctx field widget.
 -->
<template>
    <div
        class="mb-3"
        v-if="ctx[name].visible">
        <div v-if="ctx[name].widget == 'select'">
            <VSelect
                :field="name"
                :ctx="ctx"
            />
        </div>
        <div v-else-if="['text', 'float', 'integer'].includes(ctx[name].widget)">
            <VText
                :field="name"
                :ctx="ctx"
            />
        </div>
        <div v-else-if="ctx[name].widget == 'static'">
            <VStatic
                :field="name"
                :ctx="ctx"
            />
        </div>
        <div v-else-if="ctx[name].widget == 'button'">
            <VButton
                :field="name"
                :ctx="ctx"
            />
        </div>
        <div v-else-if="ctx[name].widget == 'heatmap_with_lineouts'">
            <VHeatmapWithLineouts
                v-if="ctx.image"
                :colorMap="ctx.color_map.value"
                :plot="ctx.image"
            />
        </div>
    </div>
</template>

<script setup>
 import VButton from '@/components/widget/VButton.vue';
 import VSelect from '@/components/widget/VSelect.vue';
 import VStatic from '@/components/widget/VStatic.vue';
 import VText from '@/components/widget/VText.vue';
 import VHeatmapWithLineouts from '@/components/plot/VHeatmapWithLineouts.vue';

 const props = defineProps({
     name: String,
     ctx: Object,
 });
</script>
