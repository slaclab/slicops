<template>
  <form v-if="ui_ctx">
    <div class="row">
      <div v-if="errorMessage" class="alert alert-warning">{{ errorMessage }}</div>
      <layout-component 
        :layout="layout" 
        :form-data="formData" 
        :parent="this"
        :ui_ctx="ui_ctx" />
    </div>
  </form>
</template>

<script>
// Profile Monitor SlicLet
//
// Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
// http://github.com/slaclab/slicops/LICENSE

import APIService from '@/services/APIService';
import LogService from '@/services/LogService';
import LayoutComponent from '@/components/Layout/LayoutComponent.vue';

export default {
  name: 'ScreenComponent',
  components: {
    LayoutComponent
  },
  data() {
    return {
      errorMessage: '',
      image: null,
      imageTimeout: null,
      layout: null,
      formData: {},
      ui_ctx: null
    };
  },
  created() {
    APIService.call(
      'screen_ui_ctx',
      {},
      (result) => {
        this.ui_ctx = result.ui_ctx;
        this.layout = result.layout;
        const formValues = {};
        for (let field in result.ui_ctx) {
          formValues[field] = result.ui_ctx[field].value;
        }
        this.formData = formValues;
      },
      this.handleError
    );
    
    APIService.subscribe(
      'screen_update',
      {},
      (result) => this.updateUIState(result),
      this.handleError
    );
  },
  methods: {
    handleError(err) {
      LogService.error(['apiService error', err]);
      this.errorMessage = err;
    },
    
    serverAction(field, value) {
      this.errorMessage = '';
      this.ui_ctx[field].enabled = false;
      
      APIService.call(
        `screen_${field}`,
        {
          field_value: value,
        },
        (result) => {
          if (result.ui_ctx && field in result.ui_ctx && 'enabled' in result.ui_ctx[field]) {
            // Do nothing, the server has set enabled
          } else {
            this.ui_ctx[field].enabled = true;
          }
          this.updateUIState(result);
        },
        (err) => {
          this.handleError(err);
          this.ui_ctx[field].enabled = true;
        }
      );
    },
    
    updateUIState(result) {
      if (result.plot) {
        this.image = result.plot;
      }
      
      if (result.ui_ctx) {
        Object.assign(this.ui_ctx, result.ui_ctx);
        const values = {};
        
        for (let field in result.ui_ctx) {
          if ('value' in result.ui_ctx[field]) {
            values[field] = result.ui_ctx[field].value;
          }
        }
        
        // Update form values
        this.formData = { ...this.formData, ...values };
      }
    }
  },
  beforeUnmount() {
    // Cleanup any possible subscriptions
    if (this.imageTimeout) {
      clearTimeout(this.imageTimeout);
    }
  }
}
</script>
