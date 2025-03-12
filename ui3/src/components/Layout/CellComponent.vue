<template>
  <div :style="'column-count:' + fields.length">
    <div v-for="item in fields" :key="item" style="display: inline">
      <field-editor-component
        :name="item"
        :form-data="formData"
        :parent="parent"
        :ui_ctx="ui_ctx" />
    </div>
  </div>
</template>

<script>
// Import FieldEditorComponent directly as this doesn't create a circular dependency
import FieldEditorComponent from './FieldEditorComponent.vue';

export default {
  name: 'CellComponent',
  components: {
    FieldEditorComponent
  },
  props: {
    fields: Array,
    formData: Object,
    ui_ctx: Object,
    parent: Object
  }
}
</script>
