<!--
   A component which shows a label and read-only value.
 -->
<template>
    <VLabel
        :field="field"
        :ctx="ctx"
    />
    <div>
        <div class="form-control form-control-sm form-control-plaintext">
            {{ ctx[field].value }}
        </div>
    </div>
</template>

<script setup>
 import VLabel from '@/components/widget/VLabel.vue';

 const props = defineProps({
     field: String,
     ctx: Object,
 });
</script>
