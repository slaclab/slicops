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
 import { ref, onMounted } from 'vue';
 import VLabel from '@/components/widget/VLabel.vue';

 const props = defineProps({
     field: String,
     ctx: Object,
 });
 const toggleElement = ref(null);

 const onChanged = () => {
     props.ctx.serverAction(props.field, props.ctx[props.field].value);
 };

 onMounted(() => {
     const l = props.ctx[props.field].ui.toggle_labels;
     toggleElement.value.bootstrapToggle({
         offlabel: l[0],
         onlabel: l[1],
     });
 });
</script>
