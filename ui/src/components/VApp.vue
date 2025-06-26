<!--
   A general slicops app. Takes a "prefix" which routes to ui_api python module.
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
 import { onUnmounted, ref, reactive, watch } from 'vue';
 import { apiService, websocketConnectedRef } from '@/services/api.js';
 import VLayout from '@/components/VLayout.vue';

 const props = defineProps({
     prefix: String,
 });

 const errorMessage = ref('');
 const layout = reactive({});
 const ui_ctx = reactive({});
 let apiConnection = null

 const handleError = (error) => {
     errorMessage.value = error;
 };

 const serverAction = (field, value) => {
     errorMessage.value = '';
     ui_ctx.value[field].enabled = false;
     apiService.call(
         `ui_action`, {
             field: field,
             value: value,
         },
         (result) => {
             //TODO(robnagler): sliclet will enable button when?
             ui_ctx.value[field].enabled = true;
         },
         (err) => {
             handleError(err);
             ui_ctx.value[field].enabled = true;
         }
     );
 };

 const updateUIState = (result) => {
     if (result.plot) {
         // pass large data items as a function accessor to avoid reactive() overhead
         ui_ctx.value.image = () => result.plot;
     }
     if (result.ui_ctx) {
         Object.assign(ui_ctx.value, result.ui_ctx);
     }
 }

 apiService.call(
     `ui_boot`,
     {sliclet: props.prefix},
     (result) => {
         ui_ctx.value = result.ui_ctx;
         layout.value = result.layout;
         ui_ctx.value.serverAction = serverAction;
     },
     handleError,
 );

 onUnmounted(() => {
     if (apiConnection) {
         apiConnection.unsubscribe();
         apiConnection = null;
     }
 });

 watch(websocketConnectedRef, () => {
     if (websocketConnectedRef.value) {
         apiConnection = apiService.subscribe(`ui_update`, {}, updateUIState, handleError);
     }
 });

</script>
