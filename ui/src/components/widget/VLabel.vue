<!--
   A form field label.
 -->
<template>
        <label
        class="col-form-label col-form-label-sm"
        :for="field"
    >
        {{ ui_ctx[field].label }}
    </label>
</template>

<script setup>
 const props = defineProps({
     field: String,
     ui_ctx: Object,
 });
</script>
