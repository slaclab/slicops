<!--
   A general slicops app. Takes a "prefix" which routes to ui_api python module.
 -->
<template>
    <form>
        <div
            v-if="ctx"
            class="row">
            <div
                v-if="errorMessage"
                class="alert alert-warning">{{ errorMessage }}
            </div>
            <VRows
                :rows="ui_layout.value.rows"
                :ctx="ctx.value"
            />
        </div>
    </form>
</template>

<script setup>
 import { onUnmounted, ref, reactive, watch } from 'vue';
 import { apiService, websocketConnectedRef } from '@/services/api.js';
 import { logService } from '@/services/log.js';
 import VRows from '@/components/layout/VRows.vue';

 const props = defineProps({
     prefix: String,
 });

 const errorMessage = ref('');
 const ui_layout = reactive({});
 const ctx = reactive({});
 let apiConnection = null

 const handleError = (error) => {
     errorMessage.value = error;
 };

 const serverAction = (field, value) => {
     errorMessage.value = '';
     ctx.value[field].enabled = false;
     apiService.call(
         `ui_field_change`, {
             field: field,
             value: value,
         },
         (result) => {
//TODO(robnagler): need "voting" between two values, one from the ui and one
//    from the ctx. ctx should not be updated locally, only remotely by server
             ctx.value[field].enabled = true;
         },
         (err) => {
             handleError(err);
             ctx.value[field].enabled = true;
         }
     );
 };

 const isObject = (value) => {
     return value !== null && typeof value === 'object' && !Array.isArray(value));
 };

 const lessReactiveCtx = (ctx) => {
     for (const [k, v] of Object.entries(ctx)) {
         if ("value" in v && isObject(v.value)) {
             // pass large data items as a function accessor to avoid reactive() overhead
             const x = v.value;
             v.value = () => x;
         }
     }
     return ctx;
 };

 const uiUpdate = (result) => {
     if (! result.ctx) {
         logService.error(["no ctx ui_ctx_update result", result]);
         handleError("server returned invalid update")
         return;
     }
     if (result.ui_layout) {
         // layout is always a full update
         Object.assign(ui_layout.value, result.ui_layout);
     }
     if (! ctx.value) {
         ctx.value.serverAction = serverAction;
     }
     const c = ctx.value;
     for (const [f, r] of Object.entries(lessReactiveCtx(result.ctx))) {
         Object.assign(c[f], r);
     }
 }

 onUnmounted(() => {
     if (apiConnection) {
         apiConnection.unsubscribe();
         apiConnection = null;
     }
 });

 watch(websocketConnectedRef, () => {
     if (websocketConnectedRef.value) {
         apiConnection = apiService.subscribe(`ui_ctx_update`, {sliclet: props.prefix}, uiUpdate, handleError);
     }
 });

</script>
