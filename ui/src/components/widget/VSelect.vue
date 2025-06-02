<!--
   An HTML SELECT element with a list of choices.
 -->
<template>
    <VLabel
        :field="field"
        :ui_ctx="ui_ctx"
    />
    <div>
        <select
            v-model="ui_ctx[field].value"
            class="form-select form-select-sm"
            :id="field"
            @change="onChange()"
        >
            <option
                v-for="v of ui_ctx[field].choices"
                :key="v.code"
                :value="v.code">{{ v.display }}
            </option>
        </select>
    </div>
</template>

<script setup>
 import VLabel from '@/components/widget/VLabel.vue';

 const props = defineProps({
     field: String,
     ui_ctx: Object,
 });

 const onChange = () => {
     props.ui_ctx.serverAction(props.field, props.ui_ctx[props.field].value);
 };
</script>
