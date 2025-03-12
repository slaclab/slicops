<template>
  <div class="row">
    <div 
      v-for="(col, index) in columns" 
      :key="index" 
      :class="'col-' + col.layout">
      <div v-for="(row, rowIndex) in col.rows" :key="rowIndex">
        <layout-component
          :layout="row"
          :form-data="formData"
          :parent="parent"
          :ui_ctx="ui_ctx" />
      </div>
    </div>
  </div>
</template>

<script>
// Use async import to break circular dependency
export default {
  name: 'ColumnsComponent',
  components: {
    'layout-component': () => import('./LayoutComponent.vue')
  },
  props: {
    columns: Array,
    formData: Object,
    ui_ctx: Object,
    parent: Object
  }
}
</script>
