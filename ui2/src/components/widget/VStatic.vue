<!--
   A component which shows a label and read-only value.
 -->
<template>
    <VLabel
        :field="field"
        :ui_ctx="ui_ctx"
    />
    <div>
        <input
            v-model="ui_ctx[field].value"
            class="form-control form-control-sm form-control-plaintext"
            :id="field"
        />
    </div>
</template>

<script setup>
 import VLabel from '@/components/widget/VLabel.vue';

 const props = defineProps({
     field: String,
     ui_ctx: Object,
 });
</script>
