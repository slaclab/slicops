<!--
   A general slicops app. Takes a "prefix" which routes to ui_api python module.
 -->
<template>
    <form>
        <div
            v-if="ctx.value"
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
 import { useRoute, useRouter } from 'vue-router';
 import { apiService, websocketConnectedRef } from '@/services/api.js';
 import { logService } from '@/services/log.js';
 import VRows from '@/components/layout/VRows.vue';

 const props = defineProps({
     sliclet: String,
 });

 const router = useRouter();
 const route = useRoute();
 const errorMessage = ref('');
 const ui_layout = reactive({});
 const ctx = reactive({});
 let apiConnection = null

 const handleError = (error) => {
     errorMessage.value = error;
 };

 const serverAction = (field, value) => {
     errorMessage.value = '';
     //TODO(robnagler): need "voting" between two values, one from the ui and one
     //    from the ctx. ctx should not be updated locally, only remotely by server
     // ctx.value[field].ui.enabled = false;
     apiService.call(
         'ui_ctx_write',
         {
             field_values: {
                 [field]: value,
                 //TODO(nagler) could send enabled = false
                 // and then then button would turn itself back on once it hits the server
             },
         },
         (result) => {
             return;
         },
         (err) => {
             handleError(err);
         }
     );
 };

 const isObject = (value) => {
     return value !== null && typeof value === 'object' && !Array.isArray(value);
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
     if (! result.fields) {
         logService.error(["no fields ui_ctx_update result", result]);
         handleError("server returned invalid update")
         return;
     }
     if (result.ui_layout) {
         // layout is always a full update
         ui_layout.value = result.ui_layout;
     }
     if (result.sliclet_name) {
         document.title = result.sliclet_title;
         if (! props.sliclet) {
             const u = '/' + result.sliclet_name;
             if (route.path !== u) {
                 // avoid a possible redirect loop
                 router.replace(u);
             }
         }
     }
     result.fields = lessReactiveCtx(result.fields)
     if (! ctx.value) {
         ctx.value = result.fields;
         ctx.value.serverAction = serverAction;
         return;
     }
     const c = ctx.value;
     for (const [f, r] of Object.entries(result.fields)) {
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
         apiConnection = apiService.subscribe(`ui_ctx_update`, {sliclet:  props.sliclet}, uiUpdate, handleError);
     }
 });

</script>
