<!--
   A collection of cells displayed horizontally in a row.
 -->
<template>
    <div :style="'column-count:' + cells.length">
        <div v-for="cell of cells">
            <!-- TODO(robnagler) need error if not layout cell -->
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
