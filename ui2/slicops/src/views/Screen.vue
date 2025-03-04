<template>
    <div>Screen App</div>
    <div>{{ camera }}</div>
</template>

<script setup>
 import { ref } from 'vue';
 import apiService from '@/service/api';

 const camera = ref('No camera');

 apiService.call(
     'screen_ui_ctx',
     {},
     (result) => {
         console.log('got result: camera:', result.ui_ctx.camera.value);
         camera.value = result.ui_ctx.camera.value;
     },
     (error) => {
         console.log('got an error:', error);
         camera.value = 'Error getting camera';
     },
 );
 
</script>
