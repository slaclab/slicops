<template>
  <label class="col-form-label col-form-label-sm">{{ ui_ctx[field].label }}</label>
  <div>
    <input 
      :value="formData[field]"
      class="form-control form-control-sm form-control-plaintext" 
      readonly />
  </div>
</template>

<script>
export default {
  name: 'StaticTextComponent',
  props: {
    ui_ctx: Object,
    field: String,
    parent: Object,
    formData: Object
  }
}
</script>
