<template>
    <div :style="'column-count:' + fields.length">
        <div v-for="item of fields" style="display: inline">
            <FieldEditor :name="item" :ui_ctx="ui_ctx" />
        </div>
    </div>
</template>

<script setup>
 import FieldEditor from '@/components/layout/fieldeditor.vue';
 const props = defineProps({
     fields: Object,
     ui_ctx: Object,
 });
</script>
