<template>
  <div v-for="(value, key) in layout" :key="key">
    <div v-if="key === 'name'">
      <field-editor-component 
        :name="value" 
        :form-data="formData" 
        :parent="parent"
        :ui_ctx="ui_ctx" />
    </div>
    <div v-else-if="key === 'cell'">
      <cell-component 
        :fields="value" 
        :form-data="formData" 
        :parent="parent"
        :ui_ctx="ui_ctx" />
    </div>
    <div v-else-if="key === 'columns'">
      <columns-component 
        :columns="value" 
        :form-data="formData" 
        :parent="parent"
        :ui_ctx="ui_ctx" />
    </div>
  </div>
</template>

<script>
// Breaking the circular dependency by using component registration instead of imports
export default {
  name: 'LayoutComponent',
  components: {
    'field-editor-component': () => import('./FieldEditorComponent.vue'),
    'cell-component': () => import('./CellComponent.vue'),
    'columns-component': () => import('./ColumnsComponent.vue')
  },
  props: {
    layout: Object,
    formData: Object,
    ui_ctx: Object,
    parent: Object
  }
}
</script>
