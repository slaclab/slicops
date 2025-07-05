<!--
   An HTML SELECT element with a list of choices.
 -->
<template>
    <VLabel
        :field="field"
        :ctx="ctx"
    />
    <div>
        <select
            v-model="ctx[field].value"
            class="form-select form-select-sm"
            :id="field"
            @change="onChange()"
        >
            <option
                v-for="(value, label) of ctx[field].ui.choices"
                :key="value"
                :value="value">{{ label }}
            </option>
        </select>
    </div>
</template>

<script setup>
 import VLabel from '@/components/widget/VLabel.vue';

 const props = defineProps({
     field: String,
     ctx: Object,
 });

 const onChange = () => {
     props.ctx.serverAction(props.field, props.ctx[props.field].value);
 };
</script>
