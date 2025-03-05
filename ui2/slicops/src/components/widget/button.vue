<!--
 - An HTML BUTTON.
 -->
<template>
    <button type="button" :disabled="! ui_ctx[field].enabled"
            :class="'btn btn-' + ui_ctx[field].html_class" 
            @click="onClick()"
    >{{ ui_ctx[field].label }}</button>
</template>

<script setup>
 const props = defineProps({
     field: String,
     ui_ctx: Object,
 });

 const onClick = () => {
     props.ui_ctx.serverAction(props.field, props.ui_ctx[props.field].value);
 };
</script>
