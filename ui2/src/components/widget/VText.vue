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
            v-model="v"
            class="form-control form-control-sm"
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
