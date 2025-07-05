<!--
   A collection of cells displayed horizontally in a row.
 -->
<template>
    <div :style="'column-count:' + cells.length">
        <div v-for="cell of cells" style="display: inline">
            <!-- TODO(robnagler) need error if not layout cell -->
            <!-- TODO(robnagler) seems like VCell should look at field -->
            <VCell
                :field="cell.field"
                :ctx="ctx"
            />
        </div>
    </div>
</template>

<script setup>
 import VCell from '@/components/layout/VCell.vue';

 const props = defineProps({
     cells: Object,
     ctx: Object,
 });
</script>
