<!--
 - An HTML SELECT element with a list of choices.
 -->
<template>
    <label class="col-form-label col-form-label-sm">{{ ui_ctx[field].label }}</label>
    <div>
        <select class="form-select form-select-sm" v-model="ui_ctx[field].value"
                @change="onChange()"
        >
            <option v-for="v of ui_ctx[field].choices" :value="v.code">{{ v.display }}</option>
        </select>
    </div>
</template>

<script setup>
 const props = defineProps({
     field: String,
     ui_ctx: Object,
 });

 const onChange = () => {
     props.ui_ctx.serverAction(props.field, props.ui_ctx[props.field].value);
 };
</script>
