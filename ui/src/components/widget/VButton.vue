<!--
   An HTML BUTTON.
 -->
<template>
    <button
        type="button"
        :class="'btn btn-' + ctx[field].ui.css_kind"
        :disabled="! ctx[field].ui.enabled"
        @click="onClick()"
    >{{ ctx[field].ui.label }}</button>
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
