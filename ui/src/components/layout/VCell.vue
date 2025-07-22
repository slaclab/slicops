<!--
   Field editor based on ctx field widget.
 -->
<template>
    <div
        class="mb-3"
        v-if="ctx[field].ui.visible"
    >
        <div v-if="ctx[field].ui.widget == 'select'">
            <VSelect
                :field="field"
                :ctx="ctx"
            />
        </div>
        <div v-else-if="ctx[field].ui.widget == 'toggle'">
            <VToggle
                :field="field"
                :ctx="ctx"
            />
        </div>
        <div v-else-if="['text', 'float', 'integer'].includes(ctx[field].ui.widget)">
            <VText
                :field="field"
                :ctx="ctx"
            />
        </div>
        <div v-else-if="ctx[field].ui.widget == 'static'">
            <VStatic
                :field="field"
                :ctx="ctx"
            />
        </div>
        <div v-else-if="ctx[field].ui.widget == 'button'">
            <VButton
                :field="field"
                :ctx="ctx"
            />
        </div>
        <div v-else-if="ctx[field].ui.widget == 'heatmap_with_lineouts'">
            <VHeatmapWithLineouts
                :colorMap="ctx['color_map'].value"
                :plot="ctx[field].value"
            />
        </div>
        <div v-else-if="ctx[field].ui.widget == 'heatmap'">
            <VHeatmap
                :colorMap="ctx['color_map'].value"
                :plot="ctx[field].value"
            />
        </div>
        <div v-else>
            Unhandled widget: {{ ctx[field].ui.widget }}
        </div>
    </div>
</template>

<script setup>
 import VButton from '@/components/widget/VButton.vue';
 import VHeatmap from '@/components/plot/VHeatmap.vue';
 import VHeatmapWithLineouts from '@/components/plot/VHeatmapWithLineouts.vue';
 import VSelect from '@/components/widget/VSelect.vue';
 import VStatic from '@/components/widget/VStatic.vue';
 import VText from '@/components/widget/VText.vue';
 import VToggle from '@/components/widget/VToggle.vue';

 const props = defineProps({
     field: String,
     ctx: Object,
 });
</script>
