<!--
   Profile Monitor SlicLet

   Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
 http://github.com/slaclab/slicops/LICENSE
-->
<template>
    <form>
        <div
            v-if="ui_ctx"
            class="row">
            <div
                v-if="errorMessage"
                class="alert alert-warning">{{ errorMessage }}
            </div>
            <VLayout
                :layout="layout.value"
                :ui_ctx="ui_ctx.value"
            />
        </div>
    </form>
</template>

<script setup>
 import { ref, reactive } from 'vue';
 import { apiService } from '@/service/api';
 import VLayout from '@/components/VLayout.vue';

 const errorMessage = ref('');
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
             updateUIState(result);
             if (result.ui_ctx && result.ui_ctx[field] && 'enabled' in result.ui_ctx[field]) {
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

 const updateUIState = (result) => {
     if (result.plot) {
         ui_ctx.value.image = result.plot;
     }
     if (result.ui_ctx) {
         Object.assign(ui_ctx.value, result.ui_ctx);
     }
 }

 (() => {
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

     apiService.subscribe('screen_update', {}, updateUIState, handleError);
 })();
</script>
