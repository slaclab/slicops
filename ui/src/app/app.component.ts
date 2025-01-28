import { Component, Input, OnInit, Renderer2 } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';

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

/**
 * An HTML SELECT element with a list of choices.
 */
@Component({
    selector: 'widget-select',
    template: `
      <div class="mb-3" *ngIf="ui_ctx[field].visible">
        <label class="col-form-label col-form-label-sm">{{ ui_ctx[field].label }}</label>
        <div [formGroup]="formGroup">
          <select [formControlName]="field" class="form-select form-select-sm" (change)="onChange()" >
            <option *ngFor="let v of ui_ctx[field].choices" [value]="v.code">{{ v.display }}</option>
          </select>
        </div>
      </div>
    `,
    styles: [],
})
export class SelectComponent {
    @Input() formGroup!: FormGroup;
    @Input() ui_ctx!: any;
    @Input() field!: string;
    @Input() parent!: any;

    onChange() {
        this.parent.serverAction(this.field, (this.formGroup.controls as any)[this.field].value);
    }
}

/**
 * An HTML INPUT field. Submits a value when the enter key is pressed within the input field.
 */
@Component({
    selector: 'widget-text',
    template: `
      <div class="mb-3" *ngIf="ui_ctx[field].visible">
        <label class="col-form-label col-form-label-sm">{{ ui_ctx[field].label }}</label>
        <div [formGroup]="formGroup">
          <input [readonly]="! ui_ctx[field].enabled" [formControlName]="field"
            class="form-control form-control-sm" (keydown)="onKeydown($event)" (blur)="onBlur()"/>
        </div>
      </div>
    `,
    styles: [],
})
export class TextComponent implements OnInit {
    @Input() formGroup!: FormGroup;
    @Input() ui_ctx!: any;
    @Input() field!: string;
    @Input() parent!: any;

    ngOnInit() {
        const p = (this.formGroup.get(this.field) as FormControl);
        p.addValidators([Validators.required]);
        //TODO(pjm): this is hard-coded for integer input, it should be determined from ui_ctx[field].type
        p.addValidators([
            Validators.pattern(/^\-?[0-9]+$/),
        ]);
    }

    onBlur() {
        // Restore the ui_ctx value when focus is lost
        this.formGroup.patchValue({
            [this.field]: this.ui_ctx[this.field].value,
        });
    }

    onKeydown(event: KeyboardEvent) {
        if (event.key === 'Enter') {
            const c = (this.formGroup.controls as any)[this.field];
            if (c.valid) {
                this.parent.serverAction(this.field, c.value);
            }
        }
    }
}

/**
 * A component which shows a label and read-only value.
 */
@Component({
    selector: 'widget-static-text',
    template: `
      <div class="mb-3" *ngIf="ui_ctx[field].visible">
        <label class="col-form-label col-form-label-sm">{{ ui_ctx[field].label }}</label>
        <div [formGroup]="formGroup">
          <input [formControlName]="field"
            class="form-control form-control-sm form-control-plaintext" />
        </div>
      </div>
    `,
    styles: [],
})
export class StaticTextComponent {
    @Input() formGroup!: FormGroup;
    @Input() ui_ctx!: any;
    @Input() field!: string;
    @Input() parent!: any;
}

/**
 * An HTML BUTTON.
 */
@Component({
    selector: 'widget-button',
    template: `
      <div class="mb-3" *ngIf="ui_ctx[field].visible">
        <button [disabled]="! ui_ctx[field].enabled"
          [class]="'btn btn-' + ui_ctx[field].html_class" type="button"
          (click)="onClick()">{{ ui_ctx[field].label }}</button>
      </div>
    `,
    styles: [],
})
export class ButtonComponent {
    @Input() formGroup!: FormGroup;
    @Input() ui_ctx!: any;
    @Input() field!: string;
    @Input() parent!: any;

    onClick() {
        this.parent.serverAction(this.field, true);
    }
}
