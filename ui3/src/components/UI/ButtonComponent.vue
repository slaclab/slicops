<template>
  <button 
    :disabled="!ui_ctx[field].enabled"
    :class="'btn btn-' + ui_ctx[field].html_class" 
    type="button"
    @click="onClick">
    {{ ui_ctx[field].label }}
  </button>
</template>

<script>
export default {
  name: 'ButtonComponent',
  props: {
    ui_ctx: Object,
    field: String,
    parent: Object
  },
  methods: {
    onClick() {
      this.parent.serverAction(this.field, true);
    }
  }
}
</script>
