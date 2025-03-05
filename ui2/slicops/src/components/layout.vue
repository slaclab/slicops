<template>
    <div class="row">
        <div v-for="(value, key, index) in layout">
            <div v-if="key === 'name'">
                <FieldEditor :name="value" :ui_ctx="ui_ctx" />
            </div>
            <div v-else-if="key === 'cell'">
                <Cell :fields="value" :ui_ctx="ui_ctx" />
            </div>
            <div v-else-if="key === 'columns'">
                 <Columns :columns="value" :ui_ctx="ui_ctx" />
            </div>
        </div>
    </div>
</template>

<script setup>
 import Cell from '@/components/layout/cell.vue';
 import Columns from '@/components/layout/columns.vue';
 import FieldEditor from '@/components/layout/fieldeditor.vue';
 const props = defineProps({
     layout: Object,
     ui_ctx: Object,
 });
</script>
