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
     const findChoice = (value) => {
         const c = props.ctx[props.field].constraints.choices;
         for (const k in c) {
             if (c[k] === value) {
                 return k;
             }
         }
         throw new Error(`Missing value: ${value} in Boolean choices for field: ${props.field}`);
     };
     toggleElement.value.bootstrapToggle({
         onlabel: findChoice(true),
         offlabel: findChoice(false),
     });
 });
</script>
