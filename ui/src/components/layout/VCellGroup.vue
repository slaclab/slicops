<!--
   A collection of cells displayed horizontally in a row.
 -->
<template>
    <div :style="'column-count:' + cells.length">
        <div v-for="cell of cells" style="display: inline">
            <VCell
                :field="cell"
                :ctx="ctx"
            />
        </div>
    </div>
</template>

<script setup>
 import VFieldEditor from '@/components/layout/VFieldEditor.vue';

 const props = defineProps({
     cells: Object,
     ctx: Object,
 });
</script>
