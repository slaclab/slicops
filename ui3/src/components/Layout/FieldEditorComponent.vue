<template>
  <div class="mb-3" v-if="ui_ctx[name] && ui_ctx[name].visible">
    <div :class="{ 'text-danger': fieldError }">
      <component 
        :is="getComponent(ui_ctx[name].widget)"
        :ui_ctx="ui_ctx"
        :field="name"
        :form-data="formData"
        :parent="parent" />
    </div>
  </div>
</template>

<script>
import ButtonComponent from '@/components/UI/ButtonComponent.vue';
import SelectComponent from '@/components/UI/SelectComponent.vue';
import StaticTextComponent from '@/components/UI/StaticTextComponent.vue';
import TextComponent from '@/components/UI/TextComponent.vue';
import HeatmapWithLineouts from '@/components/HeatmapWithLineouts/HeatmapWithLineouts.vue';

export default {
  name: 'FieldEditorComponent',
  components: {
    ButtonComponent,
    SelectComponent,
    StaticTextComponent,
    TextComponent,
    HeatmapWithLineouts
  },
  props: {
    name: String,
    formData: Object,
    ui_ctx: Object,
    parent: Object
  },
  data() {
    return {
      fieldError: false
    }
  },
  created() {
    // Validate that field exists in ui_ctx
    if (!(this.name in this.ui_ctx)) {
      this.fieldError = true;
      console.error(`Layout field ${this.name} is missing from ui_ctx (${Object.keys(this.ui_ctx)})`);
    }
  },
  methods: {
    getComponent(widgetType) {
      const componentMap = {
        'select': 'SelectComponent',
        'text': 'TextComponent',
        'static': 'StaticTextComponent',
        'button': 'ButtonComponent',
        'heatmap_with_lineouts': 'HeatmapWithLineouts'
      };
      
      return componentMap[widgetType] || null;
    }
  }
}
</script>
