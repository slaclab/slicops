import { Component, Renderer2 } from '@angular/core';

@Component({
    selector: 'app-root',
    template: `
      <div class="container-fluid">
        <router-outlet></router-outlet>
      </div>
    `,
    styles: [],
})
export class AppComponent {
    constructor(private renderer: Renderer2) {
        // respond to system color preference changes (light vs dark)
        const p = window.matchMedia('(prefers-color-scheme: dark)');
        p.addEventListener('change', this.handleColorScheme.bind(this));
        this.handleColorScheme(p);
    }

    handleColorScheme(event: MediaQueryList | MediaQueryListEvent) {
        this.renderer.setAttribute(
            document.querySelector('html'),
            'data-bs-theme',
            event.matches ? 'dark' : 'light',
        );
    }
}
