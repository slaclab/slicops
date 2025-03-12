<template>
  <label class="col-form-label col-form-label-sm">{{ ui_ctx[field].label }}</label>
  <div>
    <select 
      class="form-select form-select-sm" 
      :value="formData[field]"
      @change="onChange($event)">
      <option 
        v-for="v in ui_ctx[field].choices" 
        :key="v.code" 
        :value="v.code">
        {{ v.display }}
      </option>
    </select>
  </div>
</template>

<script>
export default {
  name: 'SelectComponent',
  props: {
    ui_ctx: Object,
    field: String,
    parent: Object,
    formData: Object
  },
  methods: {
    onChange(event) {
      this.parent.serverAction(this.field, event.target.value);
    }
  }
}
</script>
