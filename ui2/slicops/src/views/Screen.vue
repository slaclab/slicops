<template>
    <form>
        <div v-if="ui_ctx" class="row">
            <div v-if="errorMessage" class="alert alert-warning">{{ errorMessage }}</div>
            <Layout :layout="layout.value" :ui_ctx="ui_ctx.value"/>
        </div>
    </form>
</template>

<script setup>
 import { ref, reactive } from 'vue';
 import apiService from '@/service/api';
 import Layout from '@/components/layout.vue';

 const errorMessage = ref('');
 let image = null;
 let imageTimeout = null;
 const layout = reactive({});
 const ui_ctx = reactive({});

 const handleError = (error) => {
     errorMessage.value = error;
 };

 const serverAction = (field, value) => {
     errorMessage.value = '';
     ui_ctx.value[field].enabled = false;
     apiService.call(
         `screen_${field}`, {
             field_value: value,
         },
         (result) => {
             if (result.ui_ctx) {
                 Object.assign(ui_ctx.value, result.ui_ctx);
             }
             else {
                 ui_ctx.value[field].enabled = true;
             }
         },
         (err) => {
             handleError(err);
             ui_ctx.value[field].enabled = true;
         }
     );
 };
 
 apiService.call(
     'screen_ui_ctx',
     {},
     (result) => {
         ui_ctx.value = result.ui_ctx;
         layout.value = result.layout;
         ui_ctx.value.serverAction = serverAction;
     },
     (error) => {
         camera.value = 'Error getting camera';
     },
 );
 
</script>
