<!--
   Top level page layout. Supports three options:
    - cell: cell
    - cell_group: a group of cells arranged in a horizontal row
    - cols: a group of cols
 -->
<template>
    <div class="row">
        <div v-for="value in rows" :key="key">
            <div v-if="key === 'cell'">
                <VCell
                    :field="value.field"
                    :ctx="ctx"
                />
            </div>
            <div v-else-if="key === 'cell_group'">
                <VCellGroup
                    :cells="value"
                    :ctx="ctx"
                />
            </div>
            <div v-else-if="key === 'cols'">
                 <VCols
                     :columns="value"
                     :ctx="ctx"
                 />
            </div>
        </div>
    </div>
</template>

<script setup>
 import VCellGroup from '@/components/layout/VCellGroup.vue';
 import VCols from '@/components/layout/VCols.vue';
 import VCell from '@/components/layout/VCell.vue';

 const props = defineProps({
     rows: Object,
     ctx: Object,
 });
</script>
