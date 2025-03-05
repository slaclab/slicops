<!--
   Top level page layout. Supports three options:
    - name: field editor
    - cell: a group of field editors arranged in a horizontal row
    - columns: a group of columns
 -->
<template>
    <div class="row">
        <div v-for="(value, key, index) in layout" :key="index">
            <div v-if="key === 'name'">
                <VFieldEditor
                    :name="value"
                    :ui_ctx="ui_ctx"
                />
            </div>
            <div v-else-if="key === 'cell'">
                <VCell
                    :fields="value"
                    :ui_ctx="ui_ctx"
                />
            </div>
            <div v-else-if="key === 'columns'">
                 <VColumns
                     :columns="value"
                     :ui_ctx="ui_ctx"
                 />
            </div>
        </div>
    </div>
</template>

<script setup>
 import VCell from '@/components/layout/VCell.vue';
 import VColumns from '@/components/layout/VColumns.vue';
 import VFieldEditor from '@/components/layout/VFieldEditor.vue';
 const props = defineProps({
     layout: Object,
     ui_ctx: Object,
 });
</script>
