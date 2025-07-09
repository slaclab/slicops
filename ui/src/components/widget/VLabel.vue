<!--
   A form field label.
 -->
<template>
        <label
        class="col-form-label col-form-label-sm"
        :for="field"
    >
        {{ ctx[field].ui.label }}
    </label>
</template>

<script setup>
 const props = defineProps({
     field: String,
     ctx: Object,
 });
</script>
