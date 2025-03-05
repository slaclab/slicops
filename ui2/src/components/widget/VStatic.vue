<!--
   A component which shows a label and read-only value.
 -->
<template>
    <label class="col-form-label col-form-label-sm">{{ ui_ctx[field].label }}</label>
    <div>
        <input
            v-model="ui_ctx[field].value"
            class="form-control form-control-sm form-control-plaintext"
        />
    </div>
</template>

<script setup>
 const props = defineProps({
     field: String,
     ui_ctx: Object,
 });
</script>
