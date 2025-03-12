<template>
  <div class="container-fluid">
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App',
  mounted() {
    // Respond to system color preference changes (light vs dark)
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    prefersDarkScheme.addEventListener('change', this.handleColorScheme);
    this.handleColorScheme(prefersDarkScheme);
  },
  methods: {
    handleColorScheme(event) {
      document.querySelector('html').setAttribute(
        'data-bs-theme',
        event.matches ? 'dark' : 'light'
      );
    }
  },
  beforeUnmount() {
    // Clean up event listener
    window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', this.handleColorScheme);
  }
}
</script>
