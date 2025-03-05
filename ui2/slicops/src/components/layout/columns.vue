<template>
    <div class="row">
        <div v-for="col of columns" :class="'col-' + col.layout">
            <div v-for="row of col.rows">
                <Layout :layout="row" :ui_ctx="ui_ctx" />
            </div>
        </div>
    </div>
</template>

<script setup>
 import Layout from '@/components/layout.vue';
 const props = defineProps({
     columns: Object,
     ui_ctx: Object,
 });
</script>
