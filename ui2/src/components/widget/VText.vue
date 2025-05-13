<!--
   An HTML INPUT field. Submits a value when the enter key is pressed within the input field.
 -->
<template>
    <VLabel
        :field="field"
        :ui_ctx="ui_ctx"
    />
    <div>
        <input
            v-model="rawValue"
            autocomplete="off"
            class="form-control form-control-sm"
            :class="{'slicops-invalid': isInvalid}"
            :readonly="! ui_ctx[field].enabled"
            :id="field"
            @blur="onBlur()"
            @keydown="onKeydown($event)"
        />
    </div>
</template>

<script setup>
 import { ref } from 'vue';
 import VLabel from '@/components/widget/VLabel.vue';
 import { useValidation } from '@/components/widget/validation/useValidation.js'
 import { useNumberValidation } from '@/components/widget/validation/useNumberValidation.js'

 const props = defineProps({
     field: String,
     ui_ctx: Object,
 });

 const { isInvalid, parsedValue, rawValue } = ['integer', 'float'].includes(
     props.ui_ctx[props.field].widget)
     ? useNumberValidation(props.ui_ctx[props.field])
     : useValidation(props.ui_ctx[props.field]);
 rawValue.value = props.ui_ctx[props.field].value;

 const onBlur = () => {
     // Restore the ui_ctx value when focus is lost
     rawValue.value = props.ui_ctx[props.field].value;
     parsedValue.value = rawValue.value;
     isInvalid.value = false;
 };

 const onKeydown = ($event) => {
     if ($event.key == 'Enter' && ! isInvalid.value) {
         props.ui_ctx[props.field].value = parsedValue.value;
         props.ui_ctx.serverAction(props.field, parsedValue.value);
     }
 };
</script>
