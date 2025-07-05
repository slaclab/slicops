<!--
   A series of layout components arranged within a bootstrap column class.
   Attributes are:
     - cols: a group of column definitions:
       - css: the col-* class
       - rows: a group of layout definitions
 -->
<template>
    <div class="row">
        <div
            v-for="col of cols"
            :class="col.css">
            <!-- TODO(robnagler) need error if layout not col(?) -->
<!--            <div
                v-for="(row, index2) of col.rows"
                :key="index2">  -->
                <VRows
                    :rows="col.rows"
                    :ctx="ctx"
                />
<!--            </div> -->
        </div>
    </div>
</template>

<script setup>
 import VLayout from '@/components/VLayout.vue';

 const props = defineProps({
     cols: Object,
     ctx: Object,
 });
</script>
