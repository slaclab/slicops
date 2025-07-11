<!--
   An HTML checkbox that renders as a bootstrap toggle.
 -->
<template>
    <VLabel
        :field="field"
        :ctx="ctx"
    />
    <div>
        <input
            type="checkbox"
            data-toggle="toggle"
            data-onstyle="secondary"
            v-model="ctx[field].value"
            v-on:change="onChanged"
            ref="toggleElement"
        />
    </div>
</template>

<script setup>
 import { onBeforeUnmount, onMounted, ref, watch } from 'vue';
 import VLabel from '@/components/widget/VLabel.vue';

 const props = defineProps({
     field: String,
     ctx: Object,
 });
 const toggleElement = ref(null);

 const onChanged = () => {
     props.ctx.serverAction(props.field, props.ctx[props.field].value);
 };

 onBeforeUnmount(() => {
     toggleElement.value.bootstrapToggle('destroy');
 });

 onMounted(() => {
     const l = props.ctx[props.field].ui.toggle_labels;
     toggleElement.value.bootstrapToggle({
         offlabel: l[0],
         onlabel: l[1],
     });
 });

 watch(() => props.ctx[props.field].value, () => {
     // work-around for missing render on revert changes
     toggleElement.value.bootstrapToggle(
         props.ctx[props.field].value ? 'on' : 'off');
 });
</script>
