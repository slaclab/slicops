# Angular to Vue Migration Guide

This document outlines the key differences and migration considerations when moving from the original Angular application to the new Vue implementation.

## Key Architectural Changes

### Component Structure
- Angular components with decorators (`@Component`) have been converted to Vue's Single-File Components (SFC) with `<template>`, `<script>`, and `<style>` sections
- Angular's `@Input` props converted to Vue's `props` option
- Angular lifecycle methods mapped to Vue equivalents:
  - `ngOnInit` → `created`/`mounted`
  - `ngOnChanges` → Vue's `watch` properties
  - `ngOnDestroy` → `beforeUnmount`
  - `ngAfterViewInit` → `mounted`

### Services
- Angular's dependency injection services converted to Vue services as simple JavaScript modules with exported instances
- Angular's provider system replaced with direct imports

### Forms
- Angular's reactive forms system replaced with Vue's v-model binding and custom form handling
- Form validation moved from Angular's validators to custom validation methods

### Data Binding
- Angular's two-way binding with `[()]` syntax converted to Vue's `v-model` directives
- Angular's property binding with `[]` converted to Vue's `:prop` binding syntax
- Angular's event binding with `()` converted to Vue's `@event` syntax

### Templates
- Angular's structural directives (`*ngIf`, `*ngFor`) converted to Vue directives (`v-if`, `v-for`)
- Angular interpolation still uses `{{ }}` which aligns with Vue's syntax

## File Structure
```
Angular                     Vue
-------                     ---
app.component.ts       →    App.vue
screen.component.ts    →    components/ScreenComponent.vue
app.layout.ts          →    components/Layout/*.vue
heatmap components     →    components/HeatmapWithLineouts/*.vue
api.service.ts         →    services/APIService.js
log.service.ts         →    services/LogService.js
app-routing.module.ts  →    router/index.js
```

## Implementation Notes

1. **d3.js Integration**: The d3.js integration approach remains largely the same, using direct DOM manipulation in lifecycle hooks, but adapted to Vue's refs system.

2. **WebSocket Handling**: The WebSocket handling in APIService follows the same pattern but is implemented as a JavaScript module instead of an Angular service.

3. **Recursive Component Structure**: The layout system's recursive component structure has been preserved but adapted to Vue's component system.

4. **Bootstrap Integration**: Bootstrap classes and styling are maintained in the Vue implementation.

5. **Event Handling**: Angular's event binding changed to Vue's event handling system.

## Starting the Development Server

To run the Vue application:

```bash
# Install dependencies
npm install

# Start development server
npm run serve
```
