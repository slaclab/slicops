<!--
   An HTML BUTTON.
 -->
<template>
    <button
        type="button"
        :class="'btn btn-' + ctx[field].html_class"
        :disabled="! ctx[field].enabled"
        @click="onClick()"
    >{{ ctx[field].label }}</button>
</template>

<script setup>
 const props = defineProps({
     field: String,
     ctx: Object,
 });

 const onClick = () => {
     props.ctx.serverAction(props.field, props.ctx[props.field].value);
 };
</script>
