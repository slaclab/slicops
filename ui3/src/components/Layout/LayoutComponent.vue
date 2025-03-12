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
import FieldEditorComponent from './FieldEditorComponent.vue';
import CellComponent from './CellComponent.vue';
import ColumnsComponent from './ColumnsComponent.vue';

export default {
  name: 'LayoutComponent',
  components: {
    FieldEditorComponent,
    CellComponent,
    ColumnsComponent
  },
  props: {
    layout: Object,
    formData: Object,
    ui_ctx: Object,
    parent: Object
  }
}
</script>
