<template>
  <label class="col-form-label col-form-label-sm">{{ ui_ctx[field].label }}</label>
  <div>
    <input
      :readonly="!ui_ctx[field].enabled"
      :value="formData[field]"
      class="form-control form-control-sm"
      @keydown="onKeydown"
      @blur="onBlur"
      ref="input"
      :class="{ 'is-invalid': inputError }" />
    <div v-if="inputError" class="invalid-feedback">
      {{ inputError }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'TextComponent',
  props: {
    ui_ctx: Object,
    field: String,
    parent: Object,
    formData: Object
  },
  data() {
    return {
      inputError: null
    }
  },
  methods: {
    validate(value) {
      // Integer validation (can be extended to handle other types from ui_ctx)
      if (!/^\-?[0-9]+$/.test(value)) {
        return 'Please enter a valid integer';
      }
      return null;
    },
    
    onBlur() {
      // Restore original value on blur
      this.$refs.input.value = this.formData[field];
      this.inputError = null;
    },
    
    onKeydown(event) {
      if (event.key === 'Enter') {
        const value = event.target.value;
        const error = this.validate(value);
        
        if (!error) {
          this.inputError = null;
          this.parent.serverAction(this.field, value);
        } else {
          this.inputError = error;
        }
      }
    }
  }
}
</script>
