<!--
   An HTML INPUT field. Submits a value when the enter key is pressed within the input field.
 -->
<template>
    <label class="col-form-label col-form-label-sm">{{ ui_ctx[field].label }}</label>
    <div>
        <input
            v-model="v"
            class="form-control form-control-sm"
            :readonly="! ui_ctx[field].enabled"
            @blur="onBlur()"
            @keydown="onKeydown($event)"
        />
    </div>
</template>

<script setup>
 import { ref } from 'vue';

 const props = defineProps({
     field: String,
     ui_ctx: Object,
 });

 const v = ref(props.ui_ctx[props.field].value);

 const onBlur = () => {
     // Restore the ui_ctx value when focus is lost
     v.value = props.ui_ctx[props.field].value;
 };

 const onKeydown = ($event) => {
     if ($event.key == 'Enter') {
         props.ui_ctx[props.field].value = v.value;
         //TODO(pjm): validate
         props.ui_ctx.serverAction(props.field, v.value);
     }
 };
</script>
