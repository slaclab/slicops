import { Component, Input, OnInit, Renderer2 } from '@angular/core';
import { FormGroup } from '@angular/forms';

/**
 * A series of layout components arranged within a bootstrap column class.
 * Attributes are:
 *  - columns: a group of column definitions:
 *    - ngClass: the col-* class
 *    - rows: a group of layout definitions
 */
@Component({
    selector: 'app-columns',
    template: `
      <div class="row">
        <div *ngFor="let col of columns" [ngClass]="'col-' + col.layout">
          <div *ngFor="let row of col.rows">
            <app-layout [layout]="row" [formGroup]="formGroup" [parent]="parent"
              [ui_ctx]="ui_ctx"></app-layout>
          </div>
        </div>
      </div>
    `,
})
export class ColumnsComponent {
    @Input() columns!: any;
    @Input() formGroup!: FormGroup;
    @Input() ui_ctx!: any;
    @Input() parent!: any;
}

/**
 * Field editor based on ui_ctx field widget.
 */
@Component({
    selector: 'app-field-editor',
    template: `
      <div [ngSwitch]="ui_ctx[name].widget">
      <div *ngSwitchCase="'select'">
        <widget-select [formGroup]="formGroup" [parent]="parent" [field]="name"
          [ui_ctx]="ui_ctx"></widget-select>
      </div>
      <div *ngSwitchCase="'text'">
        <widget-text [formGroup]="formGroup" [parent]="parent" [field]="name"
          [ui_ctx]="ui_ctx"></widget-text>
      </div>
      <div *ngSwitchCase="'static'">
        <widget-static-text [formGroup]="formGroup" [parent]="parent" [field]="name"
          [ui_ctx]="ui_ctx"></widget-static-text>
      </div>
      <div *ngSwitchCase="'button'">
        <widget-button [formGroup]="formGroup" [parent]="parent" [field]="name"
          [ui_ctx]="ui_ctx"></widget-button>
      </div>
      <div *ngSwitchCase="'heatmap_with_lineouts'">
        <div *ngIf="parent.image && parent.image.raw_pixels.length">
          <app-heatmap-with-lineouts [data]="parent.image"
            [colorMap]="formGroup.value.color_map"></app-heatmap-with-lineouts>
        </div>
      </div>
    `,
})
export class FieldEditorComponent implements OnInit{
    @Input() name!: any;
    @Input() formGroup!: FormGroup;
    @Input() ui_ctx!: any;
    @Input() parent!: any;

    ngOnInit() {
        if (! (this.name in this.ui_ctx)) {
            // display a better console error message when the app is misconfigured
            throw new Error(`Layout field ${this.name} is missing from ui_ctx (${Object.keys(this.ui_ctx)})`);
        }
    }
}

/**
 * Top level page layout. Supports three options:
 *  - name: field editor
 *  - cell: a group of field editors arranged in a horizontal row
 *  - columns: a group of columns
 */
@Component({
    selector: 'app-layout',
    template: `
      <div *ngFor="let item of layout | keyvalue">
        <div *ngIf="item.key == 'name'">
          <app-field-editor [name]="item.value" [formGroup]="formGroup" [parent]="parent"
            [ui_ctx]="ui_ctx"></app-field-editor>
        </div>
        <div *ngIf="item.key == 'cell'">
          <app-cell [fields]="item.value" [formGroup]="formGroup" [parent]="parent"
            [ui_ctx]="ui_ctx"></app-cell>
        </div>
        <div *ngIf="item.key == 'columns'">
          <app-columns [columns]="item.value" [formGroup]="formGroup" [parent]="parent"
            [ui_ctx]="ui_ctx"></app-columns>
        </div>
      </div>
    `,
})
export class LayoutComponent {
    @Input() layout!: any;
    @Input() formGroup!: FormGroup;
    @Input() ui_ctx!: any;
    @Input() parent!: any;
}

/**
 * A collection of fields displayed horizontally in a row.
 */
@Component({
    selector: 'app-cell',
    template: `
      <div [style]="'column-count:' + fields.length">
        <div *ngFor="let item of fields" style="display: inline">
          <app-field-editor [name]="item" [formGroup]="formGroup" [parent]="parent"
            [ui_ctx]="ui_ctx"></app-field-editor>
        </div>
      </div>
    `,
})
export class CellComponent {
    @Input() fields!: any;
    @Input() formGroup!: FormGroup;
    @Input() ui_ctx!: any;
    @Input() parent!: any;
}
