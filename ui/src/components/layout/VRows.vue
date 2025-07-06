<!--
   Top level page layout. Supports three options:
    - cell: cell
    - cell_group: a group of cells arranged in a horizontal row
    - cols: a group of cols
 -->
<template>
    <div class="row">
        <div v-for="r in rows">
            <div v-if="r.layout === 'cell'">
                <VCell
                    :field="r.field"
                    :ctx="ctx"
                />
            </div>
            <div v-else-if="r.layout === 'cell_group'">
                <VCellGroup
                    :cells="r.cells"
                    :ctx="ctx"
                />
            </div>
            <div v-else-if="r.layout === 'cols'">
                 <VCols
                     :cols="r.cols"
                     :ctx="ctx"
                 />
            </div>
            <!-- TODO(robnagler) need error -->
        </div>
    </div>
</template>

<script setup>
 import VCell from '@/components/layout/VCell.vue';
 import VCellGroup from '@/components/layout/VCellGroup.vue';
 import VCols from '@/components/layout/VCols.vue';

 const props = defineProps({
     rows: Object,
     ctx: Object,
 });
</script>
