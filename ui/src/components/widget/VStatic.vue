<!--
   A component which shows a label and read-only value.
 -->
<template>
    <VLabel
        :field="field"
        :ctx="ctx"
    />
    <div>
        <input
            v-model="ctx[field].value"
            class="form-control form-control-sm form-control-plaintext"
            :id="field"
            readonly
        />
    </div>
</template>

<script setup>
 import VLabel from '@/components/widget/VLabel.vue';

 const props = defineProps({
     field: String,
     ctx: Object,
 });
</script>
