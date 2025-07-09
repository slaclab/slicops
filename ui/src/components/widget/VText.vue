<!--
   An HTML INPUT field. Submits a value when the enter key is pressed within the input field.
 -->
<template>
    <VLabel
        :field="field"
        :ctx="ctx"
    />
    <div>
        <input
            v-model="rawValue"
            autocomplete="off"
            class="form-control form-control-sm"
            :class="{'slicops-invalid': isInvalid}"
            :readonly="! ctx[field].ui.enabled"
            :id="field"
            @blur="onBlur()"
            @keydown="onKeydown($event)"
        />
    </div>
</template>

<script setup>
 import { ref, watch } from 'vue';
 import VLabel from '@/components/widget/VLabel.vue';
 import { useValidation } from '@/components/widget/validation/useValidation.js'
 import { useNumberValidation } from '@/components/widget/validation/useNumberValidation.js'

 const props = defineProps({
     field: String,
     ctx: Object,
 });

 const { isInvalid, parsedValue, rawValue } = ['integer', 'float'].includes(
     props.ctx[props.field].ui.widget)
     ? useNumberValidation(props.ctx[props.field])
     : useValidation(props.ctx[props.field]);
 rawValue.value = props.ctx[props.field].value;

 const onBlur = () => {
     // Restore the ctx value when focus is lost
     rawValue.value = props.ctx[props.field].value;
     parsedValue.value = rawValue.value;
     isInvalid.value = false;
 };

 const onKeydown = ($event) => {
     if ($event.key == 'Enter' && ! isInvalid.value) {
         props.ctx[props.field].value = parsedValue.value;
         props.ctx.serverAction(props.field, parsedValue.value);
     }
 };

 watch(() => props.ctx[props.field].value, () => {
     if (props.ctx[props.field].value !== parsedValue.value) {
         rawValue.value = props.ctx[props.field].value;
     }
 });

</script>
