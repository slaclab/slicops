<template>
    <div class="mb-3" v-if="ui_ctx[name].visible">
        <div v-if="ui_ctx[name].widget == 'select'">
            <Select :field="name" :ui_ctx="ui_ctx" />
        </div>
        <div v-else-if="ui_ctx[name].widget == 'text'">
            <Text :field="name" :ui_ctx="ui_ctx" />
        </div>
        <div v-else-if="ui_ctx[name].widget == 'static'">
            <Static :field="name" :ui_ctx="ui_ctx" />
        </div>
        <div v-else-if="ui_ctx[name].widget == 'button'">
            <Button :field="name" :ui_ctx="ui_ctx" />
        </div>
        <div v-else-if="ui_ctx[name].widget == 'heatmap_with_lineouts'">
            FIELD EDITOR:
            HEATMAP
        </div>
    </div>
    
</template>

<script setup>
 import Button from '@/components/widget/button.vue';
 import Select from '@/components/widget/select.vue';
 import Static from '@/components/widget/static.vue';
 import Text from '@/components/widget/text.vue';
 const props = defineProps({
     name: String,
     ui_ctx: Object,
 });
</script>
