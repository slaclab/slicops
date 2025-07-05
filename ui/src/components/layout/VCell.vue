<!--
   A collection of fields displayed horizontally in a row.
 -->
<template>
    <div :style="'column-count:' + fields.length">
        <div v-for="(item, index) of fields" :key="index" style="display: inline">
            <VFieldEditor
                :name="item"
                :ctx="ctx"
            />
        </div>
    </div>
</template>

<script setup>
 import VFieldEditor from '@/components/layout/VFieldEditor.vue';

 const props = defineProps({
     fields: Object,
     ctx: Object,
 });
</script>
