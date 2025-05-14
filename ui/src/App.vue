<template>
    <div class="container-fluid">
        <router-view></router-view>
    </div>
</template>

<script>
 // don't expose these properties to Vue
 (() => {
     const handleColorScheme = (event) => {
         document.documentElement.setAttribute('data-bs-theme', event.matches ? 'dark' : 'light');
     };
     const p = window.matchMedia('(prefers-color-scheme: dark)');
     p.addEventListener('change', handleColorScheme);
     handleColorScheme(p);
 })();
</script>
